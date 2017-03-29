# User Configuration variable settings for pitimolo
# Purpose - Motion Detection Security Cam
# Created - 20-Jul-2015 pi-timolo ver 4.02 compatible or greater
# Done by - Claude Pageau
 
configTitle = "pi-timolo Default Config Settings"
configName = "pi-timolo-default-config"

#======================================
#       pi-timolo.py Settings
#======================================

# These settings should be False if this script is run as a background /etc/rc.local
verbose = True             # Sends detailed logging info to console. set to False if running script as daeman
logDataToFile = False      # logs diagnostic data to a disk file for review  default=False
debug = False              # Puts in debug mode returns pixel average data for tuning

# print a test image
imageTestPrint = False     # default=False Set to True to print one image and exit (useful for aligning camera)

# Image Settings
imageNamePrefix = 'cam1-'  # Prefix for all image file names. Eg front-
imageWidth = 1024          # Full Size Image Width in px  default=1024
imageHeight = 768          # Full Size Image Height in px default=768
imageVFlip = False         # Flip image Vertically    default=False
imageHFlip = False         # Flip image Horizontally  default=False
imageRotation = 0          # Rotate image. Valid values: 0, 90, 180 & 270
noNightShots = False       # Don't Take images at Night default=False
noDayShots = False         # Don't Take images during day time default=False
imagePreview = False       # Preview image on connected RPI Monitor default=False
useVideoPort = True        # Use the video port to capture motion images - faster than the image port. Default=False

# Low Light Night Settings
twilightThreshold = 20     # default=35 Light level to trigger day/night transition at twilight
nightSleepSec = 25         # default=20 Sec - Time period to allow camera to calculate low light AWB
nightMaxShut = 5.5         # default=5.5 sec Highest cam shut exposure time.
                           # IMPORTANT 6 sec works sometimes but occasionally locks RPI and HARD reboot required to clear
nightMinShut = .002        # default=.002 sec Lowest camera shut exposure time for transition from day to night (or visa versa)
nightMaxISO = 800          # default=800  Max cam ISO night setting
nightMinISO = 100          # lowest ISO camera setting for transition from day to night (or visa versa)

# Date/Time Settings for Displaying info Directly on Images
showTextFontSize = 18      # Size of image Font in pixel height
showDateOnImage = True     # Set to False for No display of date/time on image default= True
showTextBottom = True      # Location of image Text True=Bottom False=Top
showTextWhite = True       # Colour of image Text True=White False=Black
showTextWhiteNight = True  # Change night text to white.  Might help if night needs white instead of black during day or visa versa

# Motion Detect Settings
motionOn = True            # True = motion capture is turned on.  False= No motion detection
motionPrefix = "mo-"       # Prefix Motion Detection images
motionDir = "media/motion"       # Storage Folder for Motion Detect Images
threshold = 35             # How much a pixel has to change to be counted default=35 (1-200)
sensitivity = 100          # Number of changed pixels to trigger motion default=100
motionAverage = 20         # Number of images to average for motion verification: 1=last image only or 100=Med 300=High Average Etc.
motionVideoOn = False      # If set to True then video clip is taken rather than image
motionVideoTimer = 10      # Number of seconds of video clip to take if Motion Detected default=10
motionQuickTLOn = False    # if set to True then take a quick time lapse sequence rather than a single image (overrides motionVideoOn)
motionQuickTLTimer = 10    # Duration in seconds of quick time lapse sequence after initial motion detected default=10
motionQuickTLInterval = 0  # Time between each Quick time lapse image 0 is fast as possible
motionForce = 3600         # Force single motion image if no Motion Detected in specified seconds.  default=3600 1 hr
motionNumOn = True         # True=On (filenames by sequenced Number) otherwise date/time used for filenames
motionNumStart = 1000      # Start motion number sequence
motionNumMax  = 500        # Max number of motion images desired. 0=Continuous    default=0
motionNumRecycle = True    # After numberMax reached restart at numberStart instead of exiting default=True
motionMaxDots = 100        # Number of motion dots before starting new line
createLockFile = False     # default=False if True then sync.sh will call gdrive to sync files to your web google drive if .sync file exists
                           # Lock File is used to indicate motion images are added so sync.sh can sync in background via sudo crontab -e

# Time Lapse Settings
timelapseOn = False        # Turns timelapse True=On  False=Off
timelapsePrefix = "tl-"    # Prefix timelapse images with this prefix
timelapseDir = "media/timelapse" # Storage Folder for Time Lapse Images
timelapseTimer = 300       # Seconds between timelapse images  default=300 5 min
timelapseNumOn = True      # True=On (filenames Sequenced by Number) otherwise date/time used for filename
timelapseNumStart = 1000   # Start of timelapse number sequence
timelapseNumMax = 2000     # Max number of timelapse images desired. 0=Continuous  default=2000
timelapseNumRecycle = True # After numberMax reached restart at numberStart instead of exiting default=True
timelapseExit = 0          # Will Quit program after specified seconds 0=Continuous  default=0

#======================================
#       webserver.py Settings
#======================================

# Left iFrame Image Settings
web_image_height = "768"       # px height of images to display in iframe default 768
web_iframe_width_usage = "75%" # Left Pane - Sets % of total screen width allowed for iframe. Rest for right list
web_iframe_width = "100%"      # Desired frame width to display images. can be eg percent "80%" or px "1280"
web_iframe_height = "100%"     # Desired frame height to display images. Scroll bars if image larger (percent or px)

# Right Side Files List
web_max_list_entries = 0         # 0 = All or Specify Max right side file entries to show (must be > 1)
web_list_height = web_image_height  # Right List - side menu height in px (link selection)
web_list_by_datetime = True      # True=datetime False=filename
web_list_sort_descending = True  # reverse sort order (filename or datetime per show_by_date setting

# Web Server settings
web_server_root = "media"     # webserver root path to webserver image folder
web_server_port = 8080        # Web server access port eg http://192.168.1.100:8090
web_page_title = "Pi-Timolo Media"     # web page title that browser show (not displayed on web page)
web_page_refresh_on = True    # False=Off (never)  Refresh True=On (per seconds below)
web_page_refresh_sec = "180"  # seconds to wait for web page refresh default=180 seconds (three minutes)
web_page_blank = False        # Start left image with a blank page until a right menu item is selected
                              # Otherwise False displays second list[1] item since first may be in progress

# ---------------------------------------------- End of User Variables -----------------------------------------------------
