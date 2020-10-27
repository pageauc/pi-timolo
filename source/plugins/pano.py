"""
pluginName = pano

IMPORTANT set config.py PANTILT_IS_PIMORONI for your default pantilt hardware
it is not included in this plugin to avoid conflicts 

Senario Panning Timelapse Project
-------------------------------
This will require a working Pimoroni, Waveshare or Compatible Pan Tilt Hat Hardware.
This setup will save images in number sequence in case date/time is not maintained
due to a reboot and no internet NTP server is available.  A sequnce of images will
be take a PANO_CAM_STOPS and saved in the pano/images folder.  The
stitching task will be spawned and a pano image stitch will be started.  If
stitching is successful the pano image will be saved in pano/panos folder.

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=pano
then these settings will override the config.py settings.

"""

# Customize settings below to suit your project needs
# ---------------------------------------------------

IMAGE_NAME_PREFIX = 'cam1-'  # Default= 'cam1-' for all image file names. Eg garage-
IMAGE_WIDTH = 1920           # Default= 1024 Full Size Image Width in px
IMAGE_HEIGHT = 1080          # Default= 768  Full Size Image Height in px
IMAGE_FORMAT = ".jpg"        # Default= ".jpg"  image Formats .jpeg .png .gif .bmp
IMAGE_JPG_QUAL = 95          # Default= 95 jpg Encoder Quality Values 1(low)-100(high min compression) 0=85

PANTILT_ON = True            # True= Enable Pan Tilt Hat hardware,  False= Disable for TIMELAPSE_PANTILT_ON and PANO_ON
PANTILT_HOME = (0, -10)      # Default= (0, -10) Pan Tilt Home Postion. Values between -90 and + 90

PANO_ON = True               # Default= True Enable image stitching using pantilt overlapping images False= Disabled
                             # Note this can run in parallel with timelapse and motion tracking Options
PANO_IMAGE_PREFIX = 'pano-'  # Default= 'pano-' Prefix for pano images
PANO_TIMER_SEC = 300         # Default= 300 (5 min) Duration between taking pano images (Helps avoid multiple stitch tasks)
                             # FYI Stitching time on RPI4 can be less than 10 seconds.
PANO_NUM_START = 1000        # Default= 1000 Start of image numbering sequence
PANO_NUM_MAX   = 0           # Default= 20 Maximum number of pano's to take 0=Continuous.
PANO_NUM_RECYCLE = True      # Default= True Recycle numbering when NUM MAX exceeded. False= Exit
PANO_DAYONLY_ON = True       # Default= True Take Pano only during day.  False= Day and Night
PANO_IMAGES_DIR = './media/pano/images'  # Dir for storing pantilt source images
PANO_DIR = './media/pano/panos'  # Dir for storing final panoramic images
PANO_PROG_PATH = '/usr/local/bin/image-stitching'  # Path to image stitching program config.cfg in pi-timolo dir.

# Set stops to take overlapping images. You need sufficient overlap for successful stitching
# Default setting [(36, 20), (0, 20), (-36, 20)] is for 1920x1080 camera resolution
# More images requires more time to stitch.  Adjust PANO_TIMER_SEC setting to avoid multiple stitches at once.
# Tested on single core RPI, but will stitch much faster on quad core.
PANO_CAM_STOPS = [(36, -10),
                  (0, -10),
                  (-36, -10)
                 ]

# Turn off other features
TIMELAPSE_ON = False          # Default= False True=Turn timelapse On, False=Off
MOTION_TRACK_ON = False       # Default= True True=Turns Motion Detect On, False=Off
MOTION_TRACK_QUICK_PIC_ON = False # Default= False True= Grab stream frame rather than stopping stream to take full size image
MOTION_VIDEO_ON = False       # Default= False  True=Take a video clip rather than image
MOTION_TRACK_MINI_TL_ON = False     # Default= False  True=Take a quick time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)
VIDEO_REPEAT_ON = False       # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
