# HDRI Sun Aligner
HDRI Sun Aligner is a Blender 2.8 addon for automatically rotating an object (e.g. a sun lightsource) to match the brightest point in a HDRI environment texture. Some ideas when this may be useful:
- Adding a sun lightsource to a scene rendered by EEVEE, as EEVEE cannot render shadows from HDRI environment textures
- Adding any lightsource to enhance a scene, in alignment with direct light from the environment

Before rotation, a preview of the detected bright point is displayed:

<a href="url"><img src="https://i.imgur.com/yRJGJD0.jpg" height="200"  align="center" ></a>

# Usage
- Add a HDRI environment texture (equirectangular projection) to the World in Blender
- Select any object in the scene
- From the Object menu, select "HDRI Sun Aligner"
- A preview of the brightest point in the HDRI is displayed (normally the sun or brightest lightsource), for verification
- Press any key to close the preview window
- The object is rotated in alignment with the vector from the bright lightsource in the HDRI

# Installation
## Installation of OpenCV
HDRI Sun Aligner uses the "OpenCV" library for image processing, which needs to be installed as follows:
### 1. Install PIP
```
cd <path to blender>\2.80\python\bin
python.exe -m ensurepip
```
### 2. Rename existing "numpy" folder
The "numpy" module is required by OpenCV and is already included in the Blender Python distribution. For some unknown reason, pip will not find this module, which will cause a a conflict during installation of OpenCV.

Solve this by renaming the exiting "numpy" folder to "_numpy" (it will be reinstalled in the next step):

`<path to blender>\2.80\python\lib\site-packages\numpy`

...rename to...

`<path to blender>\2.80\python\lib\site-packages\_numpy`

### 3. Install OpenCV
```
cd <path to blender>\2.80\python\Scripts
pip3.exe install opencv-python
```
This installes both "numpy" and "opencv-python" in `2.80\python\lib\site-packages\`

## Installation of HDRI Sun Aligner addon
1. Download this repository as a ZIP file
2. Open Blender preferences -> addons and select "Install from file"...
3. Activate the addon
