import bpy
import os

# Generate stubs into the folder where this script lives
out_dir = os.path.dirname(__file__)
print(f"Generating Blender stubs into: {out_dir}")
bpy.utils.generate_stub_files(out_dir, report=True)
print("Done generating stubs.")
