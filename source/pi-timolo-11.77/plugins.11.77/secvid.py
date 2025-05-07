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

imageNamePrefix = 'vid-'       # default= 'vid-' for all image file names. Eg garage-
motionPrefix = "mo-"           # default= "mo-" Prefix for all Motion Detect images
motionDir = "media/secvid"     # default= "media/secvid"  Folder Path for Motion Detect Image Storage
motionStartAt = ""             # default= "" Off or Specify date/time to Start Sequence Eg "01-jan-20018 08:00:00" or "20:00:00"

imageWidth = 1280              # default= 1280 Full Size Image Width in px
imageHeight = 720              # default= 720  Full Size Image Height in px
imageVFlip = False             # default= False True Flips image Vertically
imageHFlip = False             # default= False True Flips image Horizontally
showDateOnImage = True         # default= True False=Do Not display date/time text on images

motionVideoFPS = 25            # default= 25 If image size reduced to 640x480 then slow motion is possible at 90 fps
motionVideoTimer = 10          # default= 10 seconds of video clip to take if Motion Detected
motionNumOn = False            # default= False  True=filenames by sequenced Number  False=filenames by date/time
# Use settings below if motionNumOn = True
motionNumRecycle = False       # default= True when NumMax reached restart at NumStart instead of exiting
motionNumStart = 1000          # default= 1000 Start 0f motion number sequence
motionNumMax  = 0              # default= 0 Max number of motion images desired. 0=Continuous

# Manage subfolders
# -----------------
motionSubDirMaxHours = 0       # 0=off or specify Max Hrs to create new sub-folder if HrsMax exceeded
motionSubDirMaxFiles = 0       # 0=off or specify MaxFiles before a new sub-folder created
motionRecentMax = 0            # 0=off  Maintain specified number of most recent files in motionRecentDir
motionRecentDir = "media/recent/secvid"  # default= "media/recent/secstill"  Location of motionRecent files

# Manage Disk Space Settings
#---------------------------
spaceTimerHrs = 1           # default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500           # default= 500  Target Free space in MB Required.
spaceMediaDir = motionDir   # default= motion per variable above
spaceFileExt  = 'mp4'       # default= 'mp4' File extension to Delete Oldest Files

# Do Not Change these Settings
# ----------------------------
motionTrackOn = True          # Turn on Motion Tracking
motionVideoOn = True          # Take images
motionQuickTLOn = False       # Turn on motion timelapse sequence mode
motionTrackQuickPic = False   # Turn off quick picture from video stream
timelapseOn = False           # Turn off normal time lapse mode so only motion mode used.
videoRepeatOn = False         # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
motionForce = 0               # Do not force motion image if no motion for a period of time
