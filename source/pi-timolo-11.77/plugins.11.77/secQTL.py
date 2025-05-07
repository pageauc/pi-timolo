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

motionQuickTLTimer = 30       # On motion do timelapse sequence for 60 minutes
motionQuickTLInterval =  0    # Take image every as fast as possible until timer runs out

imageNamePrefix = 'QTL-'      # default= 'QTL-' for all image file names. Eg garage-
imageWidth = 1920             # default= 1920 Full Size Image Width in px
imageHeight = 1080            # default= 1080  Full Size Image Height in px
imageVFlip = False            # default= False True Flips image Vertically
imageHFlip = False            # default= False True Flips image Horizontally
showDateOnImage = False       # default= True False=Do Not display date/time text on images

motionPrefix = "mo-"          # default= "mo-" Prefix for all Motion Detect images
motionDir = "media/secQTL"    # default= "media/secQTL"  Folder Path for Motion Detect Image Storage
motionNumOn = True            # default= True  True=filenames by sequenced Number  False=filenames by date/time
motionNumRecycle = True       # default= True when NumMax reached restart at NumStart instead of exiting
motionNumStart = 1000         # default= 1000 Start 0f motion number sequence
motionNumMax  = 5000          # default= 5000 Max number of motion images desired. 0=Continuous

# Manage subfolders
# -----------------
motionSubDirMaxHours = 0      # 0=off or specify Max Hrs to create new sub-folder if HrsMax exceeded
motionSubDirMaxFiles = 0      # 0=off or specify MaxFiles before a new sub-folder created
motionRecentMax = 100         # 0=off  Maintain specified number of most recent files in motionRecentDir
motionRecentDir = "media/recent/secQTL"  # default= "media/recent/secQTL"  Location of motionRecent files


# Do Not Change These Settings
# ----------------------------
motionTrackOn = True          # Turn on Motion Tracking
motionQuickTLOn = True        # Turn on motion timelapse sequence mode
motionVideoOn = False         # Take images not video
motionTrackQuickPic = False   # Turn off quick picture from video stream
timelapseOn = False           # Turn off normal time lapse mode so only motion mode used.
videoRepeatOn = False         # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
motionForce = 0               # Do not force motion image if no motion for a period of time
