bl_info = {
    "name" : "HDRI Sun Aligner",
    "author" : "Ake Johansson",
    "description" : "Rotates an object to match the brightest point in the HDRI texture used for the environment.",
    "version": (1, 2),
    "blender" : (2, 80, 0),
    "location" : "View3D > Object > HDRI Sun Aligner",
    "warning" : "",
    "category" : "Object"
}

# Blender imports
import bpy
import bpy.types

# Import Panel
from . panel import PANEL_PT_hdri_sun_aligner

# Import Operators
from . operators import OBJECT_OT_rotate
from . operators import OBJECT_OT_add_new_sun
from . operators import OBJECT_OT_dummy
from . operators import OBJECT_OT_calculate_sun_position
from . operators import OBJECT_OT_message_box


class HDRISunAlignerPropertyGroup(bpy.types.PropertyGroup):
    """ All properties used by HDRI Sun Aligner."""

    long_deg: bpy.props.FloatProperty(name="Longitude", default=0.0, min=-180.0, max=180.0)
    lat_deg: bpy.props.FloatProperty(name="Latitude", default=0.0, min=-90.0, max=90.0)


classes = (OBJECT_OT_calculate_sun_position,
           PANEL_PT_hdri_sun_aligner,
           OBJECT_OT_dummy,
           HDRISunAlignerPropertyGroup,
           OBJECT_OT_rotate,
           OBJECT_OT_message_box,
           OBJECT_OT_add_new_sun)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Add property group
    bpy.types.Scene.hdri_sa_property_grp = bpy.props.PointerProperty(type=HDRISunAlignerPropertyGroup)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    # Delete property group
    del bpy.types.Scene.hdri_sa_property_grp

if __name__ == "__main__":
    register()
