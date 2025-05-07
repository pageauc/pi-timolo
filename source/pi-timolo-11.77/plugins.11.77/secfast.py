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

# Customize Settings Below to Suit your Project Needs
# ---------------------------------------------------

imageNamePrefix = 'fast-'      # default= 'fast-' for all image file names. Eg garage-
imageVFlip = False             # default= False True Flips image Vertically
imageHFlip = False             # default= False True Flips image Horizontally
showDateOnImage = True         # default= True False=Do Not display date/time text on images

motionPrefix = "mo-"           # default= "mo-" stream image Prefix for all Motion Detect images
motionDir = "media/secfast"    # default= "media/secvid"  Folder Path for Motion Detect Image Storage
motionTrackQPBigger = 1.5      # default= 1.5 multiply size of QuickPic saved image from default 640x480
motionNumOn = True             # default= True  True=filenames by sequenced Number  False=filenames by date/time
# Use settings below if motionNumOn = True
motionNumRecycle = True        # default= False (off) True= Restart at NumStart when motionNumMax reached
motionNumStart = 1000          # default= 10000 Start 0f motion number sequence
motionNumMax  = 2000           # default= 0 (0=Continuous) or specify Max number of motion images desired.
motionForce = 3600             # default= 3600 seconds Off=0  Force an image if no Motion Detected in specified seconds

createLockFile = True          # default= False True=Create pi-timolo.sync file whenever images saved.
                               # Lock File is used to indicate motion images have been added
                               # so sync.sh can sync in background via sudo crontab -e

# Manage subfolders
# -----------------
motionSubDirMaxHours = 0       # 0=off or specify Max Hrs to create new sub-folder if HrsMax exceeded
motionSubDirMaxFiles = 0       # 0=off or specify MaxFiles before a new sub-folder created
motionRecentMax = 100          # 0=off  Maintain specified number of most recent files in motionRecentDir
motionRecentDir = "media/recent/secfast"  # default= "media/recent/secstill"  Location of motionRecent files

# Manage Disk Space Settings
#---------------------------
spaceTimerHrs = 1              # default= 1  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500              # default= 500  Target Free space in MB Required.
spaceMediaDir = motionDir      # default= motion per variable above
spaceFileExt  = 'jpg'          # default= 'jpg' File extension to Delete Oldest Files

# Do Not Change these Settings
# ----------------------------
motionTrackQuickPic = True     # True=Take quick image from video stream  False=Off
motionTrackOn = True           # Turn on Motion Tracking
motionVideoOn = False          # True=Take a video after motion event  False=Off
motionQuickTLOn = False        # Turn on motion timelapse sequence mode
timelapseOn = False            # Turn off normal time lapse mode so only motion mode used.
videoRepeatOn = False          # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion

