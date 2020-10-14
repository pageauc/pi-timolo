"""
shopcam plugin Senario

The shopcam settings below will monitor camera view using motion tracking.
When motion tracking is triggered, the camera will take a sequence of
time lapse images with motionQuickTLInterval seconds between images and continue
for motionQuickTLTimer seconds duration then stop and monitor for another
motion tracking event.

Once the camera is setup you do not have to manage it for a each work session timelapse
sequence, since it is only activated when work motion is tracked.  If work takes longer than
motionQuickTLInterval then the next motion will trigger another timelapse sequence per settings.
Ideal for a timelapse project that spans many days with work happening at differnt times.

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=shopcam
then these settings will override the config.py settings.

"""
# Customize Settings Below to Suit your Project Needs
# ---------------------------------------------------
# secQTL plugin Fast Quick Pic Motion Capture Security cam
# --------------------------------------------------------
IMAGE_NAME_PREFIX = 'shop-'   # Default= 'cam1-' for all image file names. Eg garage-
IMAGE_WIDTH = 1920           # Default= 1024 Full Size Image Width in px
IMAGE_HEIGHT = 1080          # Default= 768  Full Size Image Height in px
IMAGE_FORMAT = ".jpg"        # Default= ".jpg"  image Formats .jpeg .png .gif .bmp
IMAGE_JPG_QUAL = 95          # Default= 95 jpg Encoder Quality Values 1(low)-100(high min compression) 0=85

MOTION_TRACK_ON = True       # Default= True True=Turns Motion Detect On, False=Off
MOTION_PREFIX = "motl-"        # Default= "mo-" Prefix for all Motion Detect images
MOTION_DIR = "media/shop"     # Default= "media/motion"  Folder Path for Motion Detect Image Storage
MOTION_RECENT_DIR = "media/recent/shop"  # Default= "media/recent/motion"  Location of motionRecent files
MOTION_TRACK_MINI_TL_ON = True      # Default= False  True=Take a quick time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)
MOTION_TRACK_MINI_TL_SEQ_SEC = 3600   # Default= 30 Duration in seconds of quick time lapse sequence after initial motion detected
MOTION_TRACK_MINI_TL_TIMER_SEC = 20   # Default= 5 seconds between each Quick time lapse image. 0 is fast as possible

# Turn off other features
TIMELAPSE_ON = False          # Default= False True=Turn timelapse On, False=Off
MOTION_VIDEO_ON = False       # Default= False  True=Take a video clip rather than image
MOTION_TRACK_QUICK_PIC_ON = False # Default= False True= Grab stream frame rather than stopping stream to take full size image
MOTION_VIDEO_ON = False      # Default= False  True=Take a video clip rather than image
VIDEO_REPEAT_ON = False      # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
