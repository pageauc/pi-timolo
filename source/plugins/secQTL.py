"""
pluginName = secQTL

Senario Security Quick Timelapse for motion event
-------------------------------------------------
This plugin will monitor camera view using motion tracking.
When motion tracking is triggered, the camera will take a series of
quick timelapse images to capture motion in HD images.  This may be
more suitable that taking a video and uses less disk space.
Once quick timelapse sequence is complete, motion tracking will resume.
Note no subfolders are created and only a limited number of images will be created with
image numbering getting recycled when motionNumMax reached.

This configuration is suitable for a remote security camera or a project
to capture HD images of faster moving objects using a timelapse sequence.

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=secQTL
then these settings will override the config.py settings.

"""
# Customize settings below to suit your project needs

# secQTL plugin Fast Quick Pic Motion Capture Security cam
# --------------------------------------------------------
IMAGE_NAME_PREFIX = 'qtl-'   # Default= 'cam1-' for all image file names. Eg garage-
MOTION_TRACK_ON = True       # Default= True True=Turns Motion Detect On, False=Off
MOTION_PREFIX = "mo-"        # Default= "mo-" Prefix for all Motion Detect images
MOTION_DIR = "media/qtl"     # Default= "media/motion"  Folder Path for Motion Detect Image Storage
MOTION_RECENT_DIR = "media/recent/qtl"  # Default= "media/recent/motion"  Location of motionRecent files
MOTION_TRACK_MINI_TL_ON = True      # Default= False  True=Take a quick time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)
MOTION_TRACK_MINI_TL_SEQ_SEC = 40   # Default= 30 Duration in seconds of quick time lapse sequence after initial motion detected
MOTION_TRACK_MINI_TL_TIMER_SEC = 0  # Default= 5 seconds between each Quick time lapse image. 0 is fast as possible

# Turn off other features
TIMELAPSE_ON = False          # Default= False True=Turn timelapse On, False=Off
MOTION_VIDEO_ON = False       # Default= False  True=Take a video clip rather than image
MOTION_TRACK_QUICK_PIC_ON = False # Default= False True= Grab stream frame rather than stopping stream to take full size image
MOTION_VIDEO_ON = False      # Default= False  True=Take a video clip rather than image
VIDEO_REPEAT_ON = False      # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
