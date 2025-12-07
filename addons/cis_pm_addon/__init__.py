# File: cis_pm_addon/__init__.py

bl_info = {
    "name": "CIS PlaneMaker Generator",
    "author": "Emilio / Capt. Iceman",
    "version": (0, 1, 3),
    "blender": (4, 5, 0),
    "location": "Properties > Scene",
    "description": "Generate / update PlaneMaker .acf from Blender flight-model meshes",
    "category": "Import-Export",
}

import os
import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import PointerProperty, EnumProperty, StringProperty, FloatProperty

# internal
from . import pm_adapter, cis_bodies2pm, cis_wings2pm, cis_logging


# -------- Paths (anchored to addon root) --------
def _get_addon_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def _templates_dir() -> str:
    return os.path.join(_get_addon_root(), "templates")

def _vmesh_dir() -> str:
    d = os.path.join(_get_addon_root(), "vmesh")
    os.makedirs(d, exist_ok=True)
    return d

def _dump_path() -> str:
    return os.path.join(_vmesh_dir(), "virtual_obj_dump.txt")

def _log_path() -> str:
    # keep in sync with cis_logging.log_path()
    return os.path.join(_get_addon_root(), "cis_pm_generator_log.txt")


# -------- Visible meshes (recursive, viewport visibility) --------
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


# -------- Properties --------
class CIS_PM_Properties(PropertyGroup):
    mode: EnumProperty(
        name="Mode",
        description="Generate using Modify or Create mode",
        items=[
            ("MODIFY", "Modify Existing", "Backup and overwrite an existing .acf"),
            ("CREATE", "Create New", "Create a new .acf from template"),
        ],
        default="MODIFY",
    )

    # Modify Existing
    existing_acf_path: StringProperty(
        name="Existing Aircraft",
        description="Path to an existing .acf to modify (a backup *_bak.acf will be created)",
        subtype="FILE_PATH",
        default="",
    )

    # Create New
    new_acf_dir: StringProperty(
        name="New Aircraft Folder",
        description="Folder where the new .acf will be created",
        subtype="DIR_PATH",
        default="",
    )

    new_acf_name: StringProperty(
        name="Aircraft Filename",
        description="Filename for the new aircraft (e.g., MyPlane.acf)",
        default="MyAircraft.acf",
    )

    # Common
    dihedral_angle: FloatProperty(
        name="Wing Dihedral (deg)",
        description="Dihedral angle in degrees applied to wing cowlings and wings",
        default=0.0,
        soft_min=-15.0, soft_max=15.0,
    )

    collection: PointerProperty(
        name="Flight Model Collection",
        description="Select the collection that contains the flight-model meshes (and its subcollections)",
        type=bpy.types.Collection,
    )


# -------- Panel --------
class CIS_PM_PT_Main(Panel):
    bl_idname = "CIS_PM_PT_main"
    bl_label = "CIS PlaneMaker Generator"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        props = context.scene.cis_pm
        col = self.layout.column(align=True)

        # Collection selector
        col.separator()
        row = col.row(align=True)
        row.label(text="Select Flight Model Collection")
        row.prop(props, "collection", text="")

        # Dihedral angle
        col.separator()
        col.prop(props, "dihedral_angle")

        # Mode row with label
        col.separator()
        row = col.row(align=True)
        row.label(text="Select Aircraft Generation Mode")
        row.prop(props, "mode", text="")


        # Modify block
        col.separator()
        box_mod = col.box()
        box_mod.label(text="Modify Existing Aircraft", icon="FILE_BLEND")
        box_mod.prop(props, "existing_acf_path")

        col.separator()

        # Create block
        box_new = col.box()
        box_new.label(text="Create New Aircraft", icon="FILE_NEW")
        row = box_new.row(align=True)
        row.prop(props, "new_acf_dir", text="New Aircraft Folder")
        box_new.prop(props, "new_acf_name", text="Aircraft Filename")


        col.separator()
        col.operator("cis_pm.generate", text="Generate PlaneMaker .acf", icon="PLAY")

        # Log controls (cis_pm.* operators)
        col.separator()
        row = col.row(align=True)
        row.operator("cis_pm.open_log", text="Open Log", icon="TEXT")
        row.operator("cis_pm.clear_log", text="Clear Log", icon="TRASH")




# ---------------------------------------------------------------------------
# NEW: Operator to open log in Blender Text Editor
# ---------------------------------------------------------------------------
class CIS_OT_PMOpenLog(Operator):
    """Open the CIS PM log in Blender's Text Editor."""
    bl_idname = "cis_pm.open_log"
    bl_label = "Open Log"

    def execute(self, context):
        try:
            # delegate: helper handles creating/locating the log and opening it
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


# -------- Operator --------
class CIS_OT_PMGenerate(Operator):
    bl_idname = "cis_pm.generate"
    bl_label = "Generate CIS PlaneMaker"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cis_pm

        def log_line(msg: str):
            p = _log_path()
            try:
                cis_logging.log_line(msg)  # use module if available
            except Exception:
                try:  # hard fallback: write ourselves
                    with open(p, "a", encoding="utf-8") as f:
                        f.write(msg + "\n")
                except Exception:
                    pass
                print(msg)

        # Validate collection
        col = props.collection
        if not col:
            self.report({"ERROR"}, "Select a Flight Model Collection first.")
            return {"CANCELLED"}

        meshes = list(_cis_iter_visible_mesh_objects_recursive(col))
        if not meshes:
            self.report({"ERROR"}, "No visible mesh objects found in the selected collection tree.")
            return {"CANCELLED"}

        log_line(f"[CIS_PM] Visible meshes: {len(meshes)}")
        for m in meshes[:24]:
            log_line(f"[CIS_PM]  - {m.name}")

        # Build & dump virtual OBJ
        try:
            lines = pm_adapter.build_virtual_obj_lines(context, col)
            dump_path = _dump_path()
            with open(dump_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            log_line(f"[CIS_PM] Virtual OBJ dumped: {dump_path} ({len(lines)} lines)")
        except Exception as e:
            self.report({"ERROR"}, f"Failed to build/dump virtual OBJ: {e}")
            return {"CANCELLED"}

        dihed = props.dihedral_angle

        # Resolve ACF target
        if props.mode == "MODIFY":
            acf_path = props.existing_acf_path
            if not acf_path or not os.path.isfile(acf_path):
                self.report({"ERROR"}, "Provide a valid path to an existing .acf file.")
                return {"CANCELLED"}
            base, ext = os.path.splitext(acf_path)
            bak_path = f"{base}_bak{ext}"
            try:
                import shutil
                shutil.copy2(acf_path, bak_path)
                log_line(f"[CIS_PM] Backup created: {bak_path}")
            except Exception as e:
                self.report({"ERROR"}, f"Failed to create backup: {e}")
                return {"CANCELLED"}
            acf_in_path = acf_path
            acf_out_path = acf_path  # overwrite original
        else:
            new_dir = props.new_acf_dir.strip()
            new_name = props.new_acf_name.strip()
            if not new_dir:
                self.report({"ERROR"}, "Provide the folder for the new aircraft.")
                return {"CANCELLED"}
            if not new_name:
                self.report({"ERROR"}, "Provide a filename for the new aircraft.")
                return {"CANCELLED"}
            if not new_name.lower().endswith(".acf"):
                new_name += ".acf"
            os.makedirs(new_dir, exist_ok=True)
            acf_out_path = os.path.join(new_dir, new_name)
            acf_in_path = acf_out_path
            template_acf = os.path.join(_templates_dir(), "CIS_Template.acf")
            if not os.path.isfile(template_acf):
                self.report({"ERROR"}, f"Template not found: {template_acf}")
                return {"CANCELLED"}
            try:
                import shutil
                shutil.copy2(template_acf, acf_out_path)
                log_line(f"[CIS_PM] Created new ACF from template: {acf_out_path}")
            except Exception as e:
                self.report({"ERROR"}, f"Failed to create new aircraft: {e}")
                return {"CANCELLED"}

        # Templates
        body_template_path = os.path.join(_templates_dir(), "body_block_template_zeroed.txt")
        wing_template_path = os.path.join(_templates_dir(), "wing_block_template_zeroed.txt")
        log_line(f"[CIS_PM] Body template: {body_template_path}")
        log_line(f"[CIS_PM] Wing template: {wing_template_path}")

        # Bodies mapping from OBJ names
        try:
            names = cis_bodies2pm.scan_obj_mesh_names(dump_path)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to scan OBJ groups: {e}")
            return {"CANCELLED"}

        prio = {"Fuselage": 0, "LF_Cowling": 1, "RT_Cowling": 2}
        mesh_rows, used = [], set()
        for key, idx in prio.items():
            for n in names:
                if n.startswith(key):
                    mesh_rows.append({"mesh_name": n, "body_index": idx, "pm_name": n})
                    used.add(n); break
        next_idx = 3
        for n in names:
            if n in used:
                continue
            mesh_rows.append({"mesh_name": n, "body_index": next_idx, "pm_name": n})
            next_idx += 1
        log_line(f"[CIS_PM] Bodies mapping (mesh_rows): {mesh_rows}")

        # Bodies: manual build to pass dihedral to cowlings
        try:
            bodies = cis_bodies2pm.build_bodies_from_obj(dump_path)
            by_name = {b["group_name"]: b for b in bodies}

            bodies_by_idx = {}
            for row in mesh_rows:
                name = row["mesh_name"]; idx = row["body_index"]
                if name in by_name and idx not in bodies_by_idx:
                    body = dict(by_name[name])
                    body["pm_name"] = row["pm_name"]
                    bodies_by_idx[idx] = body

            ordered = [bodies_by_idx[i] for i in sorted(bodies_by_idx.keys())]

            all_lines = []
            for i, _ in enumerate(ordered):
                ordered[i]["body_index"] = i
                blk = cis_bodies2pm.build_body_block_from_template(
                    ordered, i, body_template_path, wing_dihed_deg=dihed
                )
                all_lines.extend(blk)

            cis_bodies2pm.rewrite_acf_bodies(acf_in_path, acf_out_path, all_lines)
            log_line("[CIS_PM] Bodies written with dihedral applied to cowlings.")
        except Exception as e:
            self.report({"ERROR"}, f"Bodies generation failed: {e}")
            return {"CANCELLED"}

        # --- Wings ---
        try:
            panel_data = cis_wings2pm.compute_all_panels(dump_path, dihed, log_func=log_line)
            log_line("[CIS_PM] Computed wing panels.")
            out_after_wings = cis_wings2pm.generate_wings_from_template_and_rewrite_acf(
                acf_out_path, panel_data, wing_template_path, log_func=log_line
            )

            # keep only acf_out_path
            if out_after_wings and os.path.isfile(out_after_wings) and out_after_wings != acf_out_path:
                try:
                    os.replace(out_after_wings, acf_out_path)
                    log_line(f"[CIS_PM] Consolidated updated ACF into: {acf_out_path}")
                except Exception as e:
                    log_line(f"[CIS_PM] WARNING: consolidation failed: {e}")
            else:
                log_line(f"[CIS_PM] Wings written. ACF: {acf_out_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Wings generation failed: {e}")
            return {'CANCELLED'}


        # ✅ ALWAYS end execute with a FINISHED return
        self.report({'INFO'}, f"Done. Updated: {acf_out_path}")
        try:
            cis_logging.open_log_in_text_editor(focus=True)
        except Exception:
            pass
        return {'FINISHED'}



# -------- Registration --------
classes = (
    CIS_PM_Properties,
    CIS_PM_PT_Main,
    CIS_OT_PMOpenLog,   # ensure these are registered
    CIS_OT_PMClearLog,
    CIS_OT_PMGenerate,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cis_pm = PointerProperty(
        name="CIS PlaneMaker Settings CC",
        type=CIS_PM_Properties,
    )

    # Ensure log helper operators from cis_logging (if any) are available as well
    try:
        cis_logging.register()
    except Exception as e:
        print(f"[CIS_PM] cis_logging.register() failed: {e}")

def unregister():
    # Unregister helper operators first
    try:
        cis_logging.unregister()
    except Exception as e:
        print(f"[CIS_PM] cis_logging.unregister() failed: {e}")

    del bpy.types.Scene.cis_pm
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
