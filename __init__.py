bl_info = {
    "name": "HDRI Sun Aligner",
    "author": "Ake Johansson",
    "description": "Rotates an object to match the brightest point in the HDRI texture used for the environment.",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "View3D > Object > HDRI Sun Aligner",
    "warning": "",
    "category": "Object"
}

# Blender imports
import bpy
import bpy.types

# Import Panel
from .panel import HDRISA_PT_main_panel

# Import Operators
from .operators import HDRISA_OT_rotate
from .operators import HDRISA_OT_add_new_sun
from .operators import HDRISA_OT_dummy
from .operators import HDRISA_OT_calculate_sun_position
from .operators import HDRISA_OT_message_box
from .operators import HDRISA_OT_add_rotation_driver


class HDRISAProperties(bpy.types.PropertyGroup):
    """All properties used by HDRI Sun Aligner."""

    long_deg: bpy.props.FloatProperty(name="Longitude", default=0.0, min=-180.0, max=180.0)
    lat_deg: bpy.props.FloatProperty(name="Latitude", default=0.0, min=-90.0, max=90.0)
    z_org: bpy.props.FloatProperty(name="Z rot org", default=0.0)


classes = (HDRISA_OT_calculate_sun_position,
           HDRISA_OT_dummy,
           HDRISA_OT_rotate,
           HDRISA_OT_message_box,
           HDRISA_OT_add_new_sun,
           HDRISA_OT_add_rotation_driver,
           HDRISA_PT_main_panel,
           HDRISAProperties)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Add property group
    bpy.types.Scene.hdri_sa_props = bpy.props.PointerProperty(type=HDRISAProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    # Delete property group
    del bpy.types.Scene.hdri_sa_props

if __name__ == "__main__":
    register()
