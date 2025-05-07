"""
pluginName = slowmo

Senario When motion tracking triggered take a slow motion video 
---------------------------------------------------------------
You have a project where you want to capture a slow motion video
sequence.  This plugin will monitor the camera view using motion
tracking and tigger a video at a high fps.  640x480 at 90 fps
This would be suitable for example capturing humming birds or other
fast moving objects in the camera view. Note this configuration
is setup to exit after 10 videos per motionNumMax and motionNumRecycle=False

NOTE:  Slow Motion can also be done using videoRepeatOn=True (dashcam mode)
but would Not be triggered by motion but would run a series of
slow motion videos when manually started.  

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=slowmo
then these settings will override the config.py settings.
"""
# Customize Settings Below to Suit your Project Needs
# ---------------------------------------------------

imageNamePrefix = 'slow-'    # default= 'slow-' for all image file names. Eg garage-
imageVFlip = False           # default= False True Flips image Vertically
imageHFlip = False           # default= False True Flips image Horizontally
showDateOnImage = False      # default= True False=Do Not display date/time text on images

motionPrefix = "mo-"         # default= "mo-" Prefix for all Motion Detect images
motionDir = "media/slowmo"   # default= "media/slowmo"  Folder Path for Motion Detect Image Storage
motionVideoTimer = 30        # default= 30 seconds of video clip to take if Motion Detected
motionNumOn = True           # default= False  True=filenames by sequenced Number  False=filenames by date/time
# Use settings below if motionNumOn = True
motionNumRecycle = False     # default= True when NumMax reached restart at NumStart instead of exiting
motionNumStart = 1000        # default= 1000 Start 0f motion number sequence
motionNumMax  = 10           # default= 0 Max number of motion images desired. 0=Continuous

# Manage Disk Space Settings
#---------------------------
spaceTimerHrs = 1            # default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500            # default= 500  Target Free space in MB Required.
spaceMediaDir = motionDir    # default= motion per variable above
spaceFileExt  = 'mp4'        # default= 'mp4' File extension to Delete Oldest Files

# Do Not Change these Settings
# ----------------------------
imageWidth = 640              # default= 640 Full Size Image Width in px
imageHeight = 480             # default= 480  Full Size Image Height in px
motionVideoFPS = 90           # default= 90  If image size reduced to 640x480 then slow motion is possible at 90 fps
motionTrackOn = True          # Turn on Motion Tracking
motionVideoOn = True          # Take images
motionQuickTLOn = False       # Turn on motion timelapse sequence mode
motionTrackQuickPic = False   # Turn off quick picture from video stream
timelapseOn = False           # Turn off normal time lapse mode so only motion mode used.
videoRepeatOn = False         # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
motionForce = 0               # Do not force motion image if no motion for a period of time
motionSubDirMaxHours = 0      # 0=off or specify Max Hrs to create new sub-folder if HrsMax exceeded
motionSubDirMaxFiles = 0      # 0=off or specify MaxFiles before a new sub-folder created
motionRecentMax = 0           # 0=off  Maintain specified number of most recent files in motionRecentDir