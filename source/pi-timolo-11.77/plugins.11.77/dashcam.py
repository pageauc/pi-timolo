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

imageWidth = 1280             # default= 1280 Full Size video Width in px
imageHeight = 720             # default= 720  Full Size video Height in px
imageVFlip = False            # default= False True Flips image Vertically
imageHFlip = False            # default= False True Flips image Horizontally
showDateOnImage = True        # default= True False=Do Not display date/time text on images

videoPath = "media/dashcam"   # default= media/dashcam Storage folder path for videos
videoPrefix = "dc-"           # prefix for dasbca video filenames
videoDuration = 120           # default= 120 seconds (2 min) for each video recording
videoTimer = 0                # default= 0 0=Continuous or Set Total Session Minutes to Record then Exit
videoFPS = 30                 # default= 30 fps.  Note slow motion can be achieved at 640x480 image resolution at 90 fps

videoNumOn = False            # default= False False=filenames by date/time True=filenames by sequence Number
# Use settings below if motionNumOn = True
videoNumRecycle = False       # default= False when NumMax reached restart at NumStart instead of exiting
videoNumStart = 1000          # default= 1000 Start of video filename number sequence
videoNumMax  = 0              # default= 20 Max number of videos desired. 0=Continuous

# Manage Disk Space Settings
#---------------------------
spaceTimerHrs = 1             # default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500             # default= 500  Target Free space in MB Required.
spaceMediaDir = videoPath     # default= videoPath per variable above
spaceFileExt  = 'mp4'         # default= '' File extension to Delete Oldest Files

# Do Not Change these Settings
# ----------------------------
videoRepeatOn = True          # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
