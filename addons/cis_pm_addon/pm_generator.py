# cis_pm_addon/pm_generator.py

from __future__ import annotations

from typing import Dict, List, Tuple

import bpy
from mathutils import Vector

from . import cis_logging

# ⬇️ You will wire these to your existing modules.
#    Update the imports / function names once you hook them up.
# --------------------------------------------------------------------
# Example:
# from .cis_bodies2pm import build_bodies_blocks_from_mesh
# from .cis_wings2pm import build_wings_blocks_from_mesh
# from .cis_acf_io import (
#     prepare_acf_for_generation,
#     inject_body_and_wing_blocks,
# )


def blender_to_obj_coords(co: Vector) -> Tuple[float, float, float]:
    """
    Convert Blender coordinates to the OBJ-space axes you used before.

    Blender export setting:
        Forward = -Z
        Up      =  Y

    Mapping:
        obj_x = blender_x
        obj_y = blender_z
        obj_z = -blender_y
    """
    return (co.x, co.z, -co.y)


def classify_mesh(obj: bpy.types.Object) -> str:
    """
    Very simple classifier based on name.
    Returns "BODY" or "WING".
    Adjust this to match your naming conventions.
    """
    name = obj.name.lower()
    if ("wing" in name) or ("stab" in name):
        return "WING"
    return "BODY"


def collect_mesh_data_from_collection(
    collection: bpy.types.Collection,
    dihedral_angle_rad: float,
    logger,
) -> Dict[str, List[Dict]]:
    """
    Scan the collection, pull mesh geometry and classify into bodies/wings.

    Returns a dict:
    {
        "bodies": [ { "obj": obj, "name": str, "verts": [(x,y,z), ...], "dihedral": float }, ... ],
        "wings":  [ { ... }, ... ]
    }
    """
    data = {"bodies": [], "wings": []}

    logger.info("Scanning collection '%s' for mesh objects", collection.name)

    for obj in collection.objects:
        if obj.type != "MESH":
            continue

        if not obj.visible_get():
            logger.info("Skipping hidden object: %s", obj.name)
            continue

        mesh_type = classify_mesh(obj)
        logger.info("Object '%s' classified as %s", obj.name, mesh_type)

        # Evaluate depsgraph so we get modifiers applied if needed
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

        verts_obj_space: List[Tuple[float, float, float]] = []
        for v in eval_mesh.vertices:
            # World-space coordinate
            world_co = eval_obj.matrix_world @ v.co
            verts_obj_space.append(blender_to_obj_coords(world_co))

        eval_obj.to_mesh_clear()

        entry = {
            "obj": obj,
            "name": obj.name,
            "verts": verts_obj_space,
            "dihedral": dihedral_angle_rad,
        }

        if mesh_type == "WING":
            data["wings"].append(entry)
        else:
            data["bodies"].append(entry)

    logger.info(
        "Collected %d body meshes and %d wing meshes",
        len(data["bodies"]),
        len(data["wings"]),
    )
    return data


def generate_from_scene(context: bpy.types.Context, props) -> Dict[str, object]:
    """
    Main entry point called from the operator.

    Expected 'props' is CIS_PM_Properties (from __init__.py).
    Returns a result dict with a few summary values.
    """
    logger = cis_logging.setup_logger()
    logger.info("=== CIS PM Generator run started ===")

    collection = props.use_collection
    if collection is None:
        msg = "No Flight Model collection selected."
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info("Using collection: %s", collection.name)
    logger.info("Operation mode : %s", props.operation_mode)
    logger.info("Dihedral angle : %f degrees", props.dihedral_angle)

    # Convert dihedral to radians – your downstream code can decide what to do with it
    dihedral_angle_rad = props.dihedral_angle

    # 1) Collect mesh data from Blender
    mesh_data = collect_mesh_data_from_collection(collection, dihedral_angle_rad, logger)

    # 2) Prepare target .acf (NEW vs MODIFY) – wire this to your old logic
    # --------------------------------------------------------------------
    # TODO: uncomment and implement these functions in cis_acf_io.py
    #
    # from .cis_acf_io import prepare_acf_for_generation, inject_body_and_wing_blocks
    #
    # acf_path = prepare_acf_for_generation(props, logger)
    #
    acf_path = "<acf path not wired yet>"

    # 3) Call your existing bodies/wings modules
    # --------------------------------------------------------------------
    body_blocks: List[str] = []
    wing_blocks: List[str] = []

    # TODO: wire these to your actual processing functions
    # Example:
    # from .cis_bodies2pm import build_bodies_blocks_from_mesh
    # from .cis_wings2pm import build_wings_blocks_from_mesh
    #
    # body_blocks = build_bodies_blocks_from_mesh(mesh_data["bodies"], logger)
    # wing_blocks = build_wings_blocks_from_mesh(mesh_data["wings"], logger)
    #

    if mesh_data["bodies"]:
        logger.warning(
            "Bodies were collected but cis_bodies2pm integration is not wired yet."
        )
    if mesh_data["wings"]:
        logger.warning(
            "Wings were collected but cis_wings2pm integration is not wired yet."
        )

    # 4) Inject bodies/wings into the .acf
    # --------------------------------------------------------------------
    # TODO: call your cis_acf_io helper
    # inject_body_and_wing_blocks(acf_path, body_blocks, wing_blocks, logger)

    logger.info("=== CIS PM Generator run finished (skeleton) ===")

    return {
        "acf_path": acf_path,
        "num_body_meshes": len(mesh_data["bodies"]),
        "num_wing_meshes": len(mesh_data["wings"]),
        "num_body_blocks": len(body_blocks),
        "num_wing_blocks": len(wing_blocks),
    }
