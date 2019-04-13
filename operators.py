# Blender imports
import bpy.types

# Other imports
import numpy as np
from math import pi, cos, sin
import mathutils


class HDRISA_OT_rotate(bpy.types.Operator):
    """Rotate active object in alignment with sun position"""     

    bl_idname = "hdrisa.rotate"     
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
  
        longitude = scene.hdri_sa_props.long_deg * (pi/180) # Convert to radians
        latitude = scene.hdri_sa_props.lat_deg * (pi/180)

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

        # Store z-rotation value as property, used for driver calculation 
        scene.hdri_sa_props.z_org = euler.z
        
        # Rotate selected object
        object.rotation_euler = euler
        
        return {'FINISHED'}   


class HDRISA_OT_add_new_sun(bpy.types.Operator):
    """Add a new sun, rotated in alignment with current sun position"""     

    bl_idname = "hdrisa.add_new_sun"     
    bl_label = "Add a new sun, rotated in alignment with current sun position."         
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Deselect objects
        for obj in context.selected_objects:
            obj.select_set(state=False)
        
        # Create new collection if it doesn't exist        
        new_collection = self.make_collection("HDRI Sun Aligner")
        
        # Create new sun object in the collection
        sun_data = bpy.data.lights.new(name="HDRI Sun", type='SUN')
        sun_object = bpy.data.objects.new(name="HDRI Sun", object_data=sun_data)
        new_collection.objects.link(sun_object)
        
        # Select sun object and rotate
        sun_object.select_set(state=True)
        context.view_layer.objects.active = sun_object
        bpy.ops.hdrisa.rotate()

        return {'FINISHED'}

    def make_collection(self, collection_name):
        # Check if collection already exists
        if collection_name in bpy.data.collections:
            return bpy.data.collections[collection_name]
        # If not, create new collection
        else:
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
            return new_collection


class HDRISA_OT_add_rotation_driver(bpy.types.Operator):
    """Add a a driver to the active object z-rotation, based on HDRI mapping node"""     

    bl_idname = "hdrisa.add_rotation_driver"     
    bl_label = "Add a a driver to the active object z-rotation, based on HDRI rotation using mapping node."         
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
        
        mapping_node = None
        world_nodes = scene.world.node_tree.nodes # All nodes for the World
        
        for node in world_nodes:
            # Find the Vector Mapping node
            if isinstance(node, bpy.types.ShaderNodeMapping):
                mapping_node = node.name
                break
        
        if mapping_node:
            # Path to HDRI mapping node z-rotation value
            data_path = f'node_tree.nodes["{mapping_node}"].rotation[2]'
            
            # Driver for z rotation  
            z_rotation_driver = object.driver_add('rotation_euler', 2)

            hdri_z = z_rotation_driver.driver.variables.new() # HDRI mapping node
            obj_z = z_rotation_driver.driver.variables.new() # Object original rotation 
            
            hdri_z.name = "hdri_z"
            hdri_z.targets[0].id_type = 'WORLD'
            hdri_z.targets[0].id = scene.world
            hdri_z.targets[0].data_path = data_path

            obj_z.name = "obj_z"
            obj_z.targets[0].id_type = 'SCENE'
            obj_z.targets[0].id = scene
            obj_z.targets[0].data_path = 'hdri_sa_props.z_org'

            z_rotation_driver.driver.expression = obj_z.name + '-' + hdri_z.name

        else:
            msg = "No Mapping node defined for HDRI rotation."
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message=msg)
            self.report({'WARNING'}, msg)
            return {'CANCELLED'}


        return {'FINISHED'}


class HDRISA_OT_dummy(bpy.types.Operator):
    """Calculate the brightest spot in the HDRI used for the environment"""
    
    #Dummy operator used for main operation with overide   

    bl_idname = "hdrisa.dummy"     
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
        
        bpy.ops.hdrisa.calculate_sun_position(override, 'INVOKE_DEFAULT')
        return {'FINISHED'}


class HDRISA_OT_message_box(bpy.types.Operator):
    """Show a message box."""

    bl_idname = "message.messagebox"
    bl_label = ""
 
    message: bpy.props.StringProperty(
        name="message",
        description="message",
        default=''
    )
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
 
    def draw(self, context):
        self.layout.label(text=self.message)
        self.layout.label(text="")


class HDRISA_OT_calculate_sun_position(bpy.types.Operator):
    """Calculate the brightest spot in the HDRI image used for the environment"""

    bl_idname = "hdrisa.calculate_sun_position"     
    bl_label = "Calculate sun position."         
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        scene = context.scene
        screen = context.screen
        world_nodes = scene.world.node_tree.nodes # All nodes for the World
        image = None
        
        # Cleanup to prevent duplicate images
        for img in bpy.data.images:
                name = img.name
                if name.startswith("hdri_sa_preview"):
                    bpy.data.images.remove(img)

        # Check if an environmental image is defined        
        for node in world_nodes:
            # Find the Environment Texture node
            if isinstance(node, bpy.types.ShaderNodeTexEnvironment): 
                image = node.image
            
        if image:
            # Make a copy of the original HDRI
            hdri_preview = image.copy()
            
            hdri_preview.name = "hdri_sa_preview." + image.file_format
            
            # Get image dimensions
            org_width = hdri_preview.size[0]
            org_height = hdri_preview.size[1]
            
            # Scale image if it's larger than 1k for improving performance
            if org_width > 1024:
                new_width = 1024
                new_height = int(org_height * (new_width / org_width))
                hdri_preview.scale(new_width, new_height)
           
            # Check if an Image Editor is open
            open_editor_types = [area.type for area in screen.areas]
            
            if "IMAGE_EDITOR" not in open_editor_types:
                msg = "Please open an Image Editor window."
                bpy.ops.message.messagebox('INVOKE_DEFAULT', message=msg)
                self.report({'WARNING'}, msg)
                return {'CANCELLED'}

            # Open hdri_preview image in the Image Editor
            for area in screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = hdri_preview 
        else:
            msg = "Please add an Environment Texture for the world."
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message=msg)
            self.report({'WARNING'}, msg)
            return {'CANCELLED'}

        # Calculate longitude, latitude and update HDRI preview image
        long_deg, lat_deg = self.process_hdri(hdri_preview)
        
        # Update properties
        scene.hdri_sa_props.long_deg = long_deg
        scene.hdri_sa_props.lat_deg = lat_deg
 
        #context.window_manager.modal_handler_add(self)
        #return {'RUNNING_MODAL'}
        return {'FINISHED'}

    
    def modal(self, context, event):
        """ Get image coordinates from mouse click.
        
        *** Currently not in use ***
        """

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            
            # TODO: Use image direcly
            img_size_x = context.scene.hdri_sa_props.img_size_x
            img_size_y = context.scene.hdri_sa_props.img_size_y

            # Get image coordinate from mouse click in Image Editor
            reg_x = event.mouse_region_x 
            reg_y = event.mouse_region_y

            # Calculate image coordinates
            uv_x, uv_y = context.region.view2d.region_to_view(reg_x, reg_y)
            img_coordinate_x = int(uv_x * img_size_x) 
            img_coordinate_y = int(uv_y * img_size_y)

            # Limit coordinates from zero to max size of image            
            if img_coordinate_x > img_size_x:
                img_coordinate_x = img_size_x 
            
            if img_coordinate_y > img_size_y:
                img_coordinate_y = img_size_y
            
            if img_coordinate_x < 0:
                img_coordinate_x = 0
            
            if img_coordinate_y < 0:
                img_coordinate_y = 0
            
            print(img_coordinate_x, img_coordinate_y)
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("Cancel...")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def process_hdri(self, image):
        """
        Calculate the brightest point in the equirectangular HDRI image (i.e. the sun or brightest light).
        A gaussian blur is applied to the image to prevent errors from single bright pixels.

        Update the "hdri_preview" image and return the longitude and latitude in degrees.
        """

        # Get a flat Numpy array with the image pixels
        hdri_img = np.array(image.pixels[:])

        width, height = image.size
        depth = 4 # RGBA
              
        # Reshape to RGBA matrix
        hdri_img = np.array(hdri_img).reshape([height, width, depth]) 

        # Get image dimensions
        height, width = hdri_img.shape[:2]
        
        # Convert to grayscale
        gray_img = np.dot(hdri_img[...,:3], [0.299, 0.587, 0.114])
        
        # Apply gaussian blur
        gray_img = self.gaussian_blur(gray_img, sigma=100)

        # Find index of maximum value from 2D numpy array
        result = np.where(gray_img == np.amax(gray_img))
 
        # zip the 2 arrays to get the exact coordinates
        list_of_coordinates = list(zip(result[0], result[1]))

        # Assume only one maximum, use the first found
        max_loc_new = list_of_coordinates[0]
        
        # Get x and y coordinates for the brightest pixel 
        max_x = max_loc_new[1]
        max_y = max_loc_new[0]
        
        # Create masks to indicate sun position
        circle_mask = self.create_circular_mask(height, width, thickness=4, center=[max_x, max_y], radius=50)
        point_mask = self.create_circular_mask(height, width, thickness=4, center=[max_x, max_y], radius=5)
        
        # Draw circle
        hdri_img[:, :, 0][circle_mask] = 1 # Red
        hdri_img[:, :, 1][circle_mask] = 0 # Green 
        hdri_img[:, :, 2][circle_mask] = 0 # Blue

        # Draw center dot
        hdri_img[:, :, 0][point_mask] = 1
        hdri_img[:, :, 1][point_mask] = 0
        hdri_img[:, :, 2][point_mask] = 0

        # Find the point in longitude and latitude (degrees)
        long_deg = ((max_x * 360) / width) - 180
        lat_deg = -(((max_y * -180) / height) + 90)
                     
        # Flatten array and update the blender image object       
        image.pixels = hdri_img.ravel()
        
        return long_deg, lat_deg

    def create_circular_mask(self, h, w, thickness, center=None, radius=None):
        """Create a circular mask used for drawing on the HDRI preview."""

        if center is None: # use the middle of the image
            center = [int(w/2), int(h/2)]
        if radius is None: # use the smallest distance between the center and image walls
            radius = min(center[0], center[1], w-center[0], h-center[1])

        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
        
        mask = np.logical_and(dist_from_center <= radius, dist_from_center >= (radius - thickness))
        
        return mask

    def gaussian_blur(self, gray_image, sigma):
        """ Apply gaussion blur to a grayscale image.
        
        Input: 
        - 2D Numpy array
        - sigma (gaussian blur radius)

        Return:
        - 2D Numpy array (blurred image)

        See https://scipython.com/book/chapter-6-numpy/examples/blurring-an-image-with-a-two-dimensional-fft/        
        """

        rows, cols = gray_image.shape
              
        # Take the 2-dimensional DFT and centre the frequencies
        ftimage = np.fft.fft2(gray_image)
        ftimage = np.fft.fftshift(ftimage)
        
        # Build and apply a Gaussian filter.
        sigmax = sigma
        sigmay = sigma
        cy, cx = rows/2, cols/2
        y = np.linspace(0, rows, rows)
        x = np.linspace(0, cols, cols)
        X, Y = np.meshgrid(x, y)
        gmask = np.exp(-(((X-cx)/sigmax)**2 + ((Y-cy)/sigmay)**2))

        ftimagep = ftimage * gmask

        # Take the inverse transform
        imagep = np.fft.ifft2(ftimagep)
        imagep = np.abs(imagep)

        return imagep
