"""
pluginName = secfast

Senario Security Video Stream Image
-----------------------------------
This plugin will monitor camera view using motion tracking.
When motion tracking is triggered, the camera will save a video stream image
then stop and monitor for the next motion tracking event. This will allow
capture of faster moving objects but lower quality.  The image size will
be smaller so gdrive updates will be quicker.  Note no subfolders are
created and only a limited number of images will be created with
image numbering getting recycled when motionNumMax reached.

This configuration is suitable for a remote security camera or a project
to capture images of faster moving objects.

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=secfast
then these settings will override the config.py settings.

"""

# Security Cam Quick Pic Motion Capture Security
# -------------------------------------------
IMAGE_NAME_PREFIX = 'fast-' # Default= 'cam1-' for all image file names. Eg garage-

MOTION_TRACK_ON = True        # Default= True True=Turns Motion Detect On, False=Off
MOTION_PREFIX = "mo-"        # Default= "mo-" Prefix for all Motion Detect images
MOTION_TRACK_QUICK_PIC_ON = True # Default= False True= Grab stream frame rather than stopping stream to take full size image
MOTION_TRACK_QUICK_PIC_BIGGER = 3.0 # Default= 3.0 multiply size of QuickPic saved image from Default 640x480
MOTION_DIR = "media/fast"  # Default= "media/motion"  Folder Path for Motion Detect Image Storage
MOTION_RECENT_DIR = "media/recent/fast"  # Default= "media/recent/motion"  Location of motionRecent files

# Turn off other features
TIMELAPSE_ON = False          # Default= False True=Turn timelapse On, False=Off
MOTION_VIDEO_ON = False       # Default= False  True=Take a video clip rather than image
MOTION_TRACK_MINI_TL_ON = False  # Default= False  True=Take a quick time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)
VIDEO_REPEAT_ON = False      # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
PANTILT_ON = False           # True= Enable Pan Tilt Hat hardware,  False= Disable for TIMELAPSE_PANTILT_ON and PANO_ON
