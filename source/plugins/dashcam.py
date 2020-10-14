"""
pluginName = dashcam

Senario Continuous Video Series like a Dashcam
----------------------------------------------
You want to take a series of videos like a dash cam.
You can manage disk space and delete oldest videos when disk
is close to full or run video session for a set number of minutes.

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=dashcam
then these settings will override the config.py settings.

"""

# Customize Settings Below to Suit your Project Needs
# ---------------------------------------------------

# dashcam.py Plugin Settings
# --------------------------
IMAGE_NAME_PREFIX = 'dacam-' # Default= 'cam1-' for all image file names. Eg garage-

VIDEO_REPEAT_ON = True       # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
VIDEO_DIR = "media/dashcam"  # Default= "media/videos" Storage folder path for videos
VIDEO_PREFIX = "dc-"         # prefix for video filenames
VIDEO_START_AT = ""          # Default= "" Off or Specify date/time to Start Sequence eg "01-dec-2019 08:00:00" or "20:00:00"
VIDEO_FILE_SEC = 60          # Default= 60 seconds for each video recording
VIDEO_SESSION_MIN = 0        # Default= 30 minutes  Run Recording Session then Exit  0=Continuous
VIDEO_FPS = 30               # Default= 30 fps.  Note slow motion can be achieved at 640x480 image resolution at 90 fps
VIDEO_NUM_ON = True          # Default= True True=filenames by sequence Number  False=filenames by date/time
VIDEO_NUM_RECYCLE_ON = False # Default= False when NumMax reached restart at NumStart instead of exiting
VIDEO_NUM_START = 1000       # Default= 1000 Start of video filename number sequence
VIDEO_NUM_MAX  = 100         # Default= 20 Max number of videos desired. 0=Continuous

TIMELAPSE_ON = False          # Default= False True=Turn timelapse On, False=Off
MOTION_TRACK_ON = False       # Default= True True=Turns Motion Detect On, False=Off
MOTION_VIDEO_ON = False       # Default= False  True=Take a video clip rather than image
MOTION_TRACK_MINI_TL_ON = False     # Default= False  True=Take a quick time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)
MOTION_TRACK_QUICK_PIC_ON = False   # Default= False True= Grab stream frame rather than stopping stream to take full size image
PANTILT_ON = False           # True= Enable Pan Tilt Hat hardware,  False= Disable for TIMELAPSE_PANTILT_ON and PANO_ON
