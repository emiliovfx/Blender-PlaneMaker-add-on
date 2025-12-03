bl_info = {
    "name": "CIS PlaneMaker Generator",
    "author": "Capt. Iceman",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "Properties > Scene",
    "description": "Generate PlaneMaker bodies/wings from Blender meshes",
    "category": "Import-Export",
}

import bpy
from bpy.types import PropertyGroup, Panel, Operator
from bpy.props import (
    EnumProperty,
    StringProperty,
    PointerProperty,
    BoolProperty,
    FloatProperty,
)
import os
import shutil

# Hardcoded template path for creating new aircraft
TEMPLATE_ACF_PATH = os.path.join(
    os.path.dirname(__file__),
    "templates",
    "CIS_Template.acf",  # adjust name if needed
)


class CIS_PM_Properties(PropertyGroup):
    aircraft_mode: EnumProperty(
        name="Mode",
        description="Choose whether to modify an existing aircraft or create a new one",
        items=[
            (
                "MODIFY",
                "Modify existing aircraft",
                "Modify an existing .acf in place (a *_bak.acf backup will be created)",
            ),
            (
                "NEW",
                "Create new aircraft",
                "Create a new .acf based on the internal CIS template",
            ),
        ],
        default="MODIFY",
    )

    # MODIFY mode
    existing_acf_filepath: StringProperty(
        name="Existing aircraft (.acf)",
        subtype="FILE_PATH",
        description=(
            "Existing PlaneMaker .acf file to modify in place. "
            "A backup *_bak.acf will be created next to this file."
        ),
    )

    # NEW mode
    new_acf_filename: StringProperty(
        name="New aircraft filename",
        description="Name for the new aircraft .acf (without extension)",
        default="CIS_NewAircraft",
    )

    output_dir: StringProperty(
        name="Output folder",
        subtype="DIR_PATH",
        description="Folder where the new .acf will be created",
    )

    # Geometry source
    source_collection: PointerProperty(
        name="Source Collection",
        type=bpy.types.Collection,
        description="Collection containing meshes to export to PlaneMaker",
    )

    dihedral_angle: FloatProperty(
        name="Dihedral angle",
        subtype="ANGLE",
        unit="ROTATION",
        description="Dihedral angle (used for wings and cowlings)",
        default=0.0,
    )

    verbose_log: BoolProperty(
        name="Verbose log",
        description="Print a verbose summary of what is being generated",
        default=True,
    )


class CIS_PT_PMGenerator(Panel):
    bl_label = "CIS PlaneMaker"
    bl_idname = "CIS_PT_pm_generator"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        props = context.scene.cis_pm

        # Mode selection
        layout.label(text="Aircraft Mode:")
        layout.prop(props, "aircraft_mode", expand=True)

        box = layout.box()
        if props.aircraft_mode == "MODIFY":
            box.label(text="Modify existing aircraft", icon="FILE_BLEND")
            box.prop(props, "existing_acf_filepath")
            info_box = layout.box()
            info_box.label(text="Behavior:", icon="INFO")
            info_box.label(text="• Backup: *_bak.acf next to original")
            info_box.label(text="• Output: original .acf is overwritten")
        else:
            box.label(text="Create new aircraft", icon="FILE_NEW")
            box.prop(props, "new_acf_filename")
            box.prop(props, "output_dir")

            tmpl_box = layout.box()
            tmpl_box.label(text="Template aircraft (.acf):", icon="FILE_BLEND")
            tmpl_box.label(text=os.path.basename(TEMPLATE_ACF_PATH))
            tmpl_box.label(text="(Path is hardcoded inside the add-on)")

        layout.separator()

        # Geometry source
        geom_box = layout.box()
        geom_box.label(text="Geometry Source", icon="OUTLINER_COLLECTION")
        geom_box.prop(props, "source_collection")
        geom_box.prop(props, "dihedral_angle")

        layout.separator()
        layout.prop(props, "verbose_log")
        layout.operator("cis_pm.generate_aircraft", icon="FILE_TICK")


class CIS_PM_OT_Generate(Operator):
    bl_idname = "cis_pm.generate_aircraft"
    bl_label = "Generate Aircraft"
    bl_description = "Generate PlaneMaker aircraft from Blender meshes"

    def execute(self, context):
        props = context.scene.cis_pm

        # Validate collection
        coll = props.source_collection
        if coll is None:
            self.report({"ERROR"}, "Source Collection is not set")
            return {"CANCELLED"}

        visible_meshes = [
            obj
            for obj in coll.objects
            if obj.type == "MESH" and not obj.hide_get()
        ]
        if not visible_meshes:
            self.report(
                {"ERROR"},
                "No visible mesh objects found in the Source Collection",
            )
            return {"CANCELLED"}

        mode = props.aircraft_mode

        # Resolve file paths depending on mode
        if mode == "MODIFY":
            base_acf_path = bpy.path.abspath(props.existing_acf_filepath)
            if not base_acf_path:
                self.report({"ERROR"}, "Existing aircraft (.acf) is not set")
                return {"CANCELLED"}

            if not os.path.isfile(base_acf_path):
                self.report({"ERROR"}, f"File not found: {base_acf_path}")
                return {"CANCELLED"}

            # Create backup: aircraft_bak.acf next to original
            backup_path = self._make_backup_path(base_acf_path)
            try:
                shutil.copy2(base_acf_path, backup_path)
            except Exception as e:
                self.report({"ERROR"}, f"Could not create backup: {e}")
                return {"CANCELLED"}

            output_acf_path = base_acf_path
            template_acf_path = base_acf_path  # base content is same file

        else:  # NEW
            # Template is internal and hardcoded
            template_acf_path = TEMPLATE_ACF_PATH
            if not os.path.isfile(template_acf_path):
                self.report(
                    {"ERROR"},
                    f"Template .acf not found at:\n{template_acf_path}",
                )
                return {"CANCELLED"}

            new_name = props.new_acf_filename.strip()
            if not new_name:
                self.report({"ERROR"}, "New aircraft filename is empty")
                return {"CANCELLED"}

            output_dir = bpy.path.abspath(props.output_dir)
            if not output_dir:
                self.report({"ERROR"}, "Output folder is not set")
                return {"CANCELLED"}

            os.makedirs(output_dir, exist_ok=True)

            if not new_name.lower().endswith(".acf"):
                new_name += ".acf"

            output_acf_path = os.path.join(output_dir, new_name)
            base_acf_path = template_acf_path

        if props.verbose_log:
            self.report({"INFO"}, f"Mode: {mode}")
            self.report({"INFO"}, f"Base ACF: {base_acf_path}")
            self.report({"INFO"}, f"Output ACF: {output_acf_path}")
            self.report({"INFO"}, f"Dihedral: {props.dihedral_angle}")
            self.report(
                {"INFO"},
                f"Meshes: {', '.join(obj.name for obj in visible_meshes)}",
            )

        # TODO: call your existing core generator here
        try:
            run_generator(
                base_acf_path=base_acf_path,
                output_acf_path=output_acf_path,
                meshes=visible_meshes,
                dihedral_angle=props.dihedral_angle,
                verbose=props.verbose_log,
            )
        except NameError:
            # You haven't hooked in the core PM logic yet
            self.report(
                {"WARNING"},
                "run_generator() not implemented yet; wiring is in place",
            )
            return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Generation failed: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Aircraft written to: {output_acf_path}")
        return {"FINISHED"}

    @staticmethod
    def _make_backup_path(base_path: str) -> str:
        root, ext = os.path.splitext(base_path)
        return f"{root}_bak{ext}"


classes = (
    CIS_PM_Properties,
    CIS_PT_PMGenerator,
    CIS_PM_OT_Generate,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.cis_pm = bpy.props.PointerProperty(
        type=CIS_PM_Properties
    )


def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Scene.cis_pm

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
