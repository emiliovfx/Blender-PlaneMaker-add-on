bl_info = {
    "name": "CIS PlaneMaker Generator CC",
    "author": "Emilio / Capt. Iceman",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "Properties > Scene",
    "description": "Generate / update PlaneMaker .acf from Blender flight-model meshes",
    "category": "Import-Export",
}

import os
import bpy


from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
)

from bpy.props import (
    StringProperty,
    EnumProperty,
    PointerProperty,
    FloatProperty,
)

# NEW: import cis_logging so we can reuse its open_log_in_text_editor()
from . import pm_adapter, cis_logging, cis_bodies2pm, cis_wings2pm


# ---------------------------------------------------------------------------
# Helpers: addon path + logger
# ---------------------------------------------------------------------------

def _get_addon_root() -> str:
    """Return the folder where this add-on lives."""
    return os.path.dirname(os.path.abspath(__file__))


def _log_path() -> str:
    return os.path.join(_get_addon_root(), "cis_pm_generator_log.txt")


def log_line(msg: str) -> None:
    """Append a line to cis_pm_generator_log.txt."""
    try:
        with open(_log_path(), "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        print(f"[CIS_PM] Failed to write log: {e}")

def _cis_iter_visible_mesh_objects_recursive(collection):
    yielded = set()
    for obj in collection.objects:
        if obj.type == "MESH" and obj.visible_get():
            key = obj.as_pointer() if hasattr(obj, "as_pointer") else id(obj)
            if key not in yielded:
                yielded.add(key); yield obj
    for child in collection.children_recursive:
        for obj in child.objects:
            if obj.type == "MESH" and obj.visible_get():
                key = obj.as_pointer() if hasattr(obj, "as_pointer") else id(obj)
                if key not in yielded:
                    yielded.add(key); yield obj

# ---------------------------------------------------------------------------
# Properties on Scene
# ---------------------------------------------------------------------------

class CIS_PM_Properties(PropertyGroup):
    # Flight model collection
    flight_model_collection: PointerProperty(
        name="Flight Model Collection",
        description="Collection containing the flight-model meshes (bodies, wings, etc.)",
        type=bpy.types.Collection,
    )

    # Dihedral angle (single value used for wings and cowlings)
    dihedral_angle: FloatProperty(
        name="Dihedral (deg)",
        description="Dihedral angle in degrees (used for wings and cowlings)",
        default=0.0,
    )

    # Mode: modify existing vs create new
    mode: EnumProperty(
        name="Aircraft Mode",
        description="Whether to modify an existing .acf or create a new one from template",
        items=[
            ("MODIFY", "Modify existing aircraft", "Modify an existing .acf file"),
            ("NEW", "Create new aircraft", "Create a new .acf from the CIS template"),
        ],
        default="MODIFY",
    )

    # Path to existing .acf when modifying
    acf_path: StringProperty(
        name="Aircraft .acf",
        description="Existing PlaneMaker .acf file to modify "
                    "(ignored when creating a new aircraft from template)",
        subtype="FILE_PATH",
    )

    # New aircraft name (used when mode == NEW)
    new_aircraft_name: StringProperty(
        name="New aircraft name",
        description="File name for the new .acf (when creating a new aircraft)",
        default="CIS_NewAircraft",
    )


# ---------------------------------------------------------------------------
# Operator: generate / update ACF
# ---------------------------------------------------------------------------

class CIS_OT_PMGenerate(Operator):
    """Generate / update the ACF using Blender flight-model meshes."""
    bl_idname = "cis_pm.generate_aircraft"
    bl_label = "Generate Aircraft"
    bl_description = (
        "Generate / update the PlaneMaker .acf bodies from the Flight Model Collection"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        props = scene.cis_pm

        col = props.flight_model_collection
        if col is None:
            self.report({"ERROR"}, "No Flight Model Collection selected.")
            return {"CANCELLED"}

        # Collect visible mesh objects only (as before, and log them)
        # Collect visible mesh objects recursively (viewport visibility; includes subcollections)
        meshes = list(_cis_iter_visible_mesh_objects_recursive(col))

        # meshes = []
        # for obj in col.objects:
        #     if obj.type != "MESH":
        #         continue
        #     if obj.hide_get():
        #         continue
        #     if obj.hide_viewport:
        #         continue
        #     meshes.append(obj)

        if not meshes:
            self.report({"ERROR"}, "No visible mesh objects in the Flight Model Collection.")
            return {"CANCELLED"}

        # Start log
        log_line("=" * 72)
        log_line("CIS PlaneMaker generator – BODIES RUN")
        log_line(f"Mode        : {props.mode}")
        log_line(f"FlightModel : {col.name}")
        log_line(f"ACF path    : {props.acf_path!r}")
        log_line(f"New name    : {props.new_aircraft_name!r}")
        log_line(f"Dihedral    : {props.dihedral_angle} deg")
        log_line(f"Found {len(meshes)} visible mesh object(s):")

        for obj in meshes:
            me = obj.data
            log_line(
                f"  - {obj.name}: verts={len(me.vertices)}, faces={len(me.polygons)}"
            )

        # -------------------------------------------------------------------
        # Bodies pipeline via pm_adapter (MODIFY mode only for now)
        # -------------------------------------------------------------------
        if props.mode != "MODIFY":
            self.report({"ERROR"}, "Only 'Modify existing aircraft' mode is implemented for now.")
            log_line("[CIS_PM] ERROR: NEW mode not yet implemented.")
            return {"CANCELLED"}

        if not props.acf_path:
            self.report({"ERROR"}, "No Aircraft .acf file selected.")
            log_line("[CIS_PM] ERROR: acf_path is empty.")
            return {"CANCELLED"}

        acf_in_path = props.acf_path

        # Output: create a new file next to the input with _CIS suffix
        base, ext = os.path.splitext(acf_in_path)
        acf_out_path = base + "_CIS" + ext

        # Body template: use the zeroed body-block template in /templates
        addon_root = _get_addon_root()
        body_template_path = os.path.join(
            addon_root,
            "templates",
            "body_block_template_zeroed.txt",
        )

        log_line(f"[CIS_PM] Using body template: {body_template_path}")
        log_line(f"[CIS_PM] Input ACF : {acf_in_path}")
        log_line(f"[CIS_PM] Output ACF: {acf_out_path}")

        try:
            pm_adapter.run_bodies_from_collection(
                collection=col,
                acf_in_path=acf_in_path,
                acf_out_path=acf_out_path,
                template_path=body_template_path,
                logger=log_line,
            )
        except Exception as e:
            msg = f"[CIS_PM] ERROR: bodies pipeline failed: {e}"
            log_line(msg)
            print(msg)
            self.report({"ERROR"}, "Bodies pipeline failed; check cis_pm_generator_log.txt")
            return {"CANCELLED"}
        # === CIS: Wire bodies and wings using the dumped virtual OBJ ===
        try:
            dump_path = pm_adapter.default_dump_path()
        except Exception:
            dump_path = os.path.join(_get_addon_root(), "vmesh", "virtual_obj_dump.txt")

        wing_template_path = os.path.join(_get_addon_root(), "templates", "wing_block_template_zeroed.txt")
        log_line(f"[CIS_PM] Using wing template: {wing_template_path}")
        log_line(f"[CIS_PM] Using virtual OBJ: {dump_path}")

        names = cis_bodies2pm.scan_obj_mesh_names(dump_path)
        prio = {"Fuselage": 0, "LF_Cowling": 1, "RT_Cowling": 2}
        mesh_rows = []
        used = set()
        for key, idx0 in prio.items():
            for n in names:
                if n.startswith(key):
                    mesh_rows.append({"mesh_name": n, "body_index": idx0, "pm_name": n})
                    used.add(n)
                    break
        next_idx = 3
        for n in names:
            if n in used:
                continue
            mesh_rows.append({"mesh_name": n, "body_index": next_idx, "pm_name": n})
            next_idx += 1
        log_line(f"[CIS_PM] Bodies mapping (mesh_rows): {mesh_rows}")

        try:
            # Bodies (manual build to inject dihedral into cowlings)
            bodies = cis_bodies2pm.build_bodies_from_obj(dump_path)
            by_name = {b["group_name"]: b for b in bodies}

            bodies_by_idx = {}
            for row in mesh_rows:
                name = row["mesh_name"]
                idx  = row["body_index"]
                if name in by_name and idx not in bodies_by_idx:
                    body = dict(by_name[name])
                    body["pm_name"] = row["pm_name"]
                    bodies_by_idx[idx] = body

            indices = sorted(bodies_by_idx.keys())
            ordered = [bodies_by_idx[i] for i in indices]

            all_lines = []
            for i, _ in enumerate(ordered):
                ordered[i]["body_index"] = i
                blk = cis_bodies2pm.build_body_block_from_template(
                    ordered, i, body_template_path, wing_dihed_deg=props.dihedral_angle
                )
                all_lines.extend(blk)

            cis_bodies2pm.rewrite_acf_bodies(acf_in_path, acf_out_path, all_lines)
            log_line("[CIS_PM] Bodies written with dihedral applied to cowlings.")

        except Exception as e:
            msg = f"[CIS_PM] ERROR: bodies generation failed: {e}"
            log_line(msg); print(msg)
            self.report({"ERROR"}, "Bodies generation failed; check cis_pm_generator_log.txt")
            return {"CANCELLED"}

        try:
            dihed = props.dihedral_angle
            panel_data = cis_wings2pm.compute_all_panels(dump_path, dihed, log_func=log_line)
            log_line("[CIS_PM] Computed wing panels.")
            out_after_wings = cis_wings2pm.generate_wings_from_template_and_rewrite_acf(
                acf_out_path,
                panel_data,
                wing_template_path,
                log_func=log_line,
            )
            acf_out_path = out_after_wings or acf_out_path
            log_line(f"[CIS_PM] Wings written. Current ACF: {acf_out_path}")
        except Exception as e:
            msg = f"[CIS_PM] ERROR: wings generation failed: {e}"
            log_line(msg); print(msg)
            self.report({"ERROR"}, "Wings generation failed; check cis_pm_generator_log.txt")
            return {"CANCELLED"}
        # === End CIS wiring ===


        self.report(
            {"INFO"},
            f"Generated bodies into: {acf_out_path}",
        )
        log_line(f"[CIS_PM] OK: Generated bodies into '{acf_out_path}'")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# NEW: Operator to open log in Blender Text Editor
# ---------------------------------------------------------------------------

class CIS_OT_PMOpenLog(Operator):
    """Open the CIS PM log in Blender's Text Editor."""
    bl_idname = "cis_pm.open_log"
    bl_label = "Open Log"

    def execute(self, context):
        try:
            # Delegate to cis_logging helper so we don't reinvent handling
            cis_logging.open_log_in_text_editor()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open log: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, "Opened cis_pm_generator_log.txt in Text Editor.")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# NEW: Operator to clear the log file
# ---------------------------------------------------------------------------

class CIS_OT_PMClearLog(Operator):
    """Clear the CIS PM log file."""
    bl_idname = "cis_pm.clear_log"
    bl_label = "Clear Log"

    def execute(self, context):
        path = _log_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear log: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, "cis_pm_generator_log.txt cleared.")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Panel in Scene properties
# ---------------------------------------------------------------------------

class CIS_PT_PMPanel(Panel):
    bl_idname = "CIS_PT_PlaneMakerPanel"
    bl_label = "CIS PlaneMaker Generator"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.cis_pm

        col = layout.column(align=True)
        col.label(text="Flight Model Geometry")
        col.prop(props, "flight_model_collection")
        col.prop(props, "dihedral_angle")

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Aircraft mode")
        col.prop(props, "mode", expand=True)

        if props.mode == "MODIFY":
            col.prop(props, "acf_path")
        else:
            col.prop(props, "new_aircraft_name")

        layout.separator()
        col = layout.column(align=True)
        col.operator("cis_pm.generate_aircraft", icon="MOD_BUILD")

        # NEW: Log controls
        layout.separator()
        row = layout.row(align=True)
        row.operator("cis_pm.open_log", icon="TEXT")
        row.operator("cis_pm.clear_log", icon="TRASH")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    CIS_PM_Properties,
    CIS_OT_PMGenerate,
    CIS_OT_PMOpenLog,   # NEW
    CIS_OT_PMClearLog,  # NEW
    CIS_PT_PMPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cis_pm = PointerProperty(
        name="CIS PlaneMaker Settings CC",
        type=CIS_PM_Properties,
    )


def unregister():
    del bpy.types.Scene.cis_pm

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
