"""
pluginName = TLShort

Senario Short Timelapse Project
-------------------------------
This setup will save images in number sequence in case date/time is not maintained
due to a reboot and no internet NTP server is available.  It will Not create subfolders.
Depending on the full duration of the timelapse sequence it is advised saving files to 
an attached hard drive or USB memory stick.  Due to the short nature no subfolders
will be created.

Edit the settings below to suit your project needs.
if config.py variable pluginEnable=True and pluginName=TLshort
then these settings will override the config.py settings.

"""

# Customize settings below to suit your project needs
# ---------------------------------------------------
verbose = False               # default= True Sends logging Info to Console. False if running script as daeman

imageNamePrefix = 'short-'    # default= 'short-' for all image file names. Eg garage-
imageWidth = 1920             # default= 1920 Full Size Image Width in px
imageHeight = 1080            # default= 1080  Full Size Image Height in px
imageJpegQuality = 5          # default = 5  Valid jpg encoder quality values 1(high) - 40(low)
imageVFlip = True             # default= False True Flips image Vertically
imageHFlip = True             # default= False True Flips image Horizontally
showDateOnImage = False       # default= True False=Do Not display date/time text on images

# Time Lapse Settings
# -------------------
timelapseDir = "media/TLshort" # default= "media/timelapse"  Storage Folder Path for Time Lapse Image Storage
timelapsePrefix = "tl-"       # default= "tl-" Prefix for All timelapse images with this prefix
timelapseTimer = 15           # default= 15 Seconds between timelapse images
timelapseNumOn = True         # default= True filenames Sequenced by Number False=filenames by date/time
timelapseNumRecycle = False   # default= True Restart Numbering at NumStart  False= Surpress Timelapse at NumMax
timelapseNumStart = 10000     # default= 1000 Start of timelapse number sequence
timelapseNumMax = 0           # default= 2000 Max number of timelapse images desired. 0=Continuous
timelapseExitSec = 0          # default= 0 seconds Surpress Timelapse after specified Seconds  0=Continuous
timelapseMaxFiles = 0         # 0=off or specify MaxFiles to maintain then oldest are deleted  default=0 (off)
timelapseSubDirMaxHours = 0   # 0=off or specify MaxHours - Creates New dated sub-folder if MaxHours exceeded
timelapseSubDirMaxFiles = 0   # 0=off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded
timelapseRecentMax = 100      # 0=off or specify number of most recent files to save in timelapseRecentDir
timelapseRecentDir = "media/recent/TLshort"  # default= "media/recent/TLshort"  location of timelapseRecent files

# Manage Disk Space Settings
#---------------------------
spaceTimerHrs = 0             # default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500             # default= 500  Target Free space in MB Required.
spaceMediaDir = timelapseDir  # default= timelapseDir  Starting point for directory walk
spaceFileExt  = 'jpg'         # default= 'jpg' File extension to Delete Oldest Files

# Do Not Change These Settings
# ----------------------------
timelapseOn = True            # default= False True=Turn timelapse On, False=Off
motionTrackOn = False         # Turn on Motion Tracking
motionQuickTLOn = False       # Turn on motion timelapse sequence mode
motionVideoOn = False         # Take images not video
motionTrackQuickPic = False   # Turn off quick picture from video stream
videoRepeatOn = False         # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
motionForce = 0               # Do not force motion image if no motion for a period of time
