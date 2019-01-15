# HDRI Sun Aligner
HDRI Sun Aligner is a Blender 2.8 addon for automatically rotating an object (e.g. a sun) to match the brightest point in a HDRI environment texture. Some ideas when this may be useful:
- Adding a sun to a scene rendered by EEVEE, as EEVEE cannot render shadows from HDRI environment textures
- Adding any light to enhance a scene, in alignment with direct light from the environment

Before rotation, a preview of the detected bright point is displayed:

<a href="url"><img src="https://i.imgur.com/yRJGJD0.jpg" height="200"  align="center" ></a>

# Usage
- Add a HDRI environment texture (equirectangular projection) to the World in Blender
- Select any object in the scene
- From the Object menu, select "HDRI Sun Aligner"
- A preview of the brightest point in the HDRI is displayed (normally the sun or brightest light), for verification
- Press any key to close the preview window
- The object is rotated in alignment with the vector from the bright light in the HDRI

# Installation of OpenCV library
HDRI Sun Aligner uses the "OpenCV" library for image processing, which needs to be installed as follows:

```
cd <path to blender>\2.80\python\bin
python.exe -m ensurepip
python.exe -m pip install --upgrade pip setuptools wheel
python.exe -m pip install opencv-python --user
```

# Installation of HDRI Sun Aligner addon
1. Download this repository as a ZIP file
2. Open Blender preferences -> addons and select "Install from file"...
3. Activate the addon
