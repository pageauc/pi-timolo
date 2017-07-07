# User Configuration variable settings for pitimolo
# Purpose - Motion Detection Security Cam
# Updated - 20-Jun-2017 IMPORTANT - Required for pi-timolo.py ver 6.71 or Greater
# Done by - Claude Pageau

configTitle = "pi-timolo ver 6.71 Default Settings"
configName  = "config.py"

#======================================
#   pi-timolo.py ver 6.71 Settings
#======================================

# Logging and Debug Settings
# --------------------------
# Note - Set verbose to False if script is run in background or from /etc/rc.local
verbose = True             # default= True Sends logging Info to Console. False if running script as daeman
logDataToFile = False      # default= False True logs diagnostic data to a disk file for review
debug = False              # default= False True = debug mode returns pixel average data for tuning
imageTestPrint = False     # default= False Set to True to print one image and exit (useful for aligning camera)

# Image Settings
# --------------
imageNamePrefix = 'cam1-'  # default= 'cam1-' for all image file names. Eg garage-
imageWidth = 1024          # default= 1024 Full Size Image Width in px
imageHeight = 768          # default= 768  Full Size Image Height in px
imageFormat = ".jpg"       # default = ".jpg"  image Formats .jpeg .png .gif .bmp
imageJpegQuality = 20      # default = 20  Valid jpg encoder quality values 1(high) - 40(low)
imageVFlip = False         # default= False True Flips image Vertically
imageHFlip = False         # default= False True Flips image Horizontally
imageRotation = 0          # Default= 0  Rotate image. Valid values: 0, 90, 180, 270
noNightShots = False       # default= False True=No Night Images (Motion or Timelapse)
noDayShots = False         # default= False True=No Day Images (Motion or Timelapse)
imagePreview = False       # default= False True=Preview image on connected RPI Monitor
useVideoPort = False       # default= False True=Use the video port to capture motion images (faster than the image port).

# Date/Time Settings for Displaying info Directly on Images
# ---------------------------------------------------------
showDateOnImage = True     # default= True False=Do Not display date/time text on images
showTextFontSize = 18      # default= 18 Size of image Font in pixel height
showTextBottom = True      # Location of image Text True=Bottom False=Top
showTextWhite = True       # Colour of image Text True=White False=Black
showTextWhiteNight = True  # default=True Changes night text to white.  Useful if night needs white text instead of black

# Low Light Twilight and Night Settings
# -------------------------------------
nightTwilightThreshold = 90 # default= 90 dayPixAve where twilight starts (framerate_range shutter)
nightDarkThreshold = 50     # default= 50 dayPixAve where camera variable shutter long exposure starts
nightBlackThreshold = 4     # default= 4  dayPixAve where almost no light so Max settings used
nightSleepSec = 30          # default= 30 Sec - Time period to allow camera to calculate low light AWB
nightMaxShutSec = 5.9       # default= 5.9 Sec Highest V1 Cam shutter for long exposures V2=10 Sec.
nightMaxISO  = 800          # default= 800 Night ISO setting for Long Exposure below nightThreshold
nightDarkAdjust = 4.7       # default= 4.7 Factor to fine tune nightDarkThreshold brightness (lower is brighter)

# Motion Detect Settings
# ----------------------
motionOn = True             # default= True True=Turns Motion Detect On, False=Off
motionDir = "media/motion"  # default= "media/motion"  Folder Path for Motion Detect Image Storage
motionPrefix = "mo-"        # default= "mo-" Prefix for all Motion Detect images
motionCamSleep = 0.7        # default= 0.7 Sec of day sleep so camera can measure AWB before taking photo
motionStreamOn = False      # default= False  True=Use video stream thread for Faster motion detect best on quad core
motionStreamStopSec = 0.5   # default= 0.5 seconds  Time to close stream thread
motionAverage = 20          # default= 20 Num Images to Average for motion verification: 1=last image only, 100=Med, 300=High, Etc.
motionThreshold = 50        # default= 50 (1-200)  How much a pixel has to change to be counted
motionSensitivity = 100     # default= 100 Number of changed pixels to trigger motion image
motionVideoOn = False       # default= False  True=Take a video clip rather than image
motionVideoTimer = 10       # default= 10 seconds of video clip to take if Motion Detected
motionQuickTLOn = False     # default= False  True=Take a quick time lapse sequence rather than a single image (overrides motionVideoOn)
motionQuickTLTimer = 10     # default= 10 Duration in seconds of quick time lapse sequence after initial motion detected
motionQuickTLInterval = 0   # default= 0 seconds between each Quick time lapse image. 0 is fast as possible
motionForce = 3600          # default= 3600 seconds (1 hr) Force single motion image if no Motion Detected in specified seconds.
motionNumOn = True          # default= True  True=filenames by sequenced Number  False=filenames by date/time
motionNumRecycle = True     # default= True when NumMax reached restart at NumStart instead of exiting
motionNumStart = 1000       # default= 1000 Start 0f motion number sequence
motionNumMax  = 500         # default= 0 Max number of motion images desired. 0=Continuous
motionDotsOn = True         # default= True Displays motion loop progress dots if verbose=True False=Non
motionDotsMax = 100         # default= 100 Number of motion dots before starting new line if motionDotsOn=True
motionSubDirMaxHours = 0    # 0=off or specify Max Hrs to create new sub-folder if HrsMax exceeded
motionSubDirMaxFiles = 0    # 0=off or specify Max Files to create new sub-folder if FilesMax exceeded
motionRecentMax = 10        # 0=off  Maintain specified number of most recent files in motionRecentDir
motionRecentDir = "media/recent/motion"  # default= "media/recent/motion"  Location of motionRecent files

createLockFile = False      # default= False True=Create pi-timolo.sync file whenever images saved.
                            # Lock File is used to indicate motion images have been added
                            # so sync.sh can sync in background via sudo crontab -e

# Time Lapse Settings
# -------------------
timelapseOn = True          # default= False True=Turn timelapse On, False=Off
timelapseDir = "media/timelapse" # default= "media/timelapse"  Storage Folder Path for Time Lapse Image Storage
timelapsePrefix = "tl-"     # default= "tl-" Prefix for All timelapse images with this prefix
timelapseCamSleep = 4.0     # default= 4.0 seconds day sleep so camera can measure AWB before taking photo
timelapseTimer = 300        # default= 300 (5 min) Seconds between timelapse images
timelapseNumOn = True       # default= True filenames Sequenced by Number False=filenames by date/time
timelapseNumRecycle = True  # default= True Restart Numbering at NumStart  False= Surpress Timelapse at NumMax
timelapseNumStart = 1000    # default= 1000 Start of timelapse number sequence
timelapseNumMax = 2000      # default= 2000 Max number of timelapse images desired. 0=Continuous
timelapseExitSec = 0        # default= 0 seconds Surpress Timelapse after specified Seconds  0=Continuous
timelapseMaxFiles = 0       # 0=off or specify MaxFiles to maintain then oldest are deleted  default=0 (off)
timelapseSubDirMaxHours = 0 # 0=off or specify MaxHours - Creates New dated sub-folder if MaxHours exceeded
timelapseSubDirMaxFiles = 0 # 0=off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded
timelapseRecentMax = 10     # 0=off or specify number of most recent files to save in timelapseRecentDir
timelapseRecentDir = "media/recent/timelapse"  # default= "media/recent/timelapse"  location of timelapseRecent files

# Video Repeat Mode (suppresses Timelapse and Motion Settings)
# -----------------
videoRepeatOn = False       # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
videoPath = "media/videos"  # default= media/videos Storage folder path for videos
videoPrefix = "vid-"        # prefix for video filenames
videoDuration = 120         # default= 120 seconds for each video recording
videoTimer = 60             # default= 60 minutes  Run Recording Session then Exit  0=Continuous
videoNumOn = False          # default= True True=filenames by sequence Number  False=filenames by date/time
videoNumRecycle = False     # default= False when NumMax reached restart at NumStart instead of exiting
videoNumStart = 100         # default= 100 Start of video filename number sequence
videoNumMax  = 20           # default= 20 Max number of videos desired. 0=Continuous

# Manage Disk Space Settings
#---------------------------
spaceTimerHrs = 0           # default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500           # default= 500  Target Free space in MB Required.
spaceMediaDir = '/home/pi/pi-timolo/media'  # default= '/home/pi/pi-timolo/media'  Starting point for directory walk
spaceFileExt  = 'jpg'       # default= 'jpg' File extension to Delete Oldest Files

#======================================
#       webserver.py Settings
#======================================

# Web Server settings
# -------------------
web_server_port = 8080        # default= 8080 Web server access port eg http://192.168.1.100:8080
web_server_root = "media"     # default= "media" webserver root path to webserver image/video sub-folders
web_page_title = "Pi-Timolo Media"  # web page title that browser show (not displayed on web page)
web_page_refresh_on = True    # False=Off (never)  Refresh True=On (per seconds below)
web_page_refresh_sec = "180"  # default= "180" seconds to wait for web page refresh  seconds (three minutes)
web_page_blank = False        # True Starts left image with a blank page until a right menu item is selected
                              # False displays second list[1] item since first may be in progress

# Left iFrame Image Settings
# --------------------------
web_image_height = "768"       # default= "768" px height of images to display in iframe
web_iframe_width_usage = "75%" # Left Pane - Sets % of total screen width allowed for iframe. Rest for right list
web_iframe_width = "100%"      # Desired frame width to display images. can be eg percent "80%" or px "1280"
web_iframe_height = "100%"     # Desired frame height to display images. Scroll bars if image larger (percent or px)

# Right Side Files List
# ---------------------
web_max_list_entries = 0         # 0 = All or Specify Max right side file entries to show (must be > 1)
web_list_height = web_image_height  # Right List - side menu height in px (link selection)
web_list_by_datetime = True      # True=datetime False=filename
web_list_sort_descending = True  # reverse sort order (filename or datetime per web_list_by_datetime setting


# ---------------------------------------------- End of User Variables -----------------------------------------------------
