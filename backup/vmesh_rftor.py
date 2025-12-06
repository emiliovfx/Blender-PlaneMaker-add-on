# === paste into cis_bodies2pm.py (replace only these two functions) ===
from typing import Iterable, Union, List, Dict, Any
import os

def build_bodies_from_obj(obj_source: Union[str, Iterable[str]]) -> List[Dict[str, Any]]:
    """
    Build all bodies from an OBJ *source* (path or in-memory lines) using topology-based rings.
    Each body: { body_index, group_name, part_x_ft, rings, half_n_max }
    NOTE: Only the input type changed. Downstream logic remains identical.
    """
    groups = load_all_groups_with_faces(obj_source)

    # --- keep the rest of your original function logic below this line unchanged ---
    # (classification, rings/topology, part_x_ft/part_rad_ft, etc.)
    # Example skeleton (your actual implementation already exists in the file):
    bodies: List[Dict[str, Any]] = []
    # ... your existing processing of `groups` into `bodies` ...
    return bodies


def load_all_groups_with_faces(obj_source: Union[str, Iterable[str]]) -> Dict[str, Dict[str, Any]]:
    """
    Load all groups from an OBJ *source*.

    For each group we build a *local* vertex array (only vertices referenced
    by that group's faces) and remap face indices to that local array.

    Returns:
        groups[group_name] = {
            "verts_m": [(x,y,z), ...],       # local verts (meters)
            "faces":   [[v_idx0,...], ...],  # faces using 0-based local indices
        }
    """
    # WHY: Allow two-pass parsing over either a file path or an in-memory virtual OBJ.
    def _materialize_lines(src: Union[str, Iterable[str]]) -> List[str]:
        if isinstance(src, str) and os.path.exists(src):
            with open(src, "r", encoding="utf-8", errors="ignore") as f:
                return f.readlines()
        # Ensure newline termination for consumers that expect it
        return [(ln if ln.endswith("\n") else ln + "\n") for ln in src]

    lines = _materialize_lines(obj_source)

    # ----------------
    # PASS 1: collect all global vertices (1-based in OBJ; we store 0-based list)
    # ----------------
    all_verts: List[tuple[float, float, float]] = []
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("v "):
            parts = s.split()
            # OBJ: v x y z
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            all_verts.append((x, y, z))

    # ----------------
    # PASS 2: collect groups and faces (global indices), then remap to local
    # ----------------
    groups_faces_global: Dict[str, List[List[int]]] = {}
    current: str | None = None

    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue

        if s.startswith("o ") or s.startswith("g "):
            current = s.split(maxsplit=1)[1]
            groups_faces_global.setdefault(current, [])
            continue

        if s.startswith("f "):
            if current is None:
                current = "_default"
                groups_faces_global.setdefault(current, [])
            face_tokens = s.split()[1:]
            # Accept forms: i, i/j, i/j/k; take vertex index before '/'
            face_idx: List[int] = []
            for tok in face_tokens:
                v_str = tok.split("/")[0]
                face_idx.append(int(v_str))  # still 1-based for now
            groups_faces_global[current].append(face_idx)

    # Build per-group local verts and faces (0-based local indices)
    groups: Dict[str, Dict[str, Any]] = {}
    for name, faces in groups_faces_global.items():
        if not faces:
            continue

        # Gather unique global vertex indices in order of first appearance
        used_global: List[int] = []
        seen = set()
        for f in faces:
            for gi in f:
                if gi not in seen:
                    seen.add(gi)
                    used_global.append(gi)

        # Local verts (meters) from global list; OBJ indices are 1-based
        verts_m = [all_verts[gi - 1] for gi in used_global]

        # Map global OBJ index -> local 0-based
        g2l = {gi: li for li, gi in enumerate(used_global)}

        # Remap faces to local indices
        faces_local: List[List[int]] = []
        for f in faces:
            faces_local.append([g2l[gi] for gi in f])

        groups[name] = {"verts_m": verts_m, "faces": faces_local}

    # Optional: deterministic ordering by group name if your downstream expects it
    # groups = dict(sorted(groups.items(), key=lambda kv: kv[0]))

    return groups
