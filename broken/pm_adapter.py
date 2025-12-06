from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

import bpy
from mathutils import Vector

from . import cis_bodies2pm
from . import cis_wings2pm  # wings glue still to be wired properly later

# ---------------------------------------------------------------------------
#  Types
# ---------------------------------------------------------------------------

LogFn = Callable[[str], None]


# ---------------------------------------------------------------------------
#  Coordinate transform helpers
# ---------------------------------------------------------------------------

def blender_to_pm_coords(co: Vector) -> Tuple[float, float, float]:
    """
    Convert a Blender world-space coord to PlaneMaker coord system.

    Blender world:
        -Y forward, Z up, X right

    PlaneMaker convention we’ve been using:
        -Z forward, Y up, X right

    Mapping:
        x_pm = x_bl
        y_pm = z_bl
        z_pm = -y_bl
    """
    return (co.x, co.z, -co.y)


def extract_mesh_geometry(
    obj: bpy.types.Object,
    depsgraph: bpy.types.Depsgraph,
) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int, int]]]:
    """
    Extract verts and *quad* faces from a Blender mesh in PM coordinates.

    Returns:
        verts_pm: list of (x, y, z) in PM coords
        faces_idx: list of (i0, i1, i2, i3) vertex indices (quads only)
    """
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    try:
        verts_pm: List[Tuple[float, float, float]] = []
        for v in mesh.vertices:
            co_world = eval_obj.matrix_world @ v.co
            verts_pm.append(blender_to_pm_coords(co_world))

        faces_idx: List[Tuple[int, int, int, int]] = []
        for poly in mesh.polygons:
            # We only keep quads; tris/ngons can be handled later if needed
            if len(poly.vertices) == 4:
                v0, v1, v2, v3 = poly.vertices
                faces_idx.append((v0, v1, v2, v3))

        return verts_pm, faces_idx
    finally:
        eval_obj.to_mesh_clear()


# ---------------------------------------------------------------------------
#  Mesh classification & collection
# ---------------------------------------------------------------------------

def classify_mesh_for_flightmodel(name: str) -> str | None:
    """
    Decide whether a mesh is a 'body', 'wing', or ignored for the flight model.

    Adjust the keyword lists if you change your naming convention.
    """
    lname = name.lower()

    # BODY identifiers
    body_keys = [
        "fuselage", "cowl", "cowling",
        "fairing", "tail", "nose",
        "body",
    ]
    for k in body_keys:
        if k in lname:
            return "body"

    # WING identifiers (single-surface philosophy)
    wing_keys = [
        "wing",
        "hstab", "horizontal",
        "vstab", "vertical",
    ]
    for k in wing_keys:
        if k in lname:
            return "wing"

    return None


def collect_flightmodel_meshes(
    collection: bpy.types.Collection,
    logger: LogFn | None = None,
) -> Tuple[
    Dict[str, Dict[str, Any]],
    Dict[str, Dict[str, Any]],
]:
    """
    Reads all visible meshes inside the chosen Blender collection and returns:

        bodies_geo = {
            mesh_name: {
                "verts": [(x, y, z), ...],
                "faces": [(i0, i1, i2, i3), ...],  # quads
            }, ...
        }

        wings_geo = { ... }

    All vertices are in PM coordinate system.
    """
    log = logger or (lambda msg: None)

    log(f"[ADAPTER] Collecting geometry from collection '{collection.name}'")
    depsgraph = bpy.context.evaluated_depsgraph_get()

    bodies_geo: Dict[str, Dict[str, Any]] = {}
    wings_geo: Dict[str, Dict[str, Any]] = {}

    for obj in collection.objects:
        if obj.type != "MESH":
            continue
        if obj.hide_viewport or obj.hide_get():
            # honour visibility: hidden meshes are ignored for FM
            continue

        classification = classify_mesh_for_flightmodel(obj.name)
        if classification is None:
            log(f"[ADAPTER] Skipping '{obj.name}' (unclassified mesh)")
            continue

        verts_pm, faces_idx = extract_mesh_geometry(obj, depsgraph)

        entry = {
            "verts": verts_pm,
            "faces": faces_idx,
        }

        if classification == "body":
            bodies_geo[obj.name] = entry
            log(
                f"[ADAPTER] Body mesh: '{obj.name}'  "
                f"V={len(verts_pm)} F_quads={len(faces_idx)}"
            )
        elif classification == "wing":
            wings_geo[obj.name] = entry
            log(
                f"[ADAPTER] Wing mesh: '{obj.name}'  "
                f"V={len(verts_pm)} F_quads={len(faces_idx)}"
            )

    return bodies_geo, wings_geo


# ---------------------------------------------------------------------------
#  Bodies pipeline glue
# ---------------------------------------------------------------------------

def _auto_mesh_rows_for_bodies(
    bodies_geo: Dict[str, Dict[str, Any]],
    logger: LogFn | None = None,
) -> List[Dict[str, Any]]:
    """
    Legacy helper preserved in case you want an explicit index mapping later.

    Currently UNUSED by the Blender → cis_bodies2pm pipeline.
    """
    log = logger or (lambda msg: None)

    mesh_rows: List[Dict[str, Any]] = []
    used: set[int] = set()

    default_index = getattr(cis_bodies2pm, "default_index_for_name", None)

    for name in sorted(bodies_geo.keys()):
        if default_index is not None:
            idx = default_index(name)
        else:
            idx = len(used)

        while idx in used:
            idx += 1
        used.add(idx)

        pm_name = name
        lname = name.lower()
        if "fuselage" in lname:
            pm_name = "Fuselage"
        elif "lf_cowling" in lname:
            pm_name = "Left Cowling"
        elif "rt_cowling" in lname:
            pm_name = "Right Cowling"

        row = {
            "mesh_name": name,
            "body_index": idx,
            "pm_name": pm_name,
        }
        mesh_rows.append(row)

        log(f"[BODIES] Mapping mesh '{name}' → body {idx} ('{pm_name}')")

    return mesh_rows


def run_bodies_from_collection(
    collection: bpy.types.Collection,
    acf_in_path: str,
    acf_out_path: str,
    template_path: str,
    logger: LogFn | None = None,
) -> None:
    """
    Full bodies-only pipeline driven from Blender:

      1) Collect meshes & convert coords (bodies_geo)
      2) Call cis_bodies2pm.build_bodies_from_blender(bodies_geo)
      3) Build body-block lines from template
      4) Rewrite ACF bodies block and write to acf_out_path
    """
    log = logger or (lambda msg: None)

    log("[BODIES] Starting bodies pipeline from Blender collection")

    bodies_geo, _wings_geo = collect_flightmodel_meshes(collection, logger=log)

    if not bodies_geo:
        log("[BODIES] No body meshes found in collection; nothing to do.")
        return

    # 2) Blender → BodyPMDefinition dict
    try:
        bodies = cis_bodies2pm.build_bodies_from_blender(
            meshes=bodies_geo,
        )
    except Exception as e:
        log(f"[BODIES][ERROR] build_bodies_from_blender failed: {e}")
        raise

    if not bodies:
        log("[BODIES][ERROR] No bodies returned from build_bodies_from_blender.")
        return

    log(f"[BODIES] Built {len(bodies)} body definition(s)")

    # 3) Build body-block lines from template (template_path kept for future use)
    try:
        new_body_lines = cis_bodies2pm.build_body_block_lines(
            bodies=bodies,
            template_path=template_path,
        )
    except Exception as e:
        log(f"[BODIES][ERROR] build_body_block_lines failed: {e}")
        raise

    # 4) Rewrite ACF bodies block (path-based, like the standalone tool)
    try:
        cis_bodies2pm.rewrite_acf_bodies(
            acf_in_path=acf_in_path,
            acf_out_path=acf_out_path,
            new_body_lines=new_body_lines,
        )
    except Exception as e:
        log(f"[BODIES][ERROR] rewrite_acf_bodies failed: {e}")
        raise

    log(f"[BODIES][OK] Wrote new bodies into '{acf_out_path}'.")


# ---------------------------------------------------------------------------
#  Wings pipeline glue (placeholder)
# ---------------------------------------------------------------------------

def run_wings_from_collection(
    collection: bpy.types.Collection,
    acf_in_path: str,
    acf_out_path: str,
    logger: LogFn | None = None,
) -> None:
    """
    Placeholder for the wings pipeline. This is here so __init__.py can call it
    without blowing up, but the actual logic is still to be ported.
    """
    log = logger or (lambda msg: None)
    log("[WINGS] Wings pipeline not implemented yet in pm_adapter.")
    # TODO: wire cis_wings2pm once bodies are fully validated.
