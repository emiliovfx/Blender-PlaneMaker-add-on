# File: cis_pm_addon/cis_geom_builder.py
"""
cis_geom_builder — STUBS (interfaces only, no implementation)

Purpose
-------
Define public entry points to bootstrap / manage a basic flight-model scene structure
and create placeholder geometry for bodies and wings. Landing gear is a placeholder
in this scope (API only). This module **does not** write ACF or OBJ; it only creates
or organizes Blender data (collections, empties/meshes) and returns handles.

Conventions
-----------
- Coordinate space: Blender world, meters. (OBJ export adapter handles -Z forward, +Y up.)
- Units in API: accept "m" or "ft"; **convert to Blender meters** accounting for the scene unit setup.
- Triangulation is handled by the virtual-OBJ adapter; do not triangulate here.
- Logging: call the provided `log_fn` only; do not import the logger directly.

Collections (required)
----------------------
Create/ensure a **FlightModel** root collection, then create these **as direct children**:

FlightModel (root)
├── Bodies
├── Wings
├── LandingGear
├── CG
├── FuelTanks
└── Payload

Geometry stubs in this file
---------------------------
- Fuselage (Bodies): cylinder, 16 verts, cap fill: triangle fan
- Wings (Wings): three planes — Wing1, Horiz_Stab, Vert_Stab
  - Wing1: plane size = wingspan; after creation, Edit Mode: scale X by 0.5
  - Horiz_Stab: same process as Wing1
  - Vert_Stab: same as Wing1 but after X-scale 0.5, rotate Y +90°
- Landing gear: **placeholder only** (API defined, no geometry yet)

IMPORTANT: This is a stub module. All public functions raise NotImplementedError.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple, TypedDict, Literal
import bpy

# -------------------------
# Public constants
# -------------------------

DEFAULT_ROOT_NAME = "FlightModel"

COLLECTION_NAMES = {
    "bodies": "Bodies",
    "wings": "Wings",
    "gear": "LandingGear",
    "cg": "CG",
    "fuel": "FuelTanks",
    "payload": "Payload",
}

Unit = Literal["m", "ft"]  # user-facing unit tokens


class SkeletonMap(TypedDict):
    root: bpy.types.Collection
    bodies: bpy.types.Collection
    wings: bpy.types.Collection
    gear: bpy.types.Collection
    cg: bpy.types.Collection
    fuel: bpy.types.Collection
    payload: bpy.types.Collection


class FuselageParams(TypedDict, total=False):
    """Parameters for fuselage placeholder."""
    units: Unit           # "m" or "ft" (default: "m")
    radius: float         # radius in units
    depth: float          # axial length in units
    segments: int         # cylinder sides (default: 16; keep ≥16)


class WingsParams(TypedDict, total=False):
    """Parameters for wings placeholders."""
    units: Unit           # "m" or "ft" (default: "m")
    wingspan: float       # span in units (applies to Wing1 & Horiz_Stab)
    vert_stab_span: float # optional; if missing, reuse wingspan


class BuildParams(TypedDict, total=False):
    """Aggregate parameters for all placeholders."""
    fuselage: FuselageParams
    wings: WingsParams
    create_placeholders: bool  # default True; if False, only ensure collections


# -------------------------
# Units: scene detection & conversion (stubs)
# -------------------------

def get_scene_units(context: bpy.types.Context) -> Dict[str, object]:
    """
    Inspect Blender's scene unit settings to guide conversion.

    Returns
    -------
    dict
        {
          "system": scene.unit_settings.system,     # 'NONE' | 'METRIC' | 'IMPERIAL'
          "scale_length": scene.unit_settings.scale_length,  # float
          "length_unit": scene.unit_settings.length_unit,    # e.g., 'METERS', 'CENTIMETERS', 'FEET', etc.
        }

    Notes
    -----
    - **Contract only**: implementation will read from `context.scene.unit_settings`.
    - Callers should rely on `convert_user_length_to_blender_meters(...)` for actual conversion.
    """
    raise NotImplementedError("stub")


def convert_user_length_to_blender_meters(
    value: float,
    units: Unit,
    context: bpy.types.Context,
) -> float:
    """
    Convert a user-specified length (in 'm' or 'ft') into **Blender meters** for API calls.

    Contracts & Rules
    -----------------
    - If `units == 'm'`: interpret `value` as physical meters.
    - If `units == 'ft'`: convert using 1 ft = 0.3048 m.
    - Respect scene scaling: API calls (e.g., primitive add) expect values in **scene length units**.
      The implementation must account for `scene.unit_settings.scale_length` so that the resulting
      object measures the intended **physical** size when inspected in the viewport.

    Returns
    -------
    float
        Value to pass to Blender operators (in scene-consistent meters).

    TODO
    ----
    - Validate operator expectations across Blender versions (4.5+): whether parameters are interpreted
      as raw meters or scene-scaled units; adjust the scale application accordingly.
    """
    raise NotImplementedError("stub")


# -------------------------
# Public API — root & skeleton
# -------------------------

def ensure_flight_model_root(
    context: bpy.types.Context,
    *,
    name: str = DEFAULT_ROOT_NAME,
    log_fn: Callable[[str], None] = lambda msg: None,
) -> bpy.types.Collection:
    """
    Ensure a **FlightModel** root collection exists (create if missing).

    Behavior (to implement):
    - Look for a collection named `name` at the scene level.
    - If not found, create it and link it to the active scene's master collection.
    - Return the collection handle.

    Parameters
    ----------
    context : bpy.types.Context
    name : str
        Name of the root collection (default: 'FlightModel').
    log_fn : Callable[[str], None]
        Logger callback.

    Returns
    -------
    bpy.types.Collection
        The ensured/created FlightModel root collection.

    Raises
    ------
    RuntimeError
        If the collection cannot be created or linked.
    """
    raise NotImplementedError("stub")


def create_flight_model_skeleton(
    context: bpy.types.Context,
    root_collection: bpy.types.Collection,
    *,
    log_fn: Callable[[str], None] = lambda msg: None,
) -> SkeletonMap:
    """
    Ensure the required subcollections exist **as direct children of** `root_collection` (the FlightModel).

    Creates (if missing) child collections named exactly as in COLLECTION_NAMES **and links them
    under `root_collection`**. Does not link/unlink scenes; only ensures the collection tree under
    the provided FlightModel parent.

    Parameters
    ----------
    context : bpy.types.Context
        Active Blender context.
    root_collection : bpy.types.Collection
        The user-selected/ensured FlightModel collection **that will own the subcollections**.
    log_fn : Callable[[str], None]
        Callback for logging; use add-on's shared logger.

    Returns
    -------
    SkeletonMap
        Mapping of canonical collection names to bpy Collection handles, with `root` equal
        to the given FlightModel collection, and all other collections parented under it.

    Raises
    ------
    ValueError
        If `root_collection` is invalid or not linked into the current file.

    Notes
    -----
    - No geometry is created here.
    - Names are stable and must not be localized.
    - Parent/child relation is explicit: all collections are subcollections *of FlightModel*.
    """
    raise NotImplementedError("stub")


# -------------------------
# Public API — placeholders
# -------------------------

def create_fuselage_cylinder(
    context: bpy.types.Context,
    target_collection: bpy.types.Collection,
    *,
    units: Unit = "m",
    radius: float = 1.0,
    depth: float = 4.0,
    segments: int = 16,
    name: str = "Fuselage",
    log_fn: Callable[[str], None] = lambda msg: None,
) -> bpy.types.Object:
    """
    Create a fuselage placeholder as a cylinder mesh in `target_collection` (expected: **Bodies**).

    Specification (to implement):
    - Cylinder with `segments` sides, end caps set to **triangle fan**.
    - Dimensions use `units` ("m" or "ft"); convert to Blender meters via
      `convert_user_length_to_blender_meters(...)` (respecting scene unit scale).
    - After creation:
        1) Enter Edit Mode, select all vertices
        2) Apply rotation about **X axis** by **-90 degrees**
        3) Return to Object Mode

    Parameters
    ----------
    context : bpy.types.Context
    target_collection : bpy.types.Collection
        Must be the **Bodies** subcollection under the FlightModel.
    units : Unit
        "m" or "ft" (default: "m").
    radius : float
        Cylinder radius in `units`.
    depth : float
        Cylinder depth/length in `units`.
    segments : int
        Number of radial segments, default 16.
    name : str
        Object name to assign to the created cylinder.
    log_fn : Callable[[str], None]
        Logger callback (no-op in stub).

    Returns
    -------
    bpy.types.Object
        The created object (mesh).

    Raises
    ------
    ValueError
        On invalid params or collection.

    Notes
    -----
    - Keep transforms simple (no parenting/constraints here).
    - Do not triangulate; the export adapter handles triangulation for OBJ.
    """
    raise NotImplementedError("stub")


def create_wing_planes(
    context: bpy.types.Context,
    target_collection: bpy.types.Collection,
    *,
    units: Unit = "m",
    wingspan: float = 10.0,
    vert_stab_span: Optional[float] = None,
    names: Tuple[str, str, str] = ("Wing1", "Horiz_Stab", "Vert_Stab"),
    log_fn: Callable[[str], None] = lambda msg: None,
) -> Dict[str, bpy.types.Object]:
    """
    Create three plane placeholders (Wing1, Horiz_Stab, Vert_Stab) in `target_collection` (expected: **Wings**).

    Specification (to implement):
    - All inputs provided in `units` ("m" or "ft"). Use
      `convert_user_length_to_blender_meters(...)` for sizes and offsets.
    - Planes are created one after another using **Add → Mesh → Plane**:
      1) Wing1
         - Build: plane `size` = wingspan (converted to Blender meters)
         - Align=World; Location X = -wingspan/2 (converted)
         - After creation: Edit Mode → select all → scale X by **0.5** → back to Object Mode
      2) Horiz_Stab
         - Build: same as Wing1 (size = wingspan, X offset = -wingspan/2)
         - After creation: Edit Mode → scale X by **0.5**
      3) Vert_Stab
         - Build: same as Wing1 (unless `vert_stab_span` is provided; then use it)
         - After creation: Edit Mode → scale X by **0.5**, then **rotate Y +90°**
           (back to Object Mode)

    Parameters
    ----------
    context : bpy.types.Context
    target_collection : bpy.types.Collection
        Must be the **Wings** subcollection under the FlightModel.
    units : Unit
        "m" or "ft" (default: "m").
    wingspan : float
        Baseline span in `units` for Wing1 and Horiz_Stab.
    vert_stab_span : Optional[float]
        If provided, overrides Vert_Stab size; else uses `wingspan`.
    names : Tuple[str, str, str]
        Names for (Wing1, Horiz_Stab, Vert_Stab).
    log_fn : Callable[[str], None]
        Logger callback (no-op in stub).

    Returns
    -------
    Dict[str, bpy.types.Object]
        Mapping {"Wing1": obj, "Horiz_Stab": obj, "Vert_Stab": obj}.

    Raises
    ------
    ValueError
        On invalid params or collection.

    Notes
    -----
    - Keep transforms minimal; no parenting/constraints here.
    - Do not triangulate; OBJ adapter handles triangulation later.
    """
    raise NotImplementedError("stub")


# -------------------------
# Public API — aggregate
# -------------------------

def generate_basic_geometry(
    context: bpy.types.Context,
    root_collection: bpy.types.Collection,
    *,
    params: Optional[BuildParams] = None,
    log_fn: Callable[[str], None] = lambda msg: None,
) -> Dict[str, bpy.types.ID]:
    """
    Aggregate entry point: ensure **FlightModel** root + skeleton and (optionally) create placeholders.

    Typical sequence (to implement):
    1) root = ensure_flight_model_root(context, name=DEFAULT_ROOT_NAME)
    2) skeleton = create_flight_model_skeleton(context, root)
    3) If `params.get("create_placeholders", True)`:
         - If `params["fuselage"]` present → create fuselage in **Bodies**.
         - If `params["wings"]` present → create Wing1 / Horiz_Stab / Vert_Stab in **Wings**.
         - (Landing gear deferred; return placeholder key.)

    Unit handling
    -------------
    - All user inputs are interpreted in the provided `units` ('m' or 'ft').
    - Use `convert_user_length_to_blender_meters(...)` so the created objects measure the
      intended **physical** sizes under the current scene's unit system and scale.

    Parameters
    ----------
    context : bpy.types.Context
    root_collection : bpy.types.Collection
        The **FlightModel** collection (parent). (Call `ensure_flight_model_root()` first if needed.)
    params : Optional[BuildParams]
        Aggregated placeholder settings (see types above).
    log_fn : Callable[[str], None]
        Logger callback (no-op in stub).

    Returns
    -------
    Dict[str, bpy.types.ID]
        Handles for created/ensured items, e.g.:
        {
          "skeleton": SkeletonMap,
          "fuselage_obj": bpy.types.Object | None,
          "wings": {"Wing1": obj | None, "Horiz_Stab": obj | None, "Vert_Stab": obj | None},
          "gear": None,  # placeholder in this phase
        }

    Raises
    ------
    ValueError
        On invalid collections or parameters.
    """
    raise NotImplementedError("stub")


# -------------------------
# Placeholder API — gear (no implementation now)
# -------------------------

def ensure_landing_gear_placeholders(
    context: bpy.types.Context,
    target_collection: bpy.types.Collection,
    *,
    layout: str = "tricycle",
    log_fn: Callable[[str], None] = lambda msg: None,
) -> Dict[str, bpy.types.Object]:
    """
    Placeholder for landing gear creators (to be implemented later).

    Parameters
    ----------
    context : bpy.types.Context
    target_collection : bpy.types.Collection
        Destination collection (expected: `LandingGear` under FlightModel).
    layout : str
        Gear layout hint (e.g., 'tricycle', 'taildragger').

    Returns
    -------
    Dict[str, bpy.types.Object]
        Empty dict for now (stub).

    Notes
    -----
    - This API exists to lock the module shape; no geometry is created in the stub.
    """
    raise NotImplementedError("stub")
