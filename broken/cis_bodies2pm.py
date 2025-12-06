from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any


# --------------------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------------------


@dataclass
class BodyMeshInfo:
    """Intermediate representation of a single body mesh.

    This is used by build_bodies_from_blender() to hold the recentered
    vertices and topology information before rings are built.
    """
    name: str
    vertices: List[Tuple[float, float, float]]          # (x, y, z) in PM space (meters, nose at z=0)
    faces: List[Tuple[int, int, int, int]]              # quads (v0, v1, v2, v3)
    span: float                                         # total length along longitudinal axis (meters)
    offset: float                                       # nose offset used when re-centering (meters)
    is_symmetric: bool                                  # mesh symmetric around x=0 or not
    debug_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BodyStation:
    """Topological 'station' grouping for vertices at similar z."""
    z_ft: float
    ring_indices: List[int]                   # vertex indices for the station ring
    is_tip: bool = False
    is_tail: bool = False
    debug_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BodyPMRing:
    """Plane-Maker ring (one cross-section station)."""
    j_index: int
    z_ft: float
    verts_ordered: List[Tuple[float, float, float]]     # (x_m, y_m, z_m) in meters
    is_tip: bool = False
    is_tail: bool = False
    debug_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BodyPMDefinition:
    """High-level PM body definition used by the adapter."""
    body_index: int
    mesh_name: str
    rings: List[BodyPMRing]
    offset: float                                       # meters
    span: float                                         # meters
    is_symmetric: bool
    debug_info: Dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------------------------


def ft_from_meters(m: float) -> float:
    return m * 3.280839895013123


def round_ft(val: float, ndigits: int = 9) -> float:
    """Round a float to 'ndigits' decimal places (Plane-Maker style)."""
    return float(f"{val:.{ndigits}f}")


# --------------------------------------------------------------------------------------
# Core body building logic (shared by OBJ and Blender paths)
# --------------------------------------------------------------------------------------


def recenter_body_along_longitudinal_axis(
    verts: List[Tuple[float, float, float]]
) -> Tuple[List[Tuple[float, float, float]], float, float]:
    """Recenter vertices along longitudinal axis (z) so nose is at z=0."""
    if not verts:
        return verts, 0.0, 0.0

    z_coords = [v[2] for v in verts]
    min_z = min(z_coords)
    max_z = max(z_coords)
    span = max_z - min_z

    offset = min_z
    recentered = [(x, y, z - offset) for (x, y, z) in verts]

    return recentered, offset, span


def detect_symmetry_x(verts: List[Tuple[float, float, float]], tol: float = 1e-6) -> bool:
    """Rough check for symmetry around x=0."""
    if not verts:
        return False

    buckets: Dict[Tuple[float, float], List[float]] = {}
    for x, y, z in verts:
        key = (round(y, 6), round(z, 6))
        buckets.setdefault(key, []).append(x)

    for xs in buckets.values():
        xs_sorted = sorted(xs)
        n = len(xs_sorted)
        for i in range(n // 2):
            left = xs_sorted[i]
            right = xs_sorted[-(i + 1)]
            if abs(left + right) > tol:
                return False

    return True


def build_body_mesh_info_from_group(
    group_name: str,
    group_data: Dict[str, Any],
) -> BodyMeshInfo:
    """Build a BodyMeshInfo from raw mesh data (verts, faces)."""
    original_verts = group_data["verts"]
    faces = group_data["faces"]

    recentered, offset, span = recenter_body_along_longitudinal_axis(original_verts)
    symmetric = detect_symmetry_x(recentered)

    debug_info = {
        "original_verts_count": len(original_verts),
        "faces_count": len(faces),
        "offset": offset,
        "span": span,
        "symmetric_x": symmetric,
    }

    return BodyMeshInfo(
        name=group_name,
        vertices=recentered,
        faces=faces,
        span=span,
        offset=offset,
        is_symmetric=symmetric,
        debug_info=debug_info,
    )


def build_vertex_adjacency(
    faces: List[Tuple[int, int, int, int]]
) -> Dict[int, List[int]]:
    """Build adjacency list for vertices based on quad faces."""
    adjacency: Dict[int, List[int]] = {}
    for f in faces:
        v0, v1, v2, v3 = f
        quad_edges = [
            (v0, v1),
            (v1, v2),
            (v2, v3),
            (v3, v0),
        ]
        for a, b in quad_edges:
            adjacency.setdefault(a, []).append(b)
            adjacency.setdefault(b, []).append(a)
    return adjacency


def compute_topological_layers(
    verts: List[Tuple[float, float, float]],
    adjacency: Dict[int, List[int]],
    nose_index: int,
) -> Dict[int, int]:
    """Assign each vertex a layer index based on distance from nose."""
    from collections import deque

    layers: Dict[int, int] = {nose_index: 0}
    q = deque([nose_index])

    while q:
        v = q.popleft()
        layer_v = layers[v]
        for nb in adjacency.get(v, []):
            if nb not in layers:
                layers[nb] = layer_v + 1
                q.append(nb)

    return layers


def build_station_vertex_groups(
    verts: List[Tuple[float, float, float]],
    layers: Dict[int, int],
    nose_index: int,
    tail_index: int,
    atol_z: float = 1e-4,
) -> List[BodyStation]:
    """Group vertices into stations based on z and topological distance."""
    stations: List[BodyStation] = []

    nose_z = verts[nose_index][2]
    tail_z = verts[tail_index][2]

    # Collect by (rounded z, layer)
    bucket: Dict[Tuple[float, int], List[int]] = {}
    for idx, (x, y, z) in enumerate(verts):
        z_rounded = round(z / atol_z) * atol_z
        layer = layers.get(idx, 0)
        key = (z_rounded, layer)
        bucket.setdefault(key, []).append(idx)

    station_map: Dict[float, List[int]] = {}
    for (z_rounded, _layer), vert_indices in bucket.items():
        station_map.setdefault(z_rounded, []).extend(vert_indices)

    z_values_sorted = sorted(station_map.keys())

    for z_val in z_values_sorted:
        v_indices = list(sorted(set(station_map[z_val])))
        is_tip = abs(z_val - nose_z) < atol_z
        is_tail = abs(z_val - tail_z) < atol_z
        stations.append(
            BodyStation(
                z_ft=ft_from_meters(z_val),
                ring_indices=v_indices,
                is_tip=is_tip,
                is_tail=is_tail,
                debug_info={"z_val_m": z_val},
            )
        )

    return stations


def build_pm_rings_for_mesh(body_info: BodyMeshInfo) -> List[BodyPMRing]:
    """From BodyMeshInfo, build ordered PM rings and detect tip/tail."""
    verts = body_info.vertices
    faces = body_info.faces

    if not verts or not faces:
        return []

    # Nose / tail by z-extrema in recentered coords
    z_coords = [v[2] for v in verts]
    nose_index = z_coords.index(min(z_coords))
    tail_index = z_coords.index(max(z_coords))

    adjacency = build_vertex_adjacency(body_info.faces)
    layers = compute_topological_layers(verts, adjacency, nose_index)

    stations = build_station_vertex_groups(
        verts, layers, nose_index, tail_index
    )

    pm_rings: List[BodyPMRing] = []

    for j, station in enumerate(stations):
        ring_verts = [verts[idx] for idx in station.ring_indices]
        pm_rings.append(
            BodyPMRing(
                j_index=j,
                z_ft=station.z_ft,
                verts_ordered=ring_verts,
                is_tip=station.is_tip,
                is_tail=station.is_tail,
                debug_info={"ring_indices": station.ring_indices},
            )
        )

    return pm_rings


# --------------------------------------------------------------------------------------
# High-level body dictionary builder from Blender
# --------------------------------------------------------------------------------------


def build_bodies_from_blender(
    meshes: Dict[str, Dict[str, Any]],
    start_body_index: int = 0,
) -> Dict[str, BodyPMDefinition]:
    """Build full BodyPMDefinition objects for each mesh coming from Blender."""
    bodies: Dict[str, BodyPMDefinition] = {}
    body_index = start_body_index

    # Deterministic order
    for mesh_name in sorted(meshes.keys()):
        mesh_data = meshes[mesh_name]

        body_mesh_info = build_body_mesh_info_from_group(mesh_name, mesh_data)
        rings = build_pm_rings_for_mesh(body_mesh_info)

        bodies[mesh_name] = BodyPMDefinition(
            body_index=body_index,
            mesh_name=mesh_name,
            rings=rings,
            offset=body_mesh_info.offset,
            span=body_mesh_info.span,
            is_symmetric=body_mesh_info.is_symmetric,
            debug_info=body_mesh_info.debug_info,
        )

        body_index += 1

    return bodies


# --------------------------------------------------------------------------------------
# ACF body block generation (base-style _geo_xyz writer)
# --------------------------------------------------------------------------------------


def rewrite_acf_bodies(
    acf_in_path: str,
    acf_out_path: str,
    new_body_lines: List[str],
) -> None:
    """Replace all P _body lines inside PROPERTIES_BEGIN/END with new bodies."""
    with open(acf_in_path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]

    prop_begin = None
    prop_end = None

    for idx, line in enumerate(lines):
        if line.strip() == "PROPERTIES_BEGIN":
            prop_begin = idx
        elif line.strip() == "PROPERTIES_END":
            prop_end = idx
            break

    if prop_begin is None or prop_end is None or prop_end <= prop_begin:
        raise RuntimeError("Could not find valid PROPERTIES_BEGIN/END block in ACF.")

    body_start = None
    body_end = None
    for idx in range(prop_begin + 1, prop_end):
        if lines[idx].lstrip().startswith("P _body/"):
            if body_start is None:
                body_start = idx
            body_end = idx

    if body_start is None:
        body_start = prop_begin + 1
        body_end = body_start - 1

    new_lines: List[str] = []
    new_lines.extend(lines[:body_start])
    new_lines.extend(new_body_lines)
    new_lines.extend(lines[body_end + 1:])

    with open(acf_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


def _pm_i_print_order(total_stations: int = 20) -> List[int]:
    order: List[int] = []
    if total_stations > 0:
        order.append(0)
    if total_stations > 1:
        order.append(1)
    for i in range(10, total_stations):
        order.append(i)
    for i in range(2, 10):
        if i < total_stations and i not in order:
            order.append(i)
    return order


def _pm_j_print_order(points_per_ring: int = 18) -> List[int]:
    order: List[int] = []
    if points_per_ring > 0:
        order.append(0)
    if points_per_ring > 1:
        order.append(1)
    for j in range(10, points_per_ring):
        order.append(j)
    for j in range(2, 10):
        if j < points_per_ring and j not in order:
            order.append(j)
    return order


def build_body_block_lines(
    bodies: Dict[str, BodyPMDefinition],
    template_path: str = "",
    total_stations: int = 20,
    points_per_ring: int = 18,
) -> List[str]:
    """
    Build COMPLETE Plane-Maker body blocks for *all* bodies.

    This adapts the original per-body _geo_xyz writer to the
    BodyPMDefinition structure produced by build_bodies_from_blender(),
    and returns one concatenated list of lines for all bodies.
    """
    # Order bodies by their PlaneMaker body_index
    body_list: List[BodyPMDefinition] = sorted(
        bodies.values(), key=lambda b: b.body_index
    )

    all_lines: List[str] = []

    for bdef in body_list:
        rings_m = [ring.verts_ordered for ring in bdef.rings]

        if not rings_m:
            continue

        # Convert all verts to feet
        rings_ft: List[List[Tuple[float, float, float]]] = []
        max_ring_len = 0
        max_radius_ft = 0.0
        sum_x_ft = 0.0
        count_x = 0

        for ring in rings_m:
            ring_ft: List[Tuple[float, float, float]] = []
            for (x_m, y_m, z_m) in ring:
                x_ft = ft_from_meters(x_m)
                y_ft = ft_from_meters(y_m)
                z_ft = ft_from_meters(z_m)
                ring_ft.append((x_ft, y_ft, z_ft))

                r_ft = math.hypot(x_ft, y_ft)
                if r_ft > max_radius_ft:
                    max_radius_ft = r_ft

                sum_x_ft += x_ft
                count_x += 1

            rings_ft.append(ring_ft)
            if len(ring_ft) > max_ring_len:
                max_ring_len = len(ring_ft)

        # Lateral offset: average x over all verts (in feet)
        part_x_ft = sum_x_ft / count_x if count_x > 0 else 0.0
        part_rad_ft = max_radius_ft

        # If caller's points_per_ring / total_stations are too small, grow them
        points_per_ring_eff = max(points_per_ring, max_ring_len)
        total_stations_eff = max(total_stations, len(rings_ft))

        # Header expects full ring size and station count
        r_dim = points_per_ring_eff
        s_dim = len(rings_ft)

        b = bdef.body_index

        # --- Header block for this body ---
        lines: List[str] = []
        lines.append(f"P _body/{b}/_part_x {round_ft(part_x_ft):.9f}")
        lines.append("P _body/{b}/_part_y 0.000000000".format(b=b))
        lines.append("P _body/{b}/_part_z 0.000000000".format(b=b))
        lines.append(f"P _body/{b}/_part_rad {round_ft(part_rad_ft):.9f}")
        lines.append(f"P _body/{b}/_r_dim {r_dim:d}")
        lines.append(f"P _body/{b}/_s_dim {s_dim:d}")
        lines.append("")  # blank line for readability

        # --- Prepare padded rings grid for geo ---
        padded: List[List[Tuple[float, float, float]]] = []

        # Real rings first
        for i in range(min(len(rings_ft), total_stations_eff)):
            ring = list(rings_ft[i])
            if len(ring) < points_per_ring_eff:
                ring += [(0.0, 0.0, 0.0)] * (points_per_ring_eff - len(ring))
            padded.append(ring)

        # Extra stations (up to total_stations_eff) as all zeros
        for _ in range(len(padded), total_stations_eff):
            padded.append([(0.0, 0.0, 0.0)] * points_per_ring_eff)

        # PM's station and j print order
        i_order = _pm_i_print_order(total_stations_eff)
        j_order = _pm_j_print_order(points_per_ring_eff)

        # --- _geo_xyz block in PM order ---
        for i in i_order:
            ring = padded[i]
            for j in j_order:
                x_ft, y_ft, z_ft = ring[j]
                lines.append(f"P _body/{b}/_geo_xyz/{i},{j},0 {round_ft(x_ft):.9f}")
                lines.append(f"P _body/{b}/_geo_xyz/{i},{j},1 {round_ft(y_ft):.9f}")
                lines.append(f"P _body/{b}/_geo_xyz/{i},{j},2 {round_ft(z_ft):.9f}")

        all_lines.extend(lines)

    return all_lines
