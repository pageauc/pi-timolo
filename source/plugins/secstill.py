"""
secstill plugin Senerio

This plugin will monitor camera view using motion tracking.
When motion tracking is triggered, the camera will take an HD still image
then stop and monitor for the next motion tracking event. There will
be a delay in taking the image due to camera change from streaming mode
therefore faster motions may be missed.

This configuration is suitable for a local security camera or a project
to capture high quality images of slower moving objects.

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=secstill
then these settings will override the config.py settings.

"""
# secstill pluging Security Cam Large Still Motion Capture Security
# -----------------------------------------------------------------
IMAGE_NAME_PREFIX = 'sec-'   # Default= 'cam1-' for all image file names. Eg garage-
IMAGE_WIDTH = 1920           # Default= 1024 Full Size Image Width in px
IMAGE_HEIGHT = 1080          # Default= 768  Full Size Image Height in px
IMAGE_FORMAT = ".jpg"        # Default= ".jpg"  image Formats .jpeg .png .gif .bmp
IMAGE_JPG_QUAL = 95          # Default= 95 jpg Encoder Quality Values 1(low)-100(high min compression) 0=85

MOTION_TRACK_ON = True        # Default= True True=Turns Motion Detect On, False=Off
MOTION_PREFIX = "mo-"         # Default= "mo-" Prefix for all Motion Detect images
MOTION_DIR = "media/secimg"    # Default= "media/motion"  Folder Path for Motion Detect Image Storage
MOTION_RECENT_DIR = "media/recent/secimg"  # Default= "media/recent/motion"  Location of motionRecent files
MOTION_NUM_RECYCLE_ON = False # Default= True when NumMax reached restart at NumStart instead of exiting
MOTION_NUM_START = 10000      # Default= 1000 Start 0f motion number sequence
MOTION_NUM_MAX  = 0           # Default= 2000 Max number of motion images desired. 0=Continuous

MOTION_TRACK_QUICK_PIC_ON = False # Default= False True= Grab stream frame rather than stopping stream to take full size image
MOTION_VIDEO_ON = False      # Default= False  True=Take a video clip rather than image
MOTION_TRACK_MINI_TL_ON = False     # Default= False  True=Take a quick time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)

# Turn off other features
TIMELAPSE_ON = False          # Default= False True=Turn timelapse On, False=Off
VIDEO_REPEAT_ON = False      # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
PANTILT_ON = False           # True= Enable Pan Tilt Hat hardware,  False= Disable for TIMELAPSE_PANTILT_ON and PANO_ON

