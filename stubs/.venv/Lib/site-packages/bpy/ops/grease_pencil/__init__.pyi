import typing
import collections.abc
import typing_extensions
import bpy._typing.rna_enums
import bpy.ops.transform
import bpy.types

def brush_stroke(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
    | None = None,
    mode: typing.Literal["NORMAL", "INVERT", "SMOOTH"] | None = "NORMAL",
):
    """Draw a new stroke in the active Grease Pencil object

        :type execution_context: int | str | None
        :type undo: bool | None
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] | None
        :param mode: Stroke Mode, Action taken when a paint stroke is made

    NORMAL
    Regular -- Apply brush normally.

    INVERT
    Invert -- Invert action of brush for duration of stroke.

    SMOOTH
    Smooth -- Switch brush to smooth mode for duration of stroke.
        :type mode: typing.Literal['NORMAL','INVERT','SMOOTH'] | None
    """

def caps_set(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    type: typing.Literal["ROUND", "FLAT", "START", "END"] | None = "ROUND",
):
    """Change curve caps mode (rounded or flat)

        :type execution_context: int | str | None
        :type undo: bool | None
        :param type: Type

    ROUND
    Rounded -- Set as default rounded.

    FLAT
    Flat.

    START
    Toggle Start.

    END
    Toggle End.
        :type type: typing.Literal['ROUND','FLAT','START','END'] | None
    """

def clean_loose(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    limit: int | None = 1,
):
    """Remove loose points

    :type execution_context: int | str | None
    :type undo: bool | None
    :param limit: Limit, Number of points to consider stroke as loose
    :type limit: int | None
    """

def copy(execution_context: int | str | None = None, undo: bool | None = None):
    """Copy the selected Grease Pencil points or strokes to the internal clipboard

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def cyclical_set(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    type: typing.Literal["CLOSE", "OPEN", "TOGGLE"] | None = "TOGGLE",
):
    """Close or open the selected stroke adding a segment from last to first point

    :type execution_context: int | str | None
    :type undo: bool | None
    :param type: Type
    :type type: typing.Literal['CLOSE','OPEN','TOGGLE'] | None
    """

def delete(execution_context: int | str | None = None, undo: bool | None = None):
    """Delete selected strokes or points

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def delete_frame(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    type: typing.Literal["ACTIVE_FRAME", "ALL_FRAMES"] | None = "ACTIVE_FRAME",
):
    """Delete Grease Pencil Frame(s)

        :type execution_context: int | str | None
        :type undo: bool | None
        :param type: Type, Method used for deleting Grease Pencil frames

    ACTIVE_FRAME
    Active Frame -- Deletes current frame in the active layer.

    ALL_FRAMES
    All Active Frames -- Delete active frames for all layers.
        :type type: typing.Literal['ACTIVE_FRAME','ALL_FRAMES'] | None
    """

def dissolve(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    type: typing.Literal["POINTS", "BETWEEN", "UNSELECT"] | None = "POINTS",
):
    """Delete selected points without splitting strokes

        :type execution_context: int | str | None
        :type undo: bool | None
        :param type: Type, Method used for dissolving stroke points

    POINTS
    Dissolve -- Dissolve selected points.

    BETWEEN
    Dissolve Between -- Dissolve points between selected points.

    UNSELECT
    Dissolve Unselect -- Dissolve all unselected points.
        :type type: typing.Literal['POINTS','BETWEEN','UNSELECT'] | None
    """

def duplicate(execution_context: int | str | None = None, undo: bool | None = None):
    """Duplicate the selected points

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def duplicate_move(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    GREASE_PENCIL_OT_duplicate: typing.Any | None = None,
    TRANSFORM_OT_translate: bpy.ops.transform.translate | None = None,
):
    """Make copies of the selected Grease Pencil strokes and move them

    :type execution_context: int | str | None
    :type undo: bool | None
    :param GREASE_PENCIL_OT_duplicate: Duplicate, Duplicate the selected points
    :type GREASE_PENCIL_OT_duplicate: typing.Any | None
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: bpy.ops.transform.translate | None
    """

def extrude(execution_context: int | str | None = None, undo: bool | None = None):
    """Extrude the selected points

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def extrude_move(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    GREASE_PENCIL_OT_extrude: typing.Any | None = None,
    TRANSFORM_OT_translate: bpy.ops.transform.translate | None = None,
):
    """Extrude selected points and move them

    :type execution_context: int | str | None
    :type undo: bool | None
    :param GREASE_PENCIL_OT_extrude: Extrude Stroke Points, Extrude the selected points
    :type GREASE_PENCIL_OT_extrude: typing.Any | None
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: bpy.ops.transform.translate | None
    """

def fill(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    on_back: bool | None = False,
    invert: bool | None = False,
    precision: bool | None = False,
):
    """Fill with color the shape formed by strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param on_back: Draw on Back, Send new stroke to back
    :type on_back: bool | None
    :param invert: Invert, Find boundary of unfilled instead of filled regions
    :type invert: bool | None
    :param precision: Precision, Use precision movement for extension lines
    :type precision: bool | None
    """

def insert_blank_frame(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    all_layers: bool | None = False,
    duration: int | None = 0,
):
    """Insert a blank frame on the current scene frame

    :type execution_context: int | str | None
    :type undo: bool | None
    :param all_layers: All Layers, Insert a blank frame in all editable layers
    :type all_layers: bool | None
    :param duration: Duration
    :type duration: int | None
    """

def layer_active(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    layer: int | None = 0,
):
    """Set the active Grease Pencil layer

    :type execution_context: int | str | None
    :type undo: bool | None
    :param layer: Grease Pencil Layer
    :type layer: int | None
    """

def layer_add(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    new_layer_name: str = "Layer",
):
    """Add a new Grease Pencil layer in the active object

    :type execution_context: int | str | None
    :type undo: bool | None
    :param new_layer_name: Name, Name of the new layer
    :type new_layer_name: str
    """

def layer_duplicate(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    empty_keyframes: bool | None = False,
):
    """Make a copy of the active Grease Pencil layer

    :type execution_context: int | str | None
    :type undo: bool | None
    :param empty_keyframes: Empty Keyframes, Add Empty Keyframes
    :type empty_keyframes: bool | None
    """

def layer_group_add(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    new_layer_group_name: str = "",
):
    """Add a new Grease Pencil layer group in the active object

    :type execution_context: int | str | None
    :type undo: bool | None
    :param new_layer_group_name: Name, Name of the new layer group
    :type new_layer_group_name: str
    """

def layer_group_remove(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    keep_children: bool | None = False,
):
    """Remove Grease Pencil layer group in the active object

    :type execution_context: int | str | None
    :type undo: bool | None
    :param keep_children: Keep children nodes, Keep the children nodes of the group and only delete the group itself
    :type keep_children: bool | None
    """

def layer_hide(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    unselected: bool | None = False,
):
    """Hide selected/unselected Grease Pencil layers

    :type execution_context: int | str | None
    :type undo: bool | None
    :param unselected: Unselected, Hide unselected rather than selected layers
    :type unselected: bool | None
    """

def layer_isolate(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    affect_visibility: bool | None = False,
):
    """Make only active layer visible/editable

    :type execution_context: int | str | None
    :type undo: bool | None
    :param affect_visibility: Affect Visibility, Also affect the visibility
    :type affect_visibility: bool | None
    """

def layer_lock_all(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    lock: bool | None = True,
):
    """Lock all Grease Pencil layers to prevent them from being accidentally modified

    :type execution_context: int | str | None
    :type undo: bool | None
    :param lock: Lock Value, Lock/Unlock all layers
    :type lock: bool | None
    """

def layer_mask_add(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    name: str = "",
):
    """Add new layer as masking

    :type execution_context: int | str | None
    :type undo: bool | None
    :param name: Layer, Name of the layer
    :type name: str
    """

def layer_mask_remove(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Remove Layer Mask

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def layer_mask_reorder(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    direction: typing.Literal["UP", "DOWN"] | None = "UP",
):
    """Reorder the active Grease Pencil mask layer up/down in the list

    :type execution_context: int | str | None
    :type undo: bool | None
    :param direction: Direction
    :type direction: typing.Literal['UP','DOWN'] | None
    """

def layer_remove(execution_context: int | str | None = None, undo: bool | None = None):
    """Remove the active Grease Pencil layer

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def layer_reorder(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    target_layer_name: str = "Layer",
    location: typing.Literal["ABOVE", "BELOW"] | None = "ABOVE",
):
    """Reorder the active Grease Pencil layer

    :type execution_context: int | str | None
    :type undo: bool | None
    :param target_layer_name: Target Name, Name of the target layer
    :type target_layer_name: str
    :param location: Location
    :type location: typing.Literal['ABOVE','BELOW'] | None
    """

def layer_reveal(execution_context: int | str | None = None, undo: bool | None = None):
    """Show all Grease Pencil layers

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def material_copy_to_object(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    only_active: bool | None = True,
):
    """Append Materials of the active Grease Pencil to other object

    :type execution_context: int | str | None
    :type undo: bool | None
    :param only_active: Only Active, Append only active material, uncheck to append all materials
    :type only_active: bool | None
    """

def material_hide(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    invert: bool | None = False,
):
    """Hide active/inactive Grease Pencil material(s)

    :type execution_context: int | str | None
    :type undo: bool | None
    :param invert: Invert, Hide inactive materials instead of the active one
    :type invert: bool | None
    """

def material_lock_all(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Lock all Grease Pencil materials to prevent them from being accidentally modified

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def material_lock_unselected(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Lock any material not used in any selected stroke

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def material_lock_unused(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Lock and hide any material not used

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def material_reveal(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Unhide all hidden Grease Pencil materials

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def material_select(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    deselect: bool | None = False,
):
    """Select/Deselect all Grease Pencil strokes using current material

    :type execution_context: int | str | None
    :type undo: bool | None
    :param deselect: Deselect, Unselect strokes
    :type deselect: bool | None
    """

def material_unlock_all(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Unlock all Grease Pencil materials so that they can be edited

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def move_to_layer(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    target_layer_name: str = "Layer",
    add_new_layer: bool | None = False,
):
    """Move selected strokes to another layer

    :type execution_context: int | str | None
    :type undo: bool | None
    :param target_layer_name: Name, Target Grease Pencil Layer
    :type target_layer_name: str
    :param add_new_layer: New Layer, Move selection to a new layer
    :type add_new_layer: bool | None
    """

def paste(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    paste_back: bool | None = False,
):
    """Paste Grease Pencil points or strokes from the internal clipboard to the active layer

    :type execution_context: int | str | None
    :type undo: bool | None
    :param paste_back: Paste on Back, Add pasted strokes behind all strokes
    :type paste_back: bool | None
    """

def primitive_arc(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    subdivision: int | None = 62,
    type: typing.Literal["BOX", "LINE", "POLYLINE", "CIRCLE", "ARC", "CURVE"]
    | None = "ARC",
):
    """Create predefined grease pencil stroke arcs

    :type execution_context: int | str | None
    :type undo: bool | None
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: int | None
    :param type: Type, Type of shape
    :type type: typing.Literal['BOX','LINE','POLYLINE','CIRCLE','ARC','CURVE'] | None
    """

def primitive_box(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    subdivision: int | None = 3,
    type: typing.Literal["BOX", "LINE", "POLYLINE", "CIRCLE", "ARC", "CURVE"]
    | None = "BOX",
):
    """Create predefined grease pencil stroke boxes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: int | None
    :param type: Type, Type of shape
    :type type: typing.Literal['BOX','LINE','POLYLINE','CIRCLE','ARC','CURVE'] | None
    """

def primitive_circle(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    subdivision: int | None = 94,
    type: typing.Literal["BOX", "LINE", "POLYLINE", "CIRCLE", "ARC", "CURVE"]
    | None = "CIRCLE",
):
    """Create predefined grease pencil stroke circles

    :type execution_context: int | str | None
    :type undo: bool | None
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: int | None
    :param type: Type, Type of shape
    :type type: typing.Literal['BOX','LINE','POLYLINE','CIRCLE','ARC','CURVE'] | None
    """

def primitive_curve(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    subdivision: int | None = 62,
    type: typing.Literal["BOX", "LINE", "POLYLINE", "CIRCLE", "ARC", "CURVE"]
    | None = "CURVE",
):
    """Create predefined grease pencil stroke curve shapes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: int | None
    :param type: Type, Type of shape
    :type type: typing.Literal['BOX','LINE','POLYLINE','CIRCLE','ARC','CURVE'] | None
    """

def primitive_line(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    subdivision: int | None = 6,
    type: typing.Literal["BOX", "LINE", "POLYLINE", "CIRCLE", "ARC", "CURVE"]
    | None = "LINE",
):
    """Create predefined grease pencil stroke lines

    :type execution_context: int | str | None
    :type undo: bool | None
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: int | None
    :param type: Type, Type of shape
    :type type: typing.Literal['BOX','LINE','POLYLINE','CIRCLE','ARC','CURVE'] | None
    """

def primitive_polyline(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    subdivision: int | None = 6,
    type: typing.Literal["BOX", "LINE", "POLYLINE", "CIRCLE", "ARC", "CURVE"]
    | None = "POLYLINE",
):
    """Create predefined grease pencil stroke polylines

    :type execution_context: int | str | None
    :type undo: bool | None
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: int | None
    :param type: Type, Type of shape
    :type type: typing.Literal['BOX','LINE','POLYLINE','CIRCLE','ARC','CURVE'] | None
    """

def reorder(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    direction: typing.Literal["TOP", "UP", "DOWN", "BOTTOM"] | None = "TOP",
):
    """Change the display order of the selected strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param direction: Direction
    :type direction: typing.Literal['TOP','UP','DOWN','BOTTOM'] | None
    """

def sculpt_paint(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
    | None = None,
    mode: typing.Literal["NORMAL", "INVERT", "SMOOTH"] | None = "NORMAL",
):
    """Draw a new stroke in the active Grease Pencil object

        :type execution_context: int | str | None
        :type undo: bool | None
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] | None
        :param mode: Stroke Mode, Action taken when a paint stroke is made

    NORMAL
    Regular -- Apply brush normally.

    INVERT
    Invert -- Invert action of brush for duration of stroke.

    SMOOTH
    Smooth -- Switch brush to smooth mode for duration of stroke.
        :type mode: typing.Literal['NORMAL','INVERT','SMOOTH'] | None
    """

def select_all(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    action: typing.Literal["TOGGLE", "SELECT", "DESELECT", "INVERT"] | None = "TOGGLE",
):
    """(De)select all visible strokes

        :type execution_context: int | str | None
        :type undo: bool | None
        :param action: Action, Selection action to execute

    TOGGLE
    Toggle -- Toggle selection for all elements.

    SELECT
    Select -- Select all elements.

    DESELECT
    Deselect -- Deselect all elements.

    INVERT
    Invert -- Invert selection of all elements.
        :type action: typing.Literal['TOGGLE','SELECT','DESELECT','INVERT'] | None
    """

def select_alternate(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    deselect_ends: bool | None = False,
):
    """Select alternated points in strokes with already selected points

    :type execution_context: int | str | None
    :type undo: bool | None
    :param deselect_ends: Deselect Ends, (De)select the first and last point of each stroke
    :type deselect_ends: bool | None
    """

def select_ends(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    amount_start: int | None = 0,
    amount_end: int | None = 1,
):
    """Select end points of strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param amount_start: Amount Start, Number of points to select from the start
    :type amount_start: int | None
    :param amount_end: Amount End, Number of points to select from the end
    :type amount_end: int | None
    """

def select_less(execution_context: int | str | None = None, undo: bool | None = None):
    """Shrink the selection by one point

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def select_linked(execution_context: int | str | None = None, undo: bool | None = None):
    """Select all points in curves with any point selection

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def select_more(execution_context: int | str | None = None, undo: bool | None = None):
    """Grow the selection by one point

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def select_random(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    ratio: float | None = 0.5,
    seed: int | None = 0,
    action: typing.Literal["SELECT", "DESELECT"] | None = "SELECT",
):
    """Selects random points from the current strokes selection

        :type execution_context: int | str | None
        :type undo: bool | None
        :param ratio: Ratio, Portion of items to select randomly
        :type ratio: float | None
        :param seed: Random Seed, Seed for the random number generator
        :type seed: int | None
        :param action: Action, Selection action to execute

    SELECT
    Select -- Select all elements.

    DESELECT
    Deselect -- Deselect all elements.
        :type action: typing.Literal['SELECT','DESELECT'] | None
    """

def separate(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    mode: typing.Literal["SELECTED", "MATERIAL", "LAYER"] | None = "SELECTED",
):
    """Separate the selected geometry into a new grease pencil object

        :type execution_context: int | str | None
        :type undo: bool | None
        :param mode: Mode

    SELECTED
    Selection -- Separate selected geometry.

    MATERIAL
    By Material -- Separate by material.

    LAYER
    By Layer -- Separate by layer.
        :type mode: typing.Literal['SELECTED','MATERIAL','LAYER'] | None
    """

def set_active_material(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Set the selected stroke material as the active material

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def set_material(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    slot: str | None = "DEFAULT",
):
    """Set active material

    :type execution_context: int | str | None
    :type undo: bool | None
    :param slot: Material Slot
    :type slot: str | None
    """

def set_selection_mode(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    mode: bpy._typing.rna_enums.GreasePencilSelectmodeItems | None = "POINT",
):
    """Change the selection mode for Grease Pencil strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param mode: Mode
    :type mode: bpy._typing.rna_enums.GreasePencilSelectmodeItems | None
    """

def set_uniform_opacity(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    opacity: float | None = 1.0,
):
    """Set all stroke points to same opacity

    :type execution_context: int | str | None
    :type undo: bool | None
    :param opacity: Opacity
    :type opacity: float | None
    """

def set_uniform_thickness(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    thickness: float | None = 0.1,
):
    """Set all stroke points to same thickness

    :type execution_context: int | str | None
    :type undo: bool | None
    :param thickness: Thickness, Thickness
    :type thickness: float | None
    """

def snap_cursor_to_selected(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Snap cursor to center of selected points

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def snap_to_cursor(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    use_offset: bool | None = True,
):
    """Snap selected points/strokes to the cursor

    :type execution_context: int | str | None
    :type undo: bool | None
    :param use_offset: With Offset, Offset the entire stroke instead of selected points only
    :type use_offset: bool | None
    """

def snap_to_grid(execution_context: int | str | None = None, undo: bool | None = None):
    """Snap selected points to the nearest grid points

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def stroke_cutter(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath] | None = None,
):
    """Delete stroke points in between intersecting strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param path: Path
    :type path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath] | None
    """

def stroke_material_set(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    material: str = "",
):
    """Assign the active material slot to the selected strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param material: Material, Name of the material
    :type material: str
    """

def stroke_merge_by_distance(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    threshold: float | None = 0.001,
    use_unselected: bool | None = False,
):
    """Merge points by distance

    :type execution_context: int | str | None
    :type undo: bool | None
    :param threshold: Threshold
    :type threshold: float | None
    :param use_unselected: Unselected, Use whole stroke, not only selected points
    :type use_unselected: bool | None
    """

def stroke_simplify(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    factor: float | None = 0.01,
):
    """Simplify selected strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param factor: Factor
    :type factor: float | None
    """

def stroke_smooth(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    iterations: int | None = 10,
    factor: float | None = 1.0,
    smooth_ends: bool | None = False,
    keep_shape: bool | None = False,
    smooth_position: bool | None = True,
    smooth_radius: bool | None = True,
    smooth_opacity: bool | None = False,
):
    """Smooth selected strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    :param iterations: Iterations
    :type iterations: int | None
    :param factor: Factor
    :type factor: float | None
    :param smooth_ends: Smooth Endpoints
    :type smooth_ends: bool | None
    :param keep_shape: Keep Shape
    :type keep_shape: bool | None
    :param smooth_position: Position
    :type smooth_position: bool | None
    :param smooth_radius: Radius
    :type smooth_radius: bool | None
    :param smooth_opacity: Opacity
    :type smooth_opacity: bool | None
    """

def stroke_subdivide(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    number_cuts: int | None = 1,
    only_selected: bool | None = True,
):
    """Subdivide between continuous selected points of the stroke adding a point half way between them

    :type execution_context: int | str | None
    :type undo: bool | None
    :param number_cuts: Number of Cuts
    :type number_cuts: int | None
    :param only_selected: Selected Points, Smooth only selected points in the stroke
    :type only_selected: bool | None
    """

def stroke_subdivide_smooth(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    GREASE_PENCIL_OT_stroke_subdivide: typing.Any | None = None,
    GREASE_PENCIL_OT_stroke_smooth: typing.Any | None = None,
):
    """Subdivide strokes and smooth them

    :type execution_context: int | str | None
    :type undo: bool | None
    :param GREASE_PENCIL_OT_stroke_subdivide: Subdivide Stroke, Subdivide between continuous selected points of the stroke adding a point half way between them
    :type GREASE_PENCIL_OT_stroke_subdivide: typing.Any | None
    :param GREASE_PENCIL_OT_stroke_smooth: Smooth Stroke, Smooth selected strokes
    :type GREASE_PENCIL_OT_stroke_smooth: typing.Any | None
    """

def stroke_switch_direction(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Change direction of the points of the selected strokes

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def weight_brush_stroke(
    execution_context: int | str | None = None,
    undo: bool | None = None,
    /,
    *,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
    | None = None,
    mode: typing.Literal["NORMAL", "INVERT", "SMOOTH"] | None = "NORMAL",
):
    """Draw weight on stroke points in the active Grease Pencil object

        :type execution_context: int | str | None
        :type undo: bool | None
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] | None
        :param mode: Stroke Mode, Action taken when a paint stroke is made

    NORMAL
    Regular -- Apply brush normally.

    INVERT
    Invert -- Invert action of brush for duration of stroke.

    SMOOTH
    Smooth -- Switch brush to smooth mode for duration of stroke.
        :type mode: typing.Literal['NORMAL','INVERT','SMOOTH'] | None
    """

def weight_sample(execution_context: int | str | None = None, undo: bool | None = None):
    """Set the weight of the Draw tool to the weight of the vertex under the mouse cursor

    :type execution_context: int | str | None
    :type undo: bool | None
    """

def weight_toggle_direction(
    execution_context: int | str | None = None, undo: bool | None = None
):
    """Toggle Add/Subtract for the weight paint draw tool

    :type execution_context: int | str | None
    :type undo: bool | None
    """
