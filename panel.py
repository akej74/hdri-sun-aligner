# Blender imports
import bpy.types


class HDRISA_PT_main_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "HDRI Sun Aligner"
    bl_context = "objectmode"
    bl_category = "HDRI Sun Aligner"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.operator("hdrisa.dummy", text="Calculate sun position")
        layout.separator()
        row = layout.row()
        row.label(text="Current sun position:")
        row = layout.row()
        row.prop(scene.hdri_sa_props, "long_deg", text="Longitude")
        row = layout.row()
        row.prop(scene.hdri_sa_props, "lat_deg", text="Latitude")
        layout.separator()
        row = layout.row()
        row.operator("hdrisa.rotate", text="Rotate active object")
        row = layout.row()
        row.operator("hdrisa.add_new_sun", text="Add new sun")
        layout.separator()
        row = layout.row()
        row.operator("hdrisa.add_rotation_driver", text="Add rotation driver")
