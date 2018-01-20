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

# Customize Settings Below to Suit your Project Needs
# ---------------------------------------------------

imageNamePrefix = 'HD-'        # default= 'HD-' for all image file names. Eg garage-
motionPrefix = "mo-"           # default= "mo-" Prefix for all Motion Detect images
motionDir = "media/secstill"   # default= "media/secstill"  Folder Path for Motion Detect Image Storage
motionStartAt = ""             # default= "" Off or Specify date/time to Start Sequence Eg "01-jan-20018 08:00:00" or "20:00:00"

imageWidth = 1920              # default= 1920 Full Size Image Width in px
imageHeight = 1080             # default= 1080  Full Size Image Height in px
imageVFlip = False             # default= False True Flips image Vertically
imageHFlip = False             # default= False True Flips image Horizontally
showDateOnImage = True         # default= True False=Do Not display date/time text on images

motionNumOn = False            # default= True  True=filenames by sequenced Number  False=filenames by date/time
# Use settings below if motionNumOn = True
motionNumRecycle = False       # default= False (off) True= Restart at NumStart when motionNumMax reached
motionNumStart = 10000         # default= 10000 Start 0f motion number sequence
motionNumMax  = 0              # default= 0 (0=Continuous) os specify Max number of motion images desired. 

# Manage subfolders
# -----------------
motionSubDirMaxHours = 0       # 0=off or specify Max Hrs to create new sub-folder if HrsMax exceeded
motionSubDirMaxFiles = 1000    # 0=off or specify Max Files to create new sub-folder if FilesMax exceeded
motionRecentMax = 40           # 0=off  Maintain specified number of most recent files in motionRecentDir
motionRecentDir = "media/recent/secstill"  # default= "media/recent/secstill"  Location of motionRecent files

# Manage Disk Space Settings
#---------------------------
spaceTimerHrs = 1           # default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500           # default= 500  Target Free space in MB Required.
spaceMediaDir = motionDir   # default= motion per variable above
spaceFileExt  = 'jpg'       # default= 'mp4' File extension to Delete Oldest Files

# Do Not Change these Settings
# ----------------------------
motionTrackOn = True          # Turn on Motion Tracking
motionVideoOn = False         # Take images
motionQuickTLOn = False       # Turn on motion timelapse sequence mode
motionTrackQuickPic = False   # Turn off quick picture from video stream
timelapseOn = False           # Turn off normal time lapse mode so only motion mode used.
videoRepeatOn = False         # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
motionForce = 0               # Do not force motion image if no motion for a period of time
