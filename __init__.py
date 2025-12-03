bl_info = {
    "name": "CIS_PM_Generator",
    "author": "Capt. Iceman / CIS",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "Properties > Scene",
    "description": "Generate X-Plane .acf flight model data from Blender collections",
    "category": "Import-Export",
}

import bpy
from bpy.props import (
    EnumProperty,
    FloatProperty,
    PointerProperty,
    StringProperty,
    BoolProperty,
)
from bpy.types import Panel, Operator


def cis_pm_mode_items(self, context):
    return [
        ("NEW", "New Aircraft", "Create a new .acf file from templates"),
        ("MODIFY", "Modify Existing", "Modify an existing .acf file"),
    ]


class CIS_PM_Properties(bpy.types.PropertyGroup):
    # Collection that holds bodies, wings, stabs, cowlings, empties, etc.
    collection: PointerProperty(
        name="Source Collection",
        description="Collection containing meshes (bodies, wings, stabs, cowlings, etc.) and empties used to drive the .acf",
        type=bpy.types.Collection,
    )

    # New vs Modify
    mode: EnumProperty(
        name="Mode",
        description="Create a new aircraft or modify an existing .acf",
        items=cis_pm_mode_items,
        default="NEW",
    )

    # For NEW aircraft
    new_acf_directory: StringProperty(
        name="Output Folder",
        description="Folder where the new .acf file will be written",
        subtype="DIR_PATH",
    )

    new_acf_name: StringProperty(
        name="New .acf Name",
        description="File name for the new .acf (e.g. CIS_Chieftain.acf)",
        default="CIS_NewAircraft.acf",
    )

    # For MODIFY existing aircraft
    existing_acf_path: StringProperty(
        name="Existing .acf",
        description="Path to an existing .acf file to modify",
        subtype="FILE_PATH",
    )

    # Wing / geometry params
    wing_dihedral_deg: FloatProperty(
        name="Wing Dihedral",
        description="Design dihedral angle applied to wings and cowlings (deg)",
        default=5.0,
        soft_min=-10.0,
        soft_max=15.0,
        unit="ROTATION",
        subtype="ANGLE",
    )

    # Future: templates, etc.
    show_advanced: BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False,
    )

    body_template_path: StringProperty(
        name="Body Template",
        description="Path to body_block_template_zeroed.txt (optional, overrides built-in)",
        subtype="FILE_PATH",
    )

    wing_template_path: StringProperty(
        name="Wing Template",
        description="Path to wing_block_template_zeroed.txt (optional, overrides built-in)",
        subtype="FILE_PATH",
    )

    acf_template_path: StringProperty(
        name="ACF Template",
        description="Optional path to acfnew.acf template (for NEW mode)",
        subtype="FILE_PATH",
    )


class CIS_OT_PM_Generate(Operator):
    bl_idname = "cis_pm.generate_acf"
    bl_label = "Generate .acf Flight Model"
    bl_description = "Export meshes in the selected collection to bodies/wings and write .acf"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        props = scene.cis_pm

        if props.collection is None:
            self.report({"ERROR"}, "Select a source collection first.")
            return {"CANCELLED"}

        if props.mode == "NEW":
            if not props.new_acf_directory or not props.new_acf_name:
                self.report({"ERROR"}, "Specify output folder and .acf name for NEW mode.")
                return {"CANCELLED"}
        else:  # MODIFY
            if not props.existing_acf_path:
                self.report({"ERROR"}, "Specify an existing .acf file to modify.")
                return {"CANCELLED"}

        # Placeholder – here we will later plug in cis_bodies2pm / cis_wings2pm logic
        self.report(
            {"INFO"},
            f"[CIS_PM_Generator] Would process collection '{props.collection.name}' in {props.mode} mode."
        )
        print("CIS_PM_Generator: stub operator called")
        print("  Collection:", props.collection.name if props.collection else "None")
        print("  Mode:", props.mode)
        print("  New ACF dir/name:", props.new_acf_directory, props.new_acf_name)
        print("  Existing ACF:", props.existing_acf_path)
        print("  Wing dihedral (deg):", props.wing_dihedral_deg)

        return {"FINISHED"}


class CIS_PT_PM_Generator(Panel):
    bl_idname = "SCENE_PT_cis_pm_generator"
    bl_label = "CIS_PM_Generator"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.cis_pm

        # Collection selector
        col = layout.column(align=True)
        col.label(text="Source Collection:")
        col.prop(props, "collection", text="")

        layout.separator()

        # Mode: New vs Modify
        col = layout.column(align=True)
        col.label(text="ACF Mode:")
        col.prop(props, "mode", expand=True)

        # Mode-specific settings
        if props.mode == "NEW":
            box = layout.box()
            box.label(text="New Aircraft Settings")
            box.prop(props, "new_acf_directory")
            box.prop(props, "new_acf_name")
            box.prop(props, "acf_template_path")
        else:
            box = layout.box()
            box.label(text="Modify Existing Aircraft")
            box.prop(props, "existing_acf_path")

        layout.separator()

        # Wing / geometry block
        col = layout.column(align=True)
        col.label(text="Wing / Geometry:")
        col.prop(props, "wing_dihedral_deg")

        layout.separator()

        # Advanced templates section
        row = layout.row()
        row.prop(props, "show_advanced", icon="PREFERENCES", toggle=True)

        if props.show_advanced:
            box = layout.box()
            box.label(text="Templates (Optional Overrides)")
            box.prop(props, "body_template_path")
            box.prop(props, "wing_template_path")

        layout.separator()

        # Main action button
        layout.operator(CIS_OT_PM_Generate.bl_idname, icon="FILE_TICK")


classes = (
    CIS_PM_Properties,
    CIS_OT_PM_Generate,
    CIS_PT_PM_Generator,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.cis_pm = PointerProperty(type=CIS_PM_Properties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.cis_pm


if __name__ == "__main__":
    register()
