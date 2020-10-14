"""
pluginName = secvid

Senario Security take Video for Motion Event
--------------------------------------------
This plugin will monitor camera view using motion tracking.
When motion tracking is triggered, the camera will take a short video
for motionVideoTimer seconds then stop and monitor for the next
motion tracking event.

Suitable for capturing video after a motion event

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=secvid
then these settings will override the config.py settings.

"""

# Customize Settings Below to Suit your Project Needs
# ---------------------------------------------------

# secvid plugin Security HD Video on Motion Tracking Security
# -----------------------------------------------------------
IMAGE_NAME_PREFIX = 'vid-'   # Default= 'cam1-' for all image file names. Eg garage-
IMAGE_WIDTH = 1280           # Default= 1024 Full Size Image Width in px
IMAGE_HEIGHT = 720           # Default= 768  Full Size Image Height in px
MOTION_VIDEO_ON = True       # Default= False  True=Take a video clip rather than image
MOTION_VIDEO_FPS = 15        # Default= 15 If image size reduced to 640x480 then slow motion is possible at 90 fps
MOTION_VIDEO_TIMER_SEC = 20  # Default= 10 seconds of video clip to take if Motion Detected

MOTION_TRACK_ON = True        # Default= True True=Turns Motion Detect On, False=Off
MOTION_PREFIX = "mo-"         # Default= "mo-" Prefix for all Motion Detect images
MOTION_DIR = "media/hdvid"    # Default= "media/motion"  Folder Path for Motion Detect Image Storage
MOTION_RECENT_DIR = "media/recent/hdvid"  # Default= "media/recent/motion"  Location of motionRecent files
MOTION_NUM_RECYCLE_ON = False # Default= True when NumMax reached restart at NumStart instead of exiting
MOTION_NUM_START = 10000      # Default= 1000 Start 0f motion number sequence
MOTION_NUM_MAX  = 0           # Default= 2000 Max number of motion images desired. 0=Continuous

# Turn off other features
MOTION_TRACK_QUICK_PIC_ON = False # Default= False True= Grab stream frame rather than stopping stream to take full size image
MOTION_TRACK_MINI_TL_ON = False     # Default= False  True=Take a quick time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)
TIMELAPSE_ON = False          # Default= False True=Turn timelapse On, False=Off
VIDEO_REPEAT_ON = False      # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
PANTILT_ON = False           # True= Enable Pan Tilt Hat hardware,  False= Disable for TIMELAPSE_PANTILT_ON and PANO_ON
