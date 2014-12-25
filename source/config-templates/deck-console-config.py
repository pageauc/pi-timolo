# User Configuration variable settings for pitimolo
# Purpose - Motion Detection Security Cam
# Created - 13-Dec-2014
# Done by - Claude Pageau
 
configTitle = "Texas Deck Security Cam Motion Only with 1080 images"
configName = "deck-config.py"

# print a test image
imageTestPrint = False     # default=False Set to True to print one image and exit (useful for aligning camera)

# Image Settings
imageNamePrefix = 'deck-' # Prefix for all image file names. Eg front-
imageWidth = 1920          # Full Size Image Width in px  default=1980
imageHeight = 1080         # Full Size Image Height in px default=1080
imageVFlip = False         # Flip image Vertically    default=False
imageHFlip = False         # Flip image Horizontally  default=False
imagePreview = False       # Preview image on connected RPI Monitor default=False

# Low Light Night Settings
nightMaxShut = 5.5         # default=5 sec Highest cam shut exposure time. IMPORTANT 6 sec works sometimes but occasionally locks RPI and HARD reboot required to clear
nightMinShut = .10         # default=.10 sec Lowest camera shut exposure time for transition from day to night (or visa versa)
nightMaxISO = 800          # default=800  Max cam ISO night setting
nightMinISO = 100          # lowest ISO camera setting for transition from day to night (or visa versa)  
nightSleepSec = 10         # default=10 Sec - Time period to allow camera to calculate low light AWB   
nightDayTimer = 2 * 60     # Check stream changes to determine if entering twilight zones
sunsetThreshold = 90       # If in Day and pixAverage below this then time to ram to switch to low light mode and ramp settings
sunriseThreshold = 220     # If in Night and pixAverage below this then time to ramp low light settings

# Settings for Displaying Date/Time Stamp Directly on Images
showDateOnImage = True     # Set to False for No display of date/time on image default= True
showTextBottom = True      # Location of image Text True=Bottom False=Top
showTextWhite = False      # Colour of image Text True=White False=Black
showTextWhiteNight= True   # Change night text to white.  Might help if night needs white instead of black during day or visa versa

# Motion Settings
motionOn = True            # True = motion capture is turned on.  False= No motion detection
motionPrefix = "tx-"       # Prefix Motion Detection images
motionDir = "motion"       # Storage Folder for Motion Detect Images
threshold = 10             # How much a pixel has to change to be counted default=10 (1-200)
sensitivity = 400          # Number of changed pixels to trigger motion default=300
motionVideoOn = False      # If set to True then video clip is taken rather than image
motionVideoTimer = 30      # Number of seconds of video clip to take if Motion Detected
motionForce = 60 * 60      # One Hour Force image if no Motion Detected.  default=60*60
motionNumOn = True         # True=On (filenames Sequenced by Number) otherwise date/time used for filename
motionNumStart = 1000      # Start motion number sequence
motionNumMax  = 500        # Max number of motion images desired. 0=Continuous    default=0
motionNumRecycle = True    # After numberMax reached restart at numberStart instead of exiting default=True
motionMaxDots = 50         # Number of motion dots before starting new line
createLockFile = False     # default=False if True then sync.sh will call grive to sync files to your web google drive if .sync file exists
                           # Lock File is used to indicate motion images are added so sync.sh can sync in background via sudo crontab -e 

# TimeLapse Settings
timelapseOn = False        # Turns timelapse True=On  False=Off
timelapseTimer = 5 * 60    # Seconds between timelapse images
timelapseDir = "timelapse" # Storage Folder for Time Lapse Images
timelapsePrefix = "tl-"    # Prefix timelapse images with this prefix
timelapseExit = 0 * 60     # Will Quit program after specified seconds 0=Continuous  Default=0
timelapseNumOn = True      # True=On (filenames Sequenced by Number) otherwise date/time used for filename
timelapseNumStart = 1000   # Start of timelapse number sequence 
timelapseNumMax = 1000     # Max number of timelapse images desired. 0=Continuous  default=0
timelapseNumRecycle = True # After numberMax reached restart at numberStart instead of exiting default=True   

# ---------------------------------------------- End of User Variables -----------------------------------------------------
