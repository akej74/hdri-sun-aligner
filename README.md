# HDRI Sun Aligner
HDRI Sun Aligner is a Blender 2.8 addon for automatically rotating an object (e.g. a sun) to match the brightest point in a HDRI environment texture. Some ideas when this may be useful:
- Adding a sun to a scene rendered by EEVEE, as EEVEE cannot render shadows from HDRI environment textures
- Adding any light to enhance a scene, in alignment with direct light from the environment

# Usage
- Add a HDRI environment texture (equirectangular projection) to the World in Blender
- Open both the 3D Viewport and an Image Editor
- HDRI Sun Aligner is accessed from the panel to the right:

<a href="https://imgur.com/OmL1k2z"><img src="https://i.imgur.com/OmL1k2z.jpg" height="200" title="source: imgur.com" /></a>

- Calculate the brightest point in the HDRI used for the environment by clicking on "Calculate sun position"
- A preview of the calculated position is displayed in the image editor:

<a href="https://imgur.com/nymkd3D"><img src="https://i.imgur.com/nymkd3D.jpg" height="200" title="source: imgur.com" /></a>

- Updated "Longitude and Latitude" values are displayed in the panel (can be changed manually)
- Select any object and click "Rotate object" to align it with a vector from the calculated point to origo
- To add a new sun (rotated in alignment with the current sun position), click "Add new sun"
  - The new sun will be located in a new collection, "HDRI Sun Aligner"

# Installation of HDRI Sun Aligner addon
1. Download latest release from https://github.com/akej74/hdri-sun-aligner/releases (source as ZIP). 
2. Open Blender preferences -> addons and select "Install from file"...
3. Activate the addon, "HDRI Sun Aligner"
