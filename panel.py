# Blender imports
import bpy.types


class PANEL_PT_hdri_sun_aligner(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "HDRI Sun Aligner"
    bl_context = "objectmode"
    bl_category = "HDRI Sun Aligner"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.operator("object.dummy", text="Calculate sun position")
        layout.separator()
        row = layout.row()
        row.label(text="Current sun position:")
        row = layout.row()
        row.prop(scene.hdri_sa_property_grp, "long_deg", text="Longitude")
        row = layout.row()
        row.prop(scene.hdri_sa_property_grp, "lat_deg", text="Latitude")
        layout.separator()
        row = layout.row()
        row.operator("object.rotate", text="Rotate active object")
        row = layout.row()
        row.operator("object.add_new_sun", text="Add new sun")
        layout.separator()
        row = layout.row()
        row.operator("object.add_rotation_driver", text="Add rotation driver")
