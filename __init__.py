bl_info = {
    "name" : "HDRI Sun Aligner",
    "author" : "Ake Johansson",
    "description" : "Rotates an object to match the brightest point in the HDRI texture used for the environment.",
    "version": (1, 1),
    "blender" : (2, 80, 0),
    "location" : "View3D > Object > HDRI Sun Aligner",
    "warning" : "",
    "category" : "Object"
}

# Blender imports
import bpy
import bpy.types

# Other imports
import numpy as np
from math import pi, cos, sin
import mathutils

class OBJECT_OT_rotate(bpy.types.Operator):
    """Rotate active object in alignment with sun position"""     

    bl_idname = "object.rotate"     
    bl_label = "Rotate active object in alignment with sun position."         
    bl_options = {'REGISTER'}

    # Only enable operator if an object is selected
    @classmethod
    def poll(cls, context):        
        if bpy.context.selected_objects:
            return True
        else:
            return False

    def execute(self, context):
        scene = context.scene
        object = context.object
  
        longitude = scene.hdri_sa_property_grp.long_deg * (pi/180) # Convert to radians
        latitude = scene.hdri_sa_property_grp.lat_deg * (pi/180)

        # Calculate a vector pointing from the longitude and latitude to origo
        # See https://vvvv.org/blog/polar-spherical-and-geographic-coordinates 
        x = cos(latitude) * cos(longitude)
        y = cos(latitude) * sin(longitude)
        z = sin(latitude)

        # Define euler rotation according to the vector
        vector = mathutils.Vector([x, -y, z]) # "-y" to match Blender coordinate system
        up_axis = mathutils.Vector([0.0, 0.0, 1.0])
        angle = vector.angle(up_axis, 0)
        axis = up_axis.cross(vector)
        euler = mathutils.Matrix.Rotation(angle, 4, axis).to_euler()

        # Rotate selected object
        object.rotation_euler = euler
        
        return {'FINISHED'}   


class OBJECT_OT_dummy(bpy.types.Operator):
    """Calculate the brightest spot in the HDRI used for the environment"""
    
    #Dummy operator used for main operation with overide   

    bl_idname = "object.dummy"     
    bl_label = "Dummy"         
    bl_options = {'REGISTER'}

    def execute(self, context):
        screen = context.screen
        override = bpy.context.copy()

        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'region': region, 'area': area}
        
        bpy.ops.object.calculate_sun_position(override, 'INVOKE_DEFAULT')
        return {'FINISHED'}


class OBJECT_OT_hdri_sun_aligner(bpy.types.Operator):
    """HDRI Sun Aligner"""      

    bl_idname = "object.hdri_sun_aligner"     
    bl_label = "HDRI Sun Aligner"         
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):      
        scene = context.scene
        object = context.object
        world_nodes = scene.world.node_tree.nodes # All nodes for the World
        image = None
                       
        for node in world_nodes:
            # Find the Environment Texture node
            if isinstance(node, bpy.types.ShaderNodeTexEnvironment): 
                image = node.image

            if image:
                # Load the image used for the environment texture
                image_file = bpy.path.abspath(image.filepath, library=image.library)

                # Process the image to find the longitude and latitude for the brightest point
                longitude, latitude = self.process_hdri(image_file)

                # Calculate a vector pointing from the longitude and latitude (radians)
                # See https://vvvv.org/blog/polar-spherical-and-geographic-coordinates 
                x = cos(latitude) * cos(longitude)
                y = cos(latitude) * sin(longitude)
                z = sin(latitude)

                # Define rotation according to the vector
                vector = mathutils.Vector([x, -y, z]) # "-y" to match Blender coordinate system
                up_axis = mathutils.Vector([0.0, 0.0, 1.0])
                angle = vector.angle(up_axis, 0)
                axis = up_axis.cross(vector)
                euler = mathutils.Matrix.Rotation(angle, 4, axis).to_euler()

                # Rotate selected object
                object.rotation_euler = euler

        return {'FINISHED'}

    def process_hdri(self, image_file):
        """
        Calculate the brightest point in the equirectangular HDRI image (i.e. the sun or brightest light).
        A gaussian blur is applied to the image to prevent errors from single bright pixels.

        A preview of the calculated sun position is displayed (using OpenCV "imshow").

        Return the longitude and latitude in radians.
        """

        new_width = 1024 # Rezize image to 1024 pixels wide
        radius = 51 # Radius for gaussian blur, must be an odd number

        # Open the image (numpy array) with raw pixel values
        img = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
        
        # Get image dimensions
        original_height, original_width = img.shape[:2]
        
        # Resize to width of 1024 pixels to speed up processing 
        ratio = new_width / original_width
        dim = (new_width, int(original_height * ratio))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)
        new_height, new_width = img.shape[:2]
        
        # Convert to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply gaussian blur
        gray_img_blurred = cv2.GaussianBlur(gray_img, (radius, radius), 0)

        # Get brightest point
        (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(gray_img_blurred)
        
        # Add a circle and center point to the original image for illustration
        cv2.circle(img, max_loc, radius, (255, 0, 0), 2)
        cv2.circle(img, max_loc, 3, (255, 0, 0), -1)

        # X and Y position of the brightest point
        max_x, max_y = max_loc

        # Find the point in longitude and latitude (degrees) from x-y coordinate in image
        # Longitude range: [-180 to +180]
        # Latitude range: [+90 to -90]
        #####################################
        # -180, +90              +180, +90  #                 
        #                                   #
        # -180, -90              +180, -90  #
        #####################################
        longitude_deg = ((max_x * 360) / new_width) - 180
        latitude_deg = ((max_y * -180) / new_height) + 90

        # Convert to radians
        longitude_rad = longitude_deg * (pi/180)
        latitude_rad = latitude_deg * (pi/180)
               
        # Tonemap and convert HDR to 8 bit LDR image (for displaying the calculated sun position)    
        tonemap = cv2.createTonemapReinhard(gamma=1.5, intensity=1.8, light_adapt=0, color_adapt=0)
        tonemapped_img = tonemap.process(img)

        # Convert float [0.0-1.0] to float [0.0-255.0]
        ldr_img = tonemapped_img * 255

        # Convert to uint8 datatype (required for displaying the image with "imshow")
        ldr_img = ldr_img.astype(np.uint8) 

        # Display the image in a new window
        cv2.imshow('HDRI sun position preview - press any key to close', ldr_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return longitude_rad, latitude_rad

def menu_draw(self, context):
    self.layout.separator()
    self.layout.operator("object.hdri_sun_aligner")

classes = (OBJECT_OT_hdri_sun_aligner,)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Add operator to Object menu in 3D Viewport
    bpy.types.VIEW3D_MT_object.append(menu_draw)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    # Remove operator from Object menu in 3D Viewport
    bpy.types.VIEW3D_MT_object.remove(menu_draw)

if __name__ == "__main__":
    register()
