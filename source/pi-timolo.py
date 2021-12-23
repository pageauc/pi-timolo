#!/usr/bin/python
'''
pi-timolo - Raspberry Pi Long Duration Timelapse, Motion Tracking,
with Low Light Capability
written by Claude Pageau Jul-2017 (release 7.x)
This release uses OpenCV to do Motion Tracking.
It requires updated config.py
Oct 2020 Added panoramic pantilt option plus other improvements.
'''
from __future__ import print_function
PROG_VER = "ver 12.16"  # Requires Latest 12.0 release of config.py
__version__ = PROG_VER  # May test for version number at a future time

import os
WARN_ON = False   # Add short delay to review warning messages
MY_PATH = os.path.abspath(__file__) # Find the full path of this python script
# get the path location only (excluding script name)
BASE_DIR = os.path.dirname(MY_PATH)
BASE_FILENAME = os.path.splitext(os.path.basename(MY_PATH))[0]
PROG_NAME = os.path.basename(__file__)
LOG_FILE_PATH = os.path.join(BASE_DIR, BASE_FILENAME + ".log")
HORIZ_LINE = '-------------------------------------------------------'
print(HORIZ_LINE)
print('%s %s  written by Claude Pageau' % (PROG_NAME, PROG_VER))
print(HORIZ_LINE)
print('Loading Wait ....')

# import python library modules
import datetime
import logging
import sys
import subprocess
import shutil
import glob
import time
import math
from threading import Thread
from fractions import Fraction
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# Attempt to import dateutil
try:
    from dateutil.parser import parse
except ImportError:
    print("WARN : Could Not Import dateutil.parser")
    print("       Disabling TIMELAPSE_START_AT, MOTION_START_AT and VideoStartAt")
    print("       See https://github.com/pageauc/pi-timolo/wiki/Basic-Trouble-Shooting#problems-with-python-pip-install-on-wheezy")
    WARN_ON = True
    # Disable get_sched_start if import fails for Raspbian wheezy or Jessie
    TIMELAPSE_START_AT = ""
    MOTION_START_AT = ""
    VIDEO_START_AT = ""

# Attempt to import pyexiv2.  Note python3 can be a problem
try:
    # pyexiv2 Transfers image exif data to writeTextToImage
    # For python3 install of pyexiv2 lib
    # See https://github.com/pageauc/pi-timolo/issues/79
    # Bypass pyexiv2 if library Not Found
    import pyexiv2
except ImportError:
    print("WARN  : Could Not Import pyexiv2. Required for Saving Image EXIF meta data")
    print("        If Running under python3 then Install pyexiv2 library for python3 per")
    print("        cd ~/pi-timolo")
    print("        ./install-py3exiv2.sh")
    WARN_ON = True
except OSError as err:
    print("WARN  : Could Not import python3 pyexiv2 due to an Operating System Error")
    print("        %s" % err)
    print("        Camera images will be missing exif meta data")
    WARN_ON = True

'''
This is a dictionary of the default settings for pi-timolo.py
If you don't want to use a config.py file these will create the required
variables with default values.  Change dictionary values if you want different
variable default values.
A message will be displayed if a variable is Not imported from config.py.
Note: plugins can override default and config.py values if plugins are
      enabled.  This happens after config.py variables are initialized
'''

default_settings = {
    'CONFIG_FILENAME':'default_settings',
    'CONFIG_TITLE':'No config.py so using internal dictionary settings',
    'PLUGIN_ON':False,
    'PLUGIN_NAME':"shopcam",
    'VERBOSE_ON':True,
    'LOG_TO_FILE_ON':False,
    'DEBUG_ON':False,
    'IMAGE_NAME_PREFIX':'cam1-',
    'IMAGE_WIDTH':1920,
    'IMAGE_HEIGHT':1080,
    'IMAGE_FORMAT':".jpg",
    'IMAGE_JPG_QUAL':95,
    'IMAGE_ROTATION':0,
    'IMAGE_VFLIP':True,
    'IMAGE_HFLIP':True,
    'IMAGE_GRAYSCALE':False,
    'IMAGE_PREVIEW':False,
    'IMAGE_NO_NIGHT_SHOTS':False,
    'IMAGE_NO_DAY_SHOTS':False,
    'IMAGE_SHOW_STREAM':False,
    'STREAM_WIDTH':320,
    'STREAM_HEIGHT':240,
    'STREAM_FPS':20,
    'STREAM_STOP_SEC': 0.7,
    'SHOW_DATE_ON_IMAGE':True,
    'SHOW_TEXT_FONT_SIZE':18,
    'SHOW_TEXT_BOTTOM':True,
    'SHOW_TEXT_WHITE':True,
    'SHOW_TEXT_WHITE_NIGHT':True,
    'NIGHT_TWILIGHT_MODE_ON':True,
    'NIGHT_TWILIGHT_THRESHOLD':90,
    'NIGHT_DARK_THRESHOLD':50,
    'NIGHT_BLACK_THRESHOLD':4,
    'NIGHT_SLEEP_SEC':30,
    'NIGHT_MAX_SHUT_SEC':5.9,
    'NIGHT_MAX_ISO':800,
    'NIGHT_DARK_ADJUST':4.7,
    'TIMELAPSE_ON':True,
    'TIMELAPSE_DIR':"media/timelapse",
    'TIMELAPSE_PREFIX':"tl-",
    'TIMELAPSE_START_AT':"",
    'TIMELAPSE_TIMER_SEC':300,
    'TIMELAPSE_CAM_SLEEP_SEC':4.0,
    'TIMELAPSE_NUM_ON':True,
    'TIMELAPSE_NUM_RECYCLE_ON':True,
    'TIMELAPSE_NUM_START':1000,
    'TIMELAPSE_NUM_MAX':2000,
    'TIMELAPSE_EXIT_SEC':0,
    'TIMELAPSE_MAX_FILES':0,
    'TIMELAPSE_SUBDIR_MAX_FILES':0,
    'TIMELAPSE_SUBDIR_MAX_HOURS':0,
    'TIMELAPSE_RECENT_MAX':40,
    'TIMELAPSE_RECENT_DIR':"media/recent/timelapse",
    'TIMELAPSE_PANTILT_ON':False,
    'TIMELAPSE_PANTILT_STOPS':[(90, 10),
                               (45, 10),
                               (0, 10),
                               (-45, 10),
                               (-90, 10),
                              ],
    'MOTION_TRACK_ON':True,
    'MOTION_TRACK_QUICK_PIC_ON':False,
    'MOTION_TRACK_INFO_ON':True,
    'MOTION_TRACK_TIMEOUT_SEC':0.3,
    'MOTION_TRACK_TRIG_LEN':75,
    'MOTION_TRACK_MIN_AREA':100,
    'MOTION_TRACK_QUICK_PIC_BIGGER':3.0,
    'MOTION_DIR':"media/motion",
    'MOTION_PREFIX':"mo-",
    'MOTION_START_AT':"",
    'MOTION_VIDEO_ON':False,
    'MOTION_VIDEO_FPS':15,
    'MOTION_VIDEO_TIMER_SEC':10,
    'MOTION_TRACK_MINI_TL_ON':False,
    'MOTION_TRACK_MINI_TL_SEQ_SEC':20,
    'MOTION_TRACK_MINI_TL_TIMER_SEC':4,
    'MOTION_FORCE_SEC':3600,
    'MOTION_NUM_ON':True,
    'MOTION_NUM_RECYCLE_ON':True,
    'MOTION_NUM_START':1000,
    'MOTION_NUM_MAX':500,
    'MOTION_SUBDIR_MAX_FILES':0,
    'MOTION_SUBDIR_MAX_HOURS':0,
    'MOTION_RECENT_MAX':40,
    'MOTION_RECENT_DIR':"media/recent/motion",
    'MOTION_DOTS_ON':False,
    'MOTION_DOTS_MAX':100,
    'MOTION_CAM_SLEEP':0.7,
    'CREATE_LOCKFILE':False,
    'VIDEO_REPEAT_ON':False,
    'VIDEO_DIR':"media/videos",
    'VIDEO_PREFIX':"vid-",
    'VIDEO_START_AT':"",
    'VIDEO_FILE_SEC':120,
    'VIDEO_SESSION_MIN':60,
    'VIDEO_FPS':30,
    'VIDEO_NUM_ON':False,
    'VIDEO_NUM_RECYCLE_ON':False,
    'VIDEO_NUM_START':100,
    'VIDEO_NUM_MAX':20,
    'PANTILT_ON':False,
    'PANTILT_IS_PIMORONI':False,
    'PANTILT_HOME':(0, -10),
    'PANO_ON':False,
    'PANO_DAYONLY_ON': True,
    'PANO_TIMER_SEC':160,
    'PANO_IMAGE_PREFIX':'pano-',
    'PANO_NUM_START':1000,
    'PANO_NUM_MAX':10,
    'PANO_NUM_RECYCLE':True,
    'PANO_PROG_PATH':'./image-stitching',
    'PANO_IMAGES_DIR':'./media/pano/images',
    'PANO_DIR':'./media/pano/panos',
    'PANO_CAM_STOPS':[(36, 10),
                      (0, 10),
                      (-36, 10),
                     ],
    'SPACE_TIMER_HOURS':0,
    'SPACE_TARGET_MB':500,
    'SPACE_MEDIA_DIR':'/home/pi/pi-timolo/media',
    'SPACE_TARGET_EXT':'jpg',
    'web_server_port':8080,
    'web_server_root':"media",
    'web_page_title':"PI-TIMOLO Media",
    'web_page_refresh_on':True,
    'web_page_refresh_sec':"900",
    'web_page_blank':False,
    'web_image_height':"768",
    'web_iframe_width_usage':"70%",
    'web_iframe_width':"100%",
    'web_iframe_height':"100%",
    'web_max_list_entries':0,
    'web_list_height':"768",
    'web_list_by_datetime':True,
    'web_list_sort_descending':True
    }

# Check for config.py variable file to import and error out if not found.
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.py")
if os.path.isfile(CONFIG_FILE_PATH):
    try:
        from config import CONFIG_TITLE
    except ImportError:
        print('\n           --- WARNING ---\n')
        print('pi-timolo.py ver 12.0 or greater requires an updated config.py')
        print('copy new config.py per commands below.\n')
        print('    cp config.py config.py.bak')
        print('    cp config.py.new config.py\n')
        print('config.py.bak will contain your previous settings')
        print('The NEW config.py has renamed variable names. If required')
        print('you will need to review previous settings and change')
        print('the appropriate NEW variable names using nano.\n')
        print('Note: ver 12.0 has added a pantilthat panoramic image stitching feature\n')
        print('    Press Ctrl-c to Exit and update config.py')
        print('                      or')
        text = raw_input('    Press Enter and Default Settings will be used.')
    try:
        # Read Configuration variables from config.py file
        from config import *
    except ImportError:
        print('WARN  : Problem Importing Variables from %s' % CONFIG_FILE_PATH)
        WARN_ON = True
else:
    print('WARN  : %s File Not Found. Cannot Import Configuration Variables.'
          % CONFIG_FILE_PATH)
    print('        Run Console Command Below to Download File from GitHub Repo')
    print('        wget -O config.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py')
    print('        or cp config.py.new config.py')
    print('        Will now use default_settings dictionary variable values.')
    WARN_ON = True

'''
Check if variables were imported from config.py. If not create variable using
the values in the default_settings dictionary above.
'''
for key, val in default_settings.items():
    try:
        exec(key)
    except NameError:
        print('WARN  : config.py Variable Not Found. Setting ' + key + ' = ' + str(val))
        exec(key + '=val')
        WARN_ON = True

if PANTILT_ON:
    if PANTILT_IS_PIMORONI:
        print('INFO  : Loading Pimoroni and compatible pantilthat driver ...')
        import pantilthat
    else:
        print('INFO  : Loading Waveshare and compatible pantilthat driver ...')
        from waveshare.pantilthat import PanTilt
        pantilthat = PanTilt()
    pan, tilt = PANTILT_HOME
    try:
        pantilthat.pan(pan)
        time.sleep(PANTILT_SLEEP_SEC)
        pantilthat.tilt(tilt)
        time.sleep(PANTILT_SLEEP_SEC)
        print('INFO  : Successfully imported pantilthat driver.')
        print('Loading Wait ...')
    except IOError:
        print('ERROR : Problem with pantilthat hardware\n')
        print('        Pimoroni and Waveshare compatible pantilthats are supported.\n')
        if PANTILT_IS_PIMORONI:
            print('        Try setting config.py PANTILT_IS_PIMORONI = False')
            print('        This will attempt to use the Waveshare (or compatible) pantilthat driver.')
        else:
            print('        Try setting config.py PANTILT_IS_PIMORONI = True')
            print('        This will attempt to use the Pimoroni(or compatible) pantilthat driver')
        print('\n        Then restart pi-timolo.py.  If this message persists your hardware may not work')
        print('        You may have to try changing driver details at line 270 in pi-timolo.py')
        print('        or set config.py PANTILT_ON = False to disable pantilt feature.')
        sys.exit(1)

# Setup Logging now that variables are imported from config.py/plugin
if LOG_TO_FILE_ON:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=LOG_FILE_PATH,
                        filemode='w')
elif VERBOSE_ON:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.CRITICAL,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

 # Check for user_motion_code.py file to import and error out if not found.
userMotionFilePath = os.path.join(BASE_DIR, "user_motion_code.py")
if not os.path.isfile(userMotionFilePath):
    print('WARN  : %s File Not Found. Cannot Import user_motion_code functions.' %
          userMotionFilePath)
    WARN_ON = True
else:
    # Read Configuration variables from config.py file
    try:
        motionCode = True
        import user_motion_code
    except ImportError:
        print('WARN  : Failed Import of File user_motion_code.py Investigate Problem')
        motionCode = False
        WARN_ON = True

# Give some time to read any warnings
if WARN_ON and VERBOSE_ON:
    print('')
    print('Please Review Warnings  Wait 10 sec ...')
    time.sleep(10)
    print('Loading Wait ....')

try:
    import cv2
except ImportError:
    if sys.version_info > (2, 9):
        logging.error("Failed to import cv2 opencv for python3")
        logging.error("Try installing opencv for python3")
        logging.error("See https://github.com/pageauc/opencv3-setup")
    else:
        logging.error("Failed to import cv2 for python2")
        logging.error("Try reinstalling per command")
        logging.error("sudo apt-get install python-opencv")
    logging.error("Exiting %s Due to Error", PROG_NAME)
    sys.exit(1)

try:
    from picamera import PiCamera
except ImportError:
    logging.error("Problem importing picamera module")
    logging.error("Try command below to import module")
    if sys.version_info > (2, 9):
        logging.error("sudo apt-get install python3-picamera")
    else:
        logging.error("sudo apt-get install python-picamera")
    logging.error("Exiting %s Due to Error", PROG_NAME)
    sys.exit(1)
from picamera.array import PiRGBArray
import picamera.array

# Check that pi camera module is installed and enabled
camResult = subprocess.check_output("vcgencmd get_camera", shell=True)
camResult = camResult.decode("utf-8")
camResult = camResult.replace("\n", "")
if (camResult.find("0")) >= 0:   # Was a 0 found in vcgencmd output
    logging.error("Pi Camera Module Not Found %s", camResult)
    logging.error("if supported=0 Enable Camera using command sudo raspi-config")
    logging.error("if detected=0 Check Pi Camera Module is Installed Correctly")
    logging.error("Exiting %s Due to Error", PROG_NAME)
    sys.exit(1)
else:
    # use raspistill to check maximum image resolution of attached camera module
    logging.info("Pi Camera Module is Enabled and Connected %s", camResult)
    logging.info('Checking Pi Camera Module Version Wait ...')
    import picamera
    with picamera.PiCamera() as camera:
        CAM_MAX_RESOLUTION = camera.MAX_RESOLUTION
    logging.info("PiCamera Max resolution is %s", CAM_MAX_RESOLUTION)
    CAM_MAX_WIDTH, CAM_MAX_HEIGHT = CAM_MAX_RESOLUTION.width, CAM_MAX_RESOLUTION.height
    if CAM_MAX_WIDTH == '3280':
        picameraVer = '2'
    else:
        picameraVer = '1'
    logging.info('PiCamera Module Hardware is Ver %s', picameraVer)

if PLUGIN_ON:     # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(BASE_DIR, "plugins")
    # Check if there is a .py at the end of PLUGIN_NAME variable
    if PLUGIN_NAME.endswith('.py'):
        PLUGIN_NAME = PLUGIN_NAME[:-3]    # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, PLUGIN_NAME + '.py')
    logging.info("pluginEnabled - loading PLUGIN_NAME %s", pluginPath)
    if not os.path.isdir(pluginDir):
        logging.error("plugin Directory Not Found at %s", pluginDir)
        logging.error("Rerun github curl install script to install plugins")
        logging.error("https://github.com/pageauc/pi-timolo/wiki/"
                      "How-to-Install-or-Upgrade#quick-install")
        logging.error("Exiting %s Due to Error", PROG_NAME)
        sys.exit(1)
    elif not os.path.isfile(pluginPath):
        logging.error("File Not Found PLUGIN_NAME %s", pluginPath)
        logging.error("Check Spelling of PLUGIN_NAME Value in %s",
                      CONFIG_FILE_PATH)
        logging.error("------- Valid Names -------")
        validPlugin = glob.glob(pluginDir + "/*py")
        validPlugin.sort()
        for entry in validPlugin:
            pluginFile = os.path.basename(entry)
            plugin = pluginFile.rsplit('.', 1)[0]
            if not ((plugin == "__init__") or (plugin == "current")):
                logging.error("        %s", plugin)
        logging.error("------- End of List -------")
        logging.error("Note: PLUGIN_NAME Should Not have .py Ending.")
        logging.error("or Rerun github curl install command.  See github wiki")
        logging.error("https://github.com/pageauc/pi-timolo/wiki/"
                      "How-to-Install-or-Upgrade#quick-install")
        logging.error("Exiting %s Due to Error", PROG_NAME)
        sys.exit(1)
    else:
        pluginCurrent = os.path.join(pluginDir, "current.py")
        try:    # Copy image file to recent folder
            logging.info("Copy %s to %s", pluginPath, pluginCurrent)
            shutil.copy(pluginPath, pluginCurrent)
        except OSError as err:
            logging.error('Copy Failed from %s to %s - %s',
                          pluginPath, pluginCurrent, err)
            logging.error("Check permissions, disk space, Etc.")
            logging.error("Exiting %s Due to Error", PROG_NAME)
            sys.exit(1)
        logging.info("Import Plugin %s", pluginPath)
        sys.path.insert(0, pluginDir)  # add plugin directory to program PATH
        from plugins.current import *
        try:
            if os.path.isfile(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.isfile(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
        except OSError as err:
            logging.warning("Failed Removal of %s - %s", pluginCurrentpyc, err)
            time.sleep(5)
else:
    logging.info("No Plugin Enabled per PLUGIN_ON=%s", PLUGIN_ON)

# Turn on VERBOSE_ON when DEBUG_ON mode is enabled
if DEBUG_ON:
    VERBOSE_ON = True

# Make sure image format extention starts with a dot
if not IMAGE_FORMAT.startswith('.', 0, 1):
    IMAGE_FORMAT = '.' + IMAGE_FORMAT

#==================================
#      System Variables
# Should Not need to be customized
#==================================
PIX_AVE_TIMER_SEC = 30     # Interval time for checking pixAverage Readings
SECONDS2MICRO = 1000000    # Used to convert from seconds to microseconds
NIGHT_MAX_SHUTTER = int(NIGHT_MAX_SHUT_SEC * SECONDS2MICRO)
# default=5 seconds IMPORTANT- 6 seconds works sometimes
# but occasionally locks RPI and HARD reboot required to clear
darkAdjust = int((SECONDS2MICRO/5.0) * NIGHT_DARK_ADJUST)
daymode = False            # default should always be False.
MOTION_PATH = os.path.join(BASE_DIR, MOTION_DIR)  # Store Motion images
# motion dat file to save currentCount

DATA_DIR = './data'
NUM_PATH_MOTION = os.path.join(DATA_DIR, MOTION_PREFIX + BASE_FILENAME + ".dat")
NUM_PATH_PANO = os.path.join(DATA_DIR, PANO_IMAGE_PREFIX + BASE_FILENAME + ".dat")
NUM_PATH_TIMELAPSE = os.path.join(DATA_DIR, TIMELAPSE_PREFIX + BASE_FILENAME + ".dat")

TIMELAPSE_PATH = os.path.join(BASE_DIR, TIMELAPSE_DIR)  # Store Time Lapse images
# timelapse dat file to save currentCount
LOCK_FILEPATH = os.path.join(BASE_DIR, BASE_FILENAME + ".sync")
# Colors for drawing lines
cvWhite = (255, 255, 255)
cvBlack = (0, 0, 0)
cvBlue = (255, 0, 0)
cvGreen = (0, 255, 0)
cvRed = (0, 0, 255)
LINE_THICKNESS = 1     # Thickness of opencv drawing lines
LINE_COLOR = cvWhite   # color of lines to highlight motion stream area

# Round image resolution to avoid picamera errors
if picameraVer == '2':
    imageWidthMax = 3280
    imageHeightMax = 2464
else:
    imageWidthMax = 2592
    imageHeightMax = 1944
logging.info('picamera ver %s Max Resolution is %i x %i',
             picameraVer, imageWidthMax, imageHeightMax)

# Round image resolution to avoid picamera errors
image_width = (IMAGE_WIDTH + 31) // 32 * 32
if image_width > imageWidthMax:
    image_width = imageWidthMax
image_height = (IMAGE_HEIGHT + 15) // 16 * 16

if image_height > imageHeightMax:
    image_height = imageHeightMax

stream_width = (STREAM_WIDTH + 31) // 32 * 32
if stream_width > imageWidthMax:
    stream_width = imageWidthMax
stream_height = (STREAM_HEIGHT + 15) // 16 * 16
if stream_height > imageHeightMax:
    stream_height = imageHeightMax
stream_framerate = STREAM_FPS  # camera framerate

# If camera being used inside where there is no twilight
# Reduce night threshold settings to reduce overexposures.
if not NIGHT_TWILIGHT_MODE_ON:
    NIGHT_TWILIGHT_THRESHOLD = 20
    NIGHT_DARK_THRESHOLD = 10
    NIGHT_BLACK_THRESHOLD = 4

# increase size of MOTION_TRACK_QUICK_PIC_ON image
bigImage = MOTION_TRACK_QUICK_PIC_BIGGER
bigImageWidth = int(stream_width * bigImage)
bigImageHeight = int(stream_height * bigImage)
TRACK_TRIG_LEN = MOTION_TRACK_TRIG_LEN  # Pixels moved to trigger motion photo
# Don't track progress until this Len reached.
TRACK_TRIG_LEN_MIN = int(MOTION_TRACK_TRIG_LEN / 6)
# Set max overshoot triglen allowed half cam height
TRACK_TRIG_LEN_MAX = int(stream_height / 2)
# Timeout seconds Stops motion tracking when no activity
TRACK_TIMEOUT = MOTION_TRACK_TIMEOUT_SEC
# OpenCV Contour sq px area must be greater than this.
MIN_AREA = MOTION_TRACK_MIN_AREA
BLUR_SIZE = 10  # OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20  # OpenCV setting for difference image threshold

# Fix range Errors  Use zero to set default quality to 85
if IMAGE_JPG_QUAL < 1:
    IMAGE_JPG_QUAL = 85
elif IMAGE_JPG_QUAL > 100:
    IMAGE_JPG_QUAL = 100

#------------------------------------------------------------------------------
class PiVideoStream:
    '''
    Create a picamera in memory video stream and
    return a frame when update called
    '''
    def __init__(self, resolution=(stream_width, stream_height),
                 framerate=stream_framerate,
                 rotation=0,
                 hflip=False, vflip=False):
        # initialize the camera and stream
        try:
            self.camera = PiCamera()
        except:
            logging.error("PiCamera Already in Use by Another Process")
            logging.error("Exiting %s Due to Error", PROG_NAME)
            exit(1)
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.camera.rotation = rotation
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr",
                                                     use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.thread = None   # Initialize thread
        self.frame = None
        self.stopped = False

    def start(self):
        ''' start the thread to read frames from the video stream'''
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        ''' keep looping infinitely until the thread is stopped'''
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and release camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        ''' return the frame most recently read '''
        return self.frame

    def stop(self):
        ''' indicate that the thread should be stopped '''
        self.stopped = True
        if self.thread is not None:
            self.thread.join()

#------------------------------------------------------------------------------
def shut2sec(shutspeed):
    ''' Convert camera shutter speed setting to string '''
    shutspeedSec = shutspeed/float(SECONDS2MICRO)
    shutstring = str("%.4f") % (shutspeedSec)
    return shutstring

#------------------------------------------------------------------------------
def show_time():
    ''' Show current date time in text format '''
    rightNow = datetime.datetime.now()
    currentTime = ("%04d-%02d-%02d %02d:%02d:%02d" % (rightNow.year,
                                                      rightNow.month,
                                                      rightNow.day,
                                                      rightNow.hour,
                                                      rightNow.minute,
                                                      rightNow.second))
    return currentTime

#------------------------------------------------------------------------------
def show_dots(dotcnt):
    '''
    If motionShowDots=True then display a progress
    dot for each cycle.  If MOTION_TRACK_ON then this would
    normally be too fast and should be turned off
    '''
    if MOTION_DOTS_ON:
        if MOTION_TRACK_ON and VERBOSE_ON:
            dotcnt += 1
            if dotcnt > MOTION_DOTS_MAX + 2:
                print("")
                dotcnt = 0
            elif dotcnt > MOTION_DOTS_MAX:
                print("")
                stime = show_time() + " ."
                sys.stdout.write(stime)
                sys.stdout.flush()
                dotcnt = 0
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
    return dotcnt

#------------------------------------------------------------------------------
def check_config():
    '''
    Check if both User disabled everything
    in config.py. At least one option needs to be enabled
    '''
    if not MOTION_TRACK_ON and not TIMELAPSE_ON and not PANO_ON and not VIDEO_REPEAT_ON:
        errorText = ("You need to have Motion, Timelapse, Pano or Video Repeat turned ON\n"
                     "MOTION_TRACK_ON=%s TIMELAPSE_ON=%s PANO_ON=%s VIDEO_REPEAT_ON=%s"
                     % (MOTION_TRACK_ON, TIMELAPSE_ON, PANO_ON, VIDEO_REPEAT_ON))
        if VERBOSE_ON:
            logging.error(errorText)
        else:
            sys.stdout.write(errorText)
        sys.exit(1)

#------------------------------------------------------------------------------
def display_info(motioncount, timelapsecount):
    ''' Display variable settings with plugin overlays if required '''
    if VERBOSE_ON:
        print("----------------------------------- Settings "
              "-----------------------------------")
        print("Config File .. CONFIG_FILENAME=%s  CONFIG_TITLE=%s"
              % (CONFIG_FILENAME, CONFIG_TITLE))
        if PLUGIN_ON:
            print("     Plugin .. PLUGIN_ON=%s  PLUGIN_NAME=%s"
                  " (Overlays %s Variable Settings)"
                  % (PLUGIN_ON, PLUGIN_NAME, CONFIG_FILENAME))
        else:
            print("     Plugin .. PLUGIN_ON=%s" % PLUGIN_ON)
        print("")
        print("Image Info ... Size=%ix%i  ext=%s  Prefix=%s"
              "  VFlip=%s  HFlip=%s  Rotation=%i"
              % (image_width, image_height, IMAGE_FORMAT, IMAGE_NAME_PREFIX,
                 IMAGE_VFLIP, IMAGE_HFLIP, IMAGE_ROTATION))
        print("               IMAGE_GRAYSCALE=%s   Preview=%s"
              % (IMAGE_GRAYSCALE, IMAGE_PREVIEW))
        if IMAGE_FORMAT == '.jpg' or IMAGE_FORMAT == '.jpeg':
            print("               JpegQuality=%i where 1=Low 100=High"
                  % (IMAGE_JPG_QUAL))
        print("   Low Light.. NIGHT_TWILIGHT_MODE_ON=%s  NIGHT_TWILIGHT_THRESHOLD=%i"
              "  NIGHT_DARK_THRESHOLD=%i  NIGHT_BLACK_THRESHOLD=%i"
              % (NIGHT_TWILIGHT_MODE_ON, NIGHT_TWILIGHT_THRESHOLD, NIGHT_DARK_THRESHOLD, NIGHT_BLACK_THRESHOLD))
        print("               NIGHT_MAX_SHUT_SEC=%.2f  NIGHT_MAX_ISO=%i"
              "  NIGHT_DARK_ADJUST=%.2f  NIGHT_SLEEP_SEC=%i"
              % (NIGHT_MAX_SHUT_SEC, NIGHT_MAX_ISO, NIGHT_DARK_ADJUST, NIGHT_SLEEP_SEC))
        print("   No Shots .. IMAGE_NO_NIGHT_SHOTS=%s   IMAGE_NO_DAY_SHOTS=%s"
              % (IMAGE_NO_NIGHT_SHOTS, IMAGE_NO_DAY_SHOTS))

        if SHOW_DATE_ON_IMAGE:
            print("   Img Text .. On=%s  Bottom=%s (False=Top)  WhiteText=%s (False=Black)"
                  % (SHOW_DATE_ON_IMAGE, SHOW_TEXT_BOTTOM, SHOW_TEXT_WHITE))
            print("               SHOW_TEXT_WHITE_NIGHT=%s  SHOW_TEXT_FONT_SIZE=%i px height"
                  % (SHOW_TEXT_WHITE_NIGHT, SHOW_TEXT_FONT_SIZE))
        else:
            print("    No Text .. SHOW_DATE_ON_IMAGE=%s  Text on Image is Disabled"
                  % (SHOW_DATE_ON_IMAGE))
        print("")
        if MOTION_TRACK_ON:
            print("Motion Track.. On=%s  Prefix=%s  MinArea=%i sqpx"
                  "  TrigLen=%i-%i px  TimeOut=%i sec"
                  % (MOTION_TRACK_ON, MOTION_PREFIX, MOTION_TRACK_MIN_AREA,
                     MOTION_TRACK_TRIG_LEN, TRACK_TRIG_LEN_MAX, MOTION_TRACK_TIMEOUT_SEC))
            print("               MOTION_TRACK_INFO_ON=%s   MOTION_DOTS_ON=%s  IMAGE_SHOW_STREAM=%s"
                  % (MOTION_TRACK_INFO_ON, MOTION_DOTS_ON, IMAGE_SHOW_STREAM))
            print("   Stream .... size=%ix%i  framerate=%i fps"
                  "  STREAM_STOP_SEC=%.2f  QuickPic=%s"
                  % (stream_width, stream_height, STREAM_FPS,
                     STREAM_STOP_SEC, MOTION_TRACK_QUICK_PIC_ON))
            print("   Img Path .. MOTION_PATH=%s  MOTION_CAM_SLEEP=%.2f sec"
                  % (MOTION_PATH, MOTION_CAM_SLEEP))
            print("   Sched ..... MOTION_START_AT %s blank=Off or"
                  " Set Valid Date and/or Time to Start Sequence"
                  % MOTION_START_AT)
            print("   Force ..... MOTION_FORCE_SEC=%i min (If No Motion)"
                  % (MOTION_FORCE_SEC/60))
            print("   Lockfile .. On=%s  Path=%s  NOTE: For Motion Images Only."
                  % (CREATE_LOCKFILE, LOCK_FILEPATH))

            if MOTION_NUM_ON:
                print("   Num Seq ... MOTION_NUM_ON=%s  numRecycle=%s"
                      "  numStart=%i   numMax=%i  current=%s"
                      % (MOTION_NUM_ON, MOTION_NUM_RECYCLE_ON, MOTION_NUM_START,
                         MOTION_NUM_MAX, motioncount))
                print("   Num Path .. NUM_PATH_MOTION=%s " % (NUM_PATH_MOTION))
            else:
                print("   Date-Time.. MOTION_NUM_ON=%s  Image Numbering is Disabled"
                      % (MOTION_NUM_ON))

            if MOTION_TRACK_MINI_TL_ON:
                print("   Quick TL .. MOTION_TRACK_MINI_TL_ON=%s   MOTION_TRACK_MINI_TL_SEQ_SEC=%i"
                      " sec  MOTION_TRACK_MINI_TL_TIMER_SEC=%i sec (0=fastest)"
                      % (MOTION_TRACK_MINI_TL_ON, MOTION_TRACK_MINI_TL_SEQ_SEC,
                         MOTION_TRACK_MINI_TL_TIMER_SEC))
            else:
                print("   Quick TL .. MOTION_TRACK_MINI_TL_ON=%s  Quick Time Lapse Disabled"
                      % MOTION_TRACK_MINI_TL_ON)

            if MOTION_VIDEO_ON:
                print("   Video ..... MOTION_VIDEO_ON=%s   MOTION_VIDEO_TIMER_SEC=%i"
                      " sec  MOTION_VIDEO_FPS=%i (superseded by QuickTL)"
                      % (MOTION_VIDEO_ON, MOTION_VIDEO_TIMER_SEC, MOTION_VIDEO_FPS))
            else:
                print("   Video ..... MOTION_VIDEO_ON=%s  Motion Video is Disabled"
                      % MOTION_VIDEO_ON)
            print("   Sub-Dir ... MOTION_SUBDIR_MAX_HOURS=%i (0-off)"
                  "  MOTION_SUBDIR_MAX_FILES=%i (0=off)"
                  % (MOTION_SUBDIR_MAX_HOURS, MOTION_SUBDIR_MAX_FILES))
            print("   Recent .... MOTION_RECENT_MAX=%i (0=off)  MOTION_RECENT_DIR=%s"
                  % (MOTION_RECENT_MAX, MOTION_RECENT_DIR))
        else:
            print("Motion ....... MOTION_TRACK_ON=%s  Motion Tracking is Disabled)"
                  % MOTION_TRACK_ON)
        print("")
        if TIMELAPSE_ON:
            print("Time Lapse ... On=%s  Prefix=%s   Timer=%i sec"
                  "   TIMELAPSE_EXIT_SEC=%i (0=Continuous)"
                  % (TIMELAPSE_ON, TIMELAPSE_PREFIX,
                     TIMELAPSE_TIMER_SEC, TIMELAPSE_EXIT_SEC))
            print("               TIMELAPSE_MAX_FILES=%i" % (TIMELAPSE_MAX_FILES))
            print("   Img Path .. TIMELAPSE_PATH=%s  TIMELAPSE_CAM_SLEEP_SEC=%.2f sec"
                  % (TIMELAPSE_PATH, TIMELAPSE_CAM_SLEEP_SEC))
            print("   Sched ..... TIMELAPSE_START_AT %s blank=Off or"
                  " Set Valid Date and/or Time to Start Sequence"
                  % TIMELAPSE_START_AT)
            if TIMELAPSE_NUM_ON:
                print("   Num Seq ... On=%s  numRecycle=%s  numStart=%i   numMax=%i  current=%s"
                      % (TIMELAPSE_NUM_ON, TIMELAPSE_NUM_RECYCLE_ON, TIMELAPSE_NUM_START,
                         TIMELAPSE_NUM_MAX, timelapsecount))
                print("   Num Path .. numPath=%s" % (NUM_PATH_TIMELAPSE))
            else:
                print("   Date-Time.. MOTION_NUM_ON=%s  Numbering Disabled"
                      % TIMELAPSE_NUM_ON)
            print("   Sub-Dir ... TIMELAPSE_SUBDIR_MAX_HOURS=%i (0=off)"
                  "  TIMELAPSE_SUBDIR_MAX_FILES=%i (0=off)"
                  % (TIMELAPSE_SUBDIR_MAX_HOURS, TIMELAPSE_SUBDIR_MAX_FILES))
            print("   Recent .... TIMELAPSE_RECENT_MAX=%i (0=off)  TIMELAPSE_RECENT_DIR=%s"
                  % (TIMELAPSE_RECENT_MAX, TIMELAPSE_RECENT_DIR))
        else:
            print("Time Lapse ... TIMELAPSE_ON=%s  Timelapse is Disabled"
                  % TIMELAPSE_ON)
        print("")
        if SPACE_TIMER_HOURS > 0:   # Check if disk mgmnt is enabled
            print("Disk Space  .. Enabled - Manage Target Free Disk Space."
                  " Delete Oldest %s Files if Required"
                  % (SPACE_TARGET_EXT))
            print("               Check Every SPACE_TIMER_HOURS=%i (0=off)"
                  "  Target SPACE_TARGET_MB=%i (min=100 MB)  SPACE_TARGET_EXT=%s"
                  % (SPACE_TIMER_HOURS, SPACE_TARGET_MB, SPACE_TARGET_EXT))
            print("               Delete Oldest SPACE_TARGET_EXT=%s  SPACE_MEDIA_DIR=%s"
                  % (SPACE_TARGET_EXT, SPACE_MEDIA_DIR))
        else:
            print("Disk Space  .. SPACE_TIMER_HOURS=%i "
                  "(Disabled) - Manage Target Free Disk Space. Delete Oldest %s Files"
                  % (SPACE_TIMER_HOURS, SPACE_TARGET_EXT))
            print("            .. Check Every SPACE_TIMER_HOURS=%i (0=Off)"
                  "  Target SPACE_TARGET_MB=%i (min=100 MB)"
                  % (SPACE_TIMER_HOURS, SPACE_TARGET_MB))
        print("")
        print("Logging ...... VERBOSE_ON=%s (True=Enabled False=Disabled)"
              % VERBOSE_ON)
        print("   Log Path .. LOG_TO_FILE_ON=%s  LOG_FILE_PATH=%s"
              % (LOG_TO_FILE_ON, LOG_FILE_PATH))
        print("--------------------------------- Log Activity "
              "---------------------------------")
    check_config()

#------------------------------------------------------------------------------
def get_last_subdir(directory):
    ''' Scan for directories and return most recent '''
    dirList = ([name for name in
                os.listdir(directory) if
                os.path.isdir(os.path.join(directory, name))])
    if len(dirList) > 0:
        lastSubDir = sorted(dirList)[-1]
        lastSubDir = os.path.join(directory, lastSubDir)
    else:
        lastSubDir = directory
    return lastSubDir

#------------------------------------------------------------------------------
def create_subdir(directory, prefix):
    '''
    Create a subdirectory in directory with
    unique name based on prefix and date time
    '''
    now = datetime.datetime.now()
    # Specify folder naming
    subDirName = ('%s%d-%02d%02d-%02d%02d' % (prefix,
                                              now.year, now.month, now.day,
                                              now.hour, now.minute))
    subDirPath = os.path.join(directory, subDirName)
    if not os.path.isdir(subDirPath):
        try:
            os.makedirs(subDirPath)
        except OSError as err:
            logging.error('Cannot Create Directory %s - %s, using default location.',
                          subDirPath, err)
            subDirPath = directory
        else:
            logging.info('Created %s', subDirPath)
    else:
        subDirPath = directory
    return subDirPath

#------------------------------------------------------------------------------
def subDirCheckMaxFiles(directory, filesMax):
    ''' Count number of files in a folder path '''
    fileList = glob.glob(directory + '/*jpg')
    count = len(fileList)
    if count > filesMax:
        makeNewDir = True
        logging.info('Total Files in %s Exceeds %i', directory, filesMax)
    else:
        makeNewDir = False
    return makeNewDir

#------------------------------------------------------------------------------
def subDirCheckMaxHrs(directory, hrsMax, prefix):
    '''
    Note to self need to add error checking
    extract the date-time from the directory name
    '''
    dirName = os.path.split(directory)[1] # split dir path and keep dirName
    # remove prefix from dirName so just date-time left
    dirStr = dirName.replace(prefix, '')
    # convert string to datetime
    dirDate = datetime.datetime.strptime(dirStr, "%Y-%m%d-%H%M")
    rightNow = datetime.datetime.now()   # get datetime now
    diff = rightNow - dirDate  # get time difference between dates
    days, seconds = diff.days, diff.seconds
    dirAgeHours = float(days * 24 + (seconds / 3600.0))  # convert to hours
    if dirAgeHours > hrsMax:   # See if hours are exceeded
        makeNewDir = True
        logging.info('MaxHrs %i Exceeds %i for %s',
                     dirAgeHours, hrsMax, directory)
    else:
        makeNewDir = False
    return makeNewDir

#------------------------------------------------------------------------------
def subDirChecks(maxHours, maxFiles, directory, prefix):
    ''' Check if motion SubDir needs to be created '''
    if maxHours < 1 and maxFiles < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', directory)
        subDirPath = directory
    else:
        subDirPath = get_last_subdir(directory)
        if subDirPath == directory:   # No subDir Found
            logging.info('No sub folders Found in %s', directory)
            subDirPath = create_subdir(directory, prefix)
        # Check MaxHours Folder Age Only
        elif (maxHours > 0 and maxFiles < 1):
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                subDirPath = create_subdir(directory, prefix)
        elif (maxHours < 1 and maxFiles > 0):   # Check Max Files Only
            if subDirCheckMaxFiles(subDirPath, maxFiles):
                subDirPath = create_subdir(directory, prefix)
        elif maxHours > 0 and maxFiles > 0:   # Check both Max Files and Age
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                if subDirCheckMaxFiles(subDirPath, maxFiles):
                    subDirPath = create_subdir(directory, prefix)
                else:
                    logging.info('MaxFiles Not Exceeded in %s', subDirPath)
    os.path.abspath(subDirPath)
    return subDirPath

def make_media_dir(dir_path):
    '''Create a folder sequence'''
    make_dir = False
    if not os.path.isdir(dir_path):
        make_dir = True
        logging.info("Create Folder %s", dir_path)
        try:
            os.makedirs(dir_path)
        except OSError as err:
            logging.error("Could Not Create %s - %s", dir_path, err)
            sys.exit(1)
    return make_dir

#------------------------------------------------------------------------------
def check_media_paths():
    '''
    Checks for image folders and
    create them if they do not already exist.
    '''
    make_media_dir(DATA_DIR)

    if MOTION_TRACK_ON:
        if make_media_dir(MOTION_PATH):
            if os.path.isfile(NUM_PATH_MOTION):
                logging.info("Delete Motion dat File %s", NUM_PATH_MOTION)
                os.remove(NUM_PATH_MOTION)

    if TIMELAPSE_ON:
        if make_media_dir(TIMELAPSE_PATH):
            if os.path.isfile(NUM_PATH_TIMELAPSE):
                logging.info("Delete TimeLapse dat file %s", NUM_PATH_TIMELAPSE)
                os.remove(NUM_PATH_TIMELAPSE)

    # Check for Recent Image Folders and create if they do not already exist.
    if MOTION_RECENT_MAX > 0:
        make_media_dir(MOTION_RECENT_DIR)

    if TIMELAPSE_RECENT_MAX > 0:
        make_media_dir(TIMELAPSE_RECENT_DIR)

    if PANO_ON:
        make_media_dir(PANO_DIR)
        make_media_dir(PANO_IMAGES_DIR)

#------------------------------------------------------------------------------
def deleteOldFiles(maxFiles, dirPath, prefix):
    '''
    Delete Oldest files gt or eq to maxfiles that match filename prefix
    '''
    try:
        fileList = sorted(glob.glob(os.path.join(dirPath, prefix + '*')), key=os.path.getmtime)
    except OSError as err:
        logging.error('Problem Reading Directory %s - %s', dirPath, err)
    else:
        while len(fileList) >= maxFiles:
            oldest = fileList[0]
            oldestFile = oldest
            try:   # Remove oldest file in recent folder
                fileList.remove(oldest)
                logging.info('%s', oldestFile)
                os.remove(oldestFile)
            except OSError as err:
                logging.error('Failed %s  err: %s', oldestFile, err)

#------------------------------------------------------------------------------
def saveRecent(recentMax, recentDir, filename, prefix):
    '''
    Create a symlink file in recent folder (timelapse or motion subfolder)
    Delete Oldest symlink file if recentMax exceeded.
    '''
    src = os.path.abspath(filename)  # original file path
    dest = os.path.abspath(os.path.join(recentDir,
                                        os.path.basename(filename)))
    deleteOldFiles(recentMax, os.path.abspath(recentDir), prefix)
    try:    # Create symlink in recent folder
        logging.info('symlink %s', dest)
        os.symlink(src, dest)  # Create a symlink to actual file
    except OSError as err:
        logging.error('symlink %s to %s  err: %s', dest, src, err)

#------------------------------------------------------------------------------
def filesToDelete(mediaDirPath, extension=IMAGE_FORMAT):
    '''
    Deletes files of specified format extension
    by walking folder structure from specified mediaDirPath
    '''
    return sorted(
        (os.path.join(dirname, filename)
         for dirname, dirnames, filenames in os.walk(mediaDirPath)
         for filename in filenames
         if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime, reverse=True)

#------------------------------------------------------------------------------
def freeSpaceUpTo(freeMB, mediaDir, extension=IMAGE_FORMAT):
    '''
    Walks mediaDir and deletes oldest files until SPACE_TARGET_MB is achieved.
    You should Use with Caution this feature.
    '''
    mediaDirPath = os.path.abspath(mediaDir)
    if os.path.isdir(mediaDirPath):
        MB2Bytes = 1048576  # Conversion from MB to Bytes
        targetFreeBytes = freeMB * MB2Bytes
        fileList = filesToDelete(mediaDir, extension)
        totFiles = len(fileList)
        delcnt = 0
        logging.info('Session Started')
        while fileList:
            statv = os.statvfs(mediaDirPath)
            availFreeBytes = statv.f_bfree*statv.f_bsize
            if availFreeBytes >= targetFreeBytes:
                break
            filePath = fileList.pop()
            try:
                os.remove(filePath)
            except OSError as err:
                logging.error('Del Failed %s', filePath)
                logging.error('Error is %s', err)
            else:
                delcnt += 1
                logging.info('Del %s', filePath)
                logging.info('Target=%i MB  Avail=%i MB  Deleted %i of %i Files ',
                             targetFreeBytes / MB2Bytes, availFreeBytes / MB2Bytes,
                             delcnt, totFiles)
                # Avoid deleting more than 1/4 of files at one time
                if delcnt > totFiles / 4:
                    logging.warning('Max Deletions Reached %i of %i',
                                    delcnt, totFiles)
                    logging.warning('Deletions Restricted to 1/4 of '
                                    'total files per session.')
                    break
        logging.info('Session Ended')
    else:
        logging.error('Directory Not Found - %s', mediaDirPath)

#------------------------------------------------------------------------------
def freeDiskSpaceCheck(lastSpaceCheck):
    '''
    Perform Disk space checking and Clean up
    if enabled and return datetime done
    to reset ready for next sched date/time
    '''
    if SPACE_TIMER_HOURS > 0:   # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if (datetime.datetime.now() - lastSpaceCheck).total_seconds() > SPACE_TIMER_HOURS * 3600:
            lastSpaceCheck = datetime.datetime.now()
            if SPACE_TARGET_MB < 100:   # set freeSpaceMB to reasonable value if too low
                diskFreeMB = 100
            else:
                diskFreeMB = SPACE_TARGET_MB
            logging.info('SPACE_TIMER_HOURS=%i  diskFreeMB=%i  SPACE_MEDIA_DIR=%s SPACE_TARGET_EXT=%s',
                         SPACE_TIMER_HOURS, diskFreeMB, SPACE_MEDIA_DIR, SPACE_TARGET_EXT)
            freeSpaceUpTo(diskFreeMB, SPACE_MEDIA_DIR, SPACE_TARGET_EXT)
    return lastSpaceCheck

#------------------------------------------------------------------------------
def get_current_count(numberpath, numberstart):
    '''
    Create a .dat file to store currentCount
    or read file if it already Exists
    '''
    if not os.path.isfile(numberpath):
        # Create numberPath file if it does not exist
        logging.info("Creating New File %s numberstart= %s",
                     numberpath, numberstart)
        open(numberpath, 'w').close()
        f = open(numberpath, 'w+')
        f.write(str(numberstart))
        f.close()
    # Read the numberPath file to get the last sequence number
    with open(numberpath, 'r') as f:
        writeCount = f.read()
        f.closed
        try:
            numbercounter = int(writeCount)
        # Found Corrupt dat file since cannot convert to integer
        except ValueError:
            # Try to determine if this is motion or timelapse
            if numberpath.find(MOTION_PREFIX) > 0:
                filePath = MOTION_PATH + "/*" + IMAGE_FORMAT
                fprefix = MOTION_PATH + MOTION_PREFIX + IMAGE_NAME_PREFIX
            else:
                filePath = TIMELAPSE_PATH + "/*" + IMAGE_FORMAT
                fprefix = TIMELAPSE_PATH + TIMELAPSE_PREFIX + IMAGE_NAME_PREFIX

            try:
               # Scan image folder for most recent file
               # and try to extract most recent number counter
                newest = max(glob.iglob(filePath), key=os.path.getctime)
                writeCount = newest[len(fprefix)+1:newest.find(IMAGE_FORMAT)]
            except:
                writeCount = numberstart

            try:
                numbercounter = int(writeCount)+1
            except ValueError:
                numbercounter = numberstart
            logging.warning("Found Invalid Data in %s Resetting Counter to %s",
                            numberpath, numbercounter)
        f = open(numberpath, 'w+')
        f.write(str(numbercounter))
        f.close()
        f = open(numberpath, 'r')
        writeCount = f.read()
        f.close()
        numbercounter = int(writeCount)
    return numbercounter

#------------------------------------------------------------------------------
def writeTextToImage(imagename, datetoprint, currentDayMode):
    '''
    Function to write date/time stamp
    directly on top or bottom of images.
    '''
    if SHOW_TEXT_WHITE:
        FOREGROUND = (255, 255, 255) # rgb settings for white text foreground
        textColour = "White"
    else:
        FOREGROUND = (0, 0, 0)  # rgb settings for black text foreground
        textColour = "Black"
        if SHOW_TEXT_WHITE_NIGHT and (not currentDayMode):
            # rgb settings for black text foreground
            FOREGROUND = (255, 255, 255)
            textColour = "White"
    img = cv2.imread(imagename)
    # This is grayscale image so channels is not avail or used
    height, width, channels = img.shape
    # centre text and compensate for graphics text being wider
    x = int((width/2) - (len(imagename)*2))
    if SHOW_TEXT_BOTTOM:
        y = (height - 50)  # show text at bottom of image
    else:
        y = 10  # show text at top of image
    TEXT = IMAGE_NAME_PREFIX + datetoprint
    font_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
    font = ImageFont.truetype(font_path, SHOW_TEXT_FONT_SIZE, encoding='unic')
    try:
        text = TEXT.decode('utf-8')   # required for python2
    except:
        text = TEXT   # Just set for python3
    img = Image.open(imagename)
    # For python3 install of pyexiv2 lib
    # See https://github.com/pageauc/pi-timolo/issues/79

    try:  # Read exif data since ImageDraw does not save this metadata
        metadata = pyexiv2.ImageMetadata(imagename)
        metadata.read()
    except:
        pass

    draw = ImageDraw.Draw(img)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text((x, y), text, FOREGROUND, font=font)
    if IMAGE_FORMAT.lower == '.jpg' or IMAGE_FORMAT.lower == '.jpeg':
        img.save(imagename, quality="keep")
    else:
        img.save(imagename)

    logging.info("Added %s Text [ %s ]", textColour, datetoprint)
    try:
        metadata.write() # Write previously saved exif data to image file
    except:
        logging.warning("Image EXIF Data Not Transferred.")
    logging.info("Saved %s", imagename)

#------------------------------------------------------------------------------
def writeCounter(counter, counter_path):
    '''
    Write next counter number
    to specified counter_path dat file
    to remember where counter is to start next in case
    app shuts down.
    '''
    str_count = str(counter)
    if not os.path.isfile(counter_path):
        logging.info("Create New Counter File Counter=%s %s",
                     str_count, counter_path)
        open(counter_path, 'w').close()
    f = open(counter_path, 'w+')
    f.write(str_count)
    f.close()
    logging.info("Next Counter=%s %s", str_count, counter_path)

#------------------------------------------------------------------------------
def postImageProcessing(numberon, counterstart, countermax, counter,
                        recycle, counterpath, filename, currentDaymode):
    '''
    If required process text to display directly on image
    '''
    rightNow = datetime.datetime.now()
    if SHOW_DATE_ON_IMAGE:
        dateTimeText = ("%04d%02d%02d_%02d:%02d:%02d"
                        % (rightNow.year, rightNow.month, rightNow.day,
                           rightNow.hour, rightNow.minute, rightNow.second))
        if numberon:
            if not recycle and countermax > 0:
                counterStr = "%i/%i " % (counter, counterstart + countermax)
                imageText = counterStr + dateTimeText
            else:
                counterStr = "%i  "  % (counter)
                imageText = counterStr + dateTimeText
        else:
            imageText = dateTimeText

        # Now put the imageText on the current image
        try:  # This will fail for a video file
            writeTextToImage(filename, imageText, currentDaymode)
        except:
            pass
    if CREATE_LOCKFILE and MOTION_TRACK_ON:
        create_sync_lockfile(filename)
    # Process currentCount for next image if number sequence is enabled
    if numberon:
        counter += 1
        if countermax > 0:
            if counter > counterstart + countermax:
                if recycle:
                    counter = counterstart
                else:
                    counter = counterstart + countermax + 1
                    logging.warning("Exceeded Image Count numberMax=%i for %s \n",
                                    countermax, filename)
        # write next image counter number to dat file
        writeCounter(counter, counterpath)
    return counter

#------------------------------------------------------------------------------
def getVideoName(path, prefix, numberon, counter):
    ''' build image file names by number sequence or date/time'''
    if numberon:
        if MOTION_VIDEO_ON or VIDEO_REPEAT_ON:
            filename = os.path.join(path, prefix + str(counter) + ".h264")
    else:
        if MOTION_VIDEO_ON or VIDEO_REPEAT_ON:
            rightNow = datetime.datetime.now()
            filename = ("%s/%s%04d%02d%02d-%02d%02d%02d.h264"
                        % (path, prefix,
                           rightNow.year, rightNow.month, rightNow.day,
                           rightNow.hour, rightNow.minute, rightNow.second))
    return filename

#------------------------------------------------------------------------------
def get_image_filename(path, prefix, numberon, counter):
    ''' build image file names by number sequence or date/time '''
    if numberon:
        filename = os.path.join(path, prefix + str(counter) + IMAGE_FORMAT)
    else:
        rightNow = datetime.datetime.now()
        filename = ("%s/%s%04d%02d%02d-%02d%02d%02d%s"
                    % (path, prefix,
                       rightNow.year, rightNow.month, rightNow.day,
                       rightNow.hour, rightNow.minute, rightNow.second,
                       IMAGE_FORMAT))
    return filename

#------------------------------------------------------------------------------
def take_mo_quick_pic(image, filename):
    ''' Enlarge and Save stream image if MOTION_TRACK_QUICK_PIC_ON=True'''
    big_image = cv2.resize(image, (bigImageWidth, bigImageHeight)) if bigImage != 1 else image
    cv2.imwrite(filename, big_image)
    logging.info("Saved %ix%i Image to %s",
                 bigImageWidth, bigImageHeight, filename)

#------------------------------------------------------------------------------
def showBox(filename):
    '''
    Show stream image detection area on image to align camera
    This is a quick fix for restricting motion detection
    to a portion of the final image. Change the stream image size
    on line 206 and 207 above
    Adjust track config.py file MOTION_TRACK_TRIG_LEN as required.
    '''
    working_image = cv2.imread(filename)
    x1y1 = (int((IMAGE_WIDTH - stream_width)/2),
            int((image_height - stream_height)/2))
    x2y2 = (x1y1[0] + stream_width,
            x1y1[1] + stream_height)
    cv2.rectangle(working_image, x1y1, x2y2, LINE_COLOR, LINE_THICKNESS)
    cv2.imwrite(filename, working_image)

#------------------------------------------------------------------------------
def take_day_image(filename, cam_sleep_time):
    ''' Take a Day image using exp=auto and awb=auto '''
    with picamera.PiCamera() as camera:
        camera.resolution = (image_width, image_height)
        camera.vflip = IMAGE_VFLIP
        camera.hflip = IMAGE_HFLIP
        camera.rotation = IMAGE_ROTATION # Valid values are 0, 90, 180, 270
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        if IMAGE_GRAYSCALE:
            camera.color_effects = (128, 128)
        time.sleep(cam_sleep_time) # use motion or TL camera sleep to get AWB
        if IMAGE_PREVIEW:
            camera.start_preview()
        if IMAGE_FORMAT == ".jpg":   # Set quality if image is jpg
            camera.capture(filename, quality=IMAGE_JPG_QUAL)
        else:
            camera.capture(filename)
        camera.close()

    if IMAGE_SHOW_STREAM:    # Show motion area on full image to align camera
        showBox(filename)

    logging.info("camSleepSec=%.2f exp=auto awb=auto Size=%ix%i ",
                 cam_sleep_time, image_width, image_height)
    # SHOW_DATE_ON_IMAGE displays FilePath so avoid showing twice
    if not SHOW_DATE_ON_IMAGE:
        logging.info("FilePath  %s", filename)

#------------------------------------------------------------------------------
def take_pano(pano_seq_num):
    '''
    Take a series of overlapping images using pantilt at specified PANO_CAM_STOPS
    then attempt to stitch the images into one panoramic image. Note this
    will take time so depending on number of cpu cores and speed. The PANO_TIMER
    should be set to avoid multiple stitching operations at once.
    use htop or top to check stitching PID activity.

    Successfuly Stitching needs good lighting so it should be restricted to
    day light hours or sufficient indoor lighting.
    Review pano source image overlap using webserver. Adjust pano stops accordingly.
    '''

    logging.info('Sched Pano  timer=%i sec  pano_seq_num=%s',
                 PANO_TIMER_SEC, pano_seq_num)
    with picamera.PiCamera() as camera:
        camera.resolution = (image_width, image_height)
        camera.vflip = IMAGE_VFLIP
        camera.hflip = IMAGE_HFLIP
        camera.rotation = IMAGE_ROTATION # Valid values are 0, 90, 180, 270
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        if IMAGE_GRAYSCALE:
            camera.color_effects = (128, 128)
        time.sleep(MOTION_CAM_SLEEP) # use motion or TL camera sleep to get AWB
        if IMAGE_PREVIEW:
            camera.start_preview()

        pano_image_num = 0   # initialize counter to ensure each image filename is unique
        pano_image_files = ''  # string of contatenated image input pano filenames for stitch command line
        pano_file_path = os.path.join(PANO_DIR,
                                      PANO_IMAGE_PREFIX +
                                      IMAGE_NAME_PREFIX +
                                      str(pano_seq_num) +
                                      IMAGE_FORMAT)

        for cam_pos in PANO_CAM_STOPS:   # take images at each specified stop
            pano_image_num += 1 # Set image numbering for this image
            pan, tilt = cam_pos # set pan tilt values for this image
            pano_filename = os.path.join(PANO_IMAGES_DIR,
                                         PANO_IMAGE_PREFIX +
                                         IMAGE_NAME_PREFIX +
                                         str(pano_seq_num) +
                                         '-' + str(pano_image_num) +
                                         IMAGE_FORMAT)
            pano_image_files += ' ' + pano_filename
            pantilthat.pan(pan)
            pantilthat.tilt(tilt)
            if pano_seq_num == 1:
                time.sleep(0.3)
            time.sleep(PANTILT_SLEEP_SEC)
            if IMAGE_FORMAT == ".jpg":   # Set quality if image is jpg
                camera.capture(pano_filename, quality=IMAGE_JPG_QUAL)
            else:
                camera.capture(pano_filename)
            logging.info('Size %ix%i Saved %s at cam_pos(%i, %i)',
                         image_width, image_height,
                         pano_filename,
                         pan, tilt)
        camera.close()
    # Center pantilt
    pantilt_go_home()

    if not os.path.isfile(PANO_PROG_PATH):
        logging.error('Cannot Find Pano Executable File at %s', PANO_PROG_PATH)
        logging.info('Please run menubox.sh UPGRADE to correct problem')
        logging.warning('Exiting - Cannot Run Image Stitching of Images.')
        return
    if not os.path.isfile('./config.cfg'):
        logging.error('Cannot Find ./config.cfg required for %s', PANO_PROG_PATH)
        logging.info('Please run menubox.sh UPGRADE to correct problem')
        logging.warning('Exiting - Cannot Run Image Stitching of Images.')
        return

    # Create the stitch command line string
    stitch_cmd = PANO_PROG_PATH + ' ' + pano_file_path + pano_image_files
    try:
        logging.info("Run Image Stitching Command per Below")
        print("%s" % stitch_cmd)
        # spawn stitch command with parameters as seperate task
        proc = subprocess.Popen(stitch_cmd, shell=True, stdin=None,
                                stdout=None, stderr=None, close_fds=True)
    except IOError:
        logging.error("Failed subprocess %s", stitch_cmd)
    pano_seq_num += 1
    if PANO_NUM_RECYCLE and PANO_NUM_MAX > 0:
        if pano_seq_num > PANO_NUM_START + PANO_NUM_MAX:
            logging.info('PANO_NUM_RECYCLE Activated. Reset pano_seq_num to %i',
                         PANO_NUM_START)
            pano_seq_num = PANO_NUM_START
    writeCounter(pano_seq_num, NUM_PATH_PANO)
    return pano_seq_num

#------------------------------------------------------------------------------
def get_shutter_setting(pxAve):
    '''
    Calculate a shutter speed based on image pixel average
    '''
    px = pxAve + 1  # avoid division by zero
    offset = NIGHT_MAX_SHUTTER - ((NIGHT_MAX_SHUTTER / float(NIGHT_DARK_THRESHOLD) * px))
    brightness = offset * (1/float(NIGHT_DARK_ADJUST))
    # hyperbolic curve + brightness adjust
    shut = (NIGHT_MAX_SHUTTER * (1 / float(px))) + brightness
    return int(shut)

#------------------------------------------------------------------------------
def take_night_image(filename, pixelAve):
    ''' Take low light Twilight or Night image '''
    with picamera.PiCamera() as camera:
        camera.resolution = (image_width, image_height)
        camera.vflip = IMAGE_VFLIP
        camera.hflip = IMAGE_HFLIP
        camera.rotation = IMAGE_ROTATION # valid values are 0, 90, 180, 270
        if IMAGE_GRAYSCALE:
            camera.color_effects = (128, 128)
        # Use Twilight Threshold variable framerate_range
        if pixelAve >= NIGHT_DARK_THRESHOLD:
            camera.framerate_range = (Fraction(1, 6), Fraction(30, 1))
            time.sleep(1)
            camera.iso = NIGHT_MAX_ISO
            logging.info("%ix%i  TwilightThresh=%i/%i  MaxISO=%i uses framerate_range",
                         image_width, image_height,
                         pixelAve, NIGHT_TWILIGHT_THRESHOLD,
                         NIGHT_MAX_ISO)
            time.sleep(4)
        else:
            # Set the framerate to a fixed value
            camera.framerate = Fraction(1, 6)
            time.sleep(1)
            camera.iso = NIGHT_MAX_ISO
            if pixelAve <= NIGHT_BLACK_THRESHOLD:  # Black Threshold (very dark)
                camera.shutter_speed = NIGHT_MAX_SHUTTER
                logging.info("%ix%i  BlackThresh=%i/%i shutSec=%s  MaxISO=%i  NIGHT_SLEEP_SEC=%i",
                             image_width, image_height,
                             pixelAve, NIGHT_BLACK_THRESHOLD,
                             shut2sec(NIGHT_MAX_SHUTTER), NIGHT_MAX_ISO, NIGHT_SLEEP_SEC)
            else: # Dark Threshold (Between Twilight and Black)
                camShut = get_shutter_setting(pixelAve)
                if camShut > NIGHT_MAX_SHUTTER:
                    camShut = NIGHT_MAX_SHUTTER
                # Set the shutter for long exposure
                camera.shutter_speed = camShut
                logging.info("%ix%i  DarkThresh=%i/%i  shutSec=%s  MaxISO=%i  NIGHT_SLEEP_SEC=%i",
                             image_width, image_height,
                             pixelAve, NIGHT_DARK_THRESHOLD,
                             shut2sec(camShut), NIGHT_MAX_ISO, NIGHT_SLEEP_SEC)
            time.sleep(NIGHT_SLEEP_SEC)
            camera.exposure_mode = 'off'
        if IMAGE_FORMAT == ".jpg":
            camera.capture(filename, format='jpeg', quality=IMAGE_JPG_QUAL)
        else:
            camera.capture(filename)
        camera.framerate = 10   # Adhoc Fix for Stretch camera freeze issue
                               # Perform sudo rpi-update
        camera.close()

    if IMAGE_SHOW_STREAM:    # Show motion area on full image to align camera
        showBox(filename)

    # SHOW_DATE_ON_IMAGE displays FilePath to avoid showing twice
    if not SHOW_DATE_ON_IMAGE:
        logging.info("FilePath %s", filename)

#------------------------------------------------------------------------------
def take_mo_mini_timelapse(moPath, prefix, NumOn, motionNumCount,
                           currentDayMode, NumPath):
    '''
    Take a motion tracking activated mini timelapse sequence
    using yield if motion triggered
    '''
    logging.info("START - Run for %i secs with image every %i secs",
                 MOTION_TRACK_MINI_TL_SEQ_SEC, MOTION_TRACK_MINI_TL_TIMER_SEC)
    checkTimeLapseTimer = datetime.datetime.now()
    keepTakingImages = True
    imgCnt = 0
    filename = get_image_filename(moPath, prefix, NumOn, motionNumCount)
    while keepTakingImages:
        yield filename
        rightNow = datetime.datetime.now()
        timelapseDiff = (rightNow - checkTimeLapseTimer).total_seconds()
        motionNumCount = postImageProcessing(NumOn,
                                             MOTION_NUM_START,
                                             MOTION_NUM_MAX,
                                             motionNumCount,
                                             MOTION_NUM_RECYCLE_ON,
                                             NumPath, filename,
                                             currentDayMode)
        filename = get_image_filename(moPath, prefix, NumOn, motionNumCount)
        if timelapseDiff > MOTION_TRACK_MINI_TL_SEQ_SEC:
            keepTakingImages = False
        else:
            imgCnt += 1
            if MOTION_RECENT_MAX > 0:
                saveRecent(MOTION_RECENT_MAX,
                           MOTION_RECENT_DIR,
                           filename,
                           prefix)
            time.sleep(MOTION_TRACK_MINI_TL_TIMER_SEC)

    logging.info('END - Total %i Images in %i sec every %i sec',
                 imgCnt, timelapseDiff, MOTION_TRACK_MINI_TL_TIMER_SEC)

def pantilt_go_home():
    '''
    Move pantilt to home position. If pantilt installed then this
    can position pantilt to a home position for consistent
    motion tracking and timelapse camera pointing.
    '''
    if PANTILT_ON:
        pantilthat.pan(PANTILT_HOME[0])
        time.sleep(PANTILT_SLEEP_SEC)
        pantilthat.tilt(PANTILT_HOME[1])
        time.sleep(PANTILT_SLEEP_SEC)

#------------------------------------------------------------------------------
def create_sync_lockfile(imagefilename):
    '''
    If required create a lock file to indicate file(s) to process
    '''
    if CREATE_LOCKFILE:
        if not os.path.isfile(LOCK_FILEPATH):
            open(LOCK_FILEPATH, 'w').close()
            logging.info("Create Lock File %s", LOCK_FILEPATH)
        rightNow = datetime.datetime.now()
        now = ("%04d%02d%02d-%02d%02d%02d"
               % (rightNow.year, rightNow.month, rightNow.day,
                  rightNow.hour, rightNow.minute, rightNow.second))
        filecontents = (now + " create_sync_lockfile - " + imagefilename +
                        " Ready to sync using sudo ./sync.sh command.")
        f = open(LOCK_FILEPATH, 'w+')
        f.write(filecontents)
        f.close()

#------------------------------------------------------------------------------
def take_mo_video(filename, duration, fps=25):
    ''' Take a short motion video if required '''
    # Working folder for h264 videos
    h264_work = os.path.join(BASE_DIR, "h264_work")
    if not os.path.isdir(h264_work):
        try:
            os.makedirs(h264_work)
        except OSError as err:
            logging.error('%s  err: %s', h264_work, err)
        else:
            logging.info('Created Dir %s', h264_work)
    filePath264 = os.path.join(h264_work, os.path.basename(filename))
    # Final destination for mp4 videos
    filePathMP4 = os.path.join(os.path.dirname(filename),
                               os.path.splitext(os.path.basename(filename))[0] + ".mp4")
    # command to convert h264 video to mp4
    h264_mp4_cmd = ("/usr/bin/MP4Box -add %s:fps=%i -new %s" %
                    (filePath264, fps, filePathMP4))
    logging.info("File : %s", filePath264)
    logging.info("Start: Size %ix%i for %i sec at %i fps",
                 image_width, image_height, duration, fps)
    if MOTION_VIDEO_ON or VIDEO_REPEAT_ON:
        with picamera.PiCamera() as camera:
            camera.resolution = (image_width, image_height)
            camera.vflip = IMAGE_VFLIP
            camera.hflip = IMAGE_HFLIP
            # rotation can be used if camera is on side
            camera.rotation = IMAGE_ROTATION
            camera.framerate = fps
            if SHOW_DATE_ON_IMAGE:
                rightNow = datetime.datetime.now()
                dateTimeText = (" Started at %04d-%02d-%02d %02d:%02d:%02d "
                                % (rightNow.year,
                                   rightNow.month,
                                   rightNow.day,
                                   rightNow.hour,
                                   rightNow.minute,
                                   rightNow.second))
                camera.annotate_text_size = SHOW_TEXT_FONT_SIZE
                camera.annotate_foreground = picamera.Color('black')
                camera.annotate_background = picamera.Color('white')
                camera.annotate_text = dateTimeText
            camera.start_recording(filePath264)
            camera.wait_recording(duration)
            camera.stop_recording()
            camera.close()
        # This creates a subprocess that runs MP4Box to convert h264 file
        # to MP4 with the filename as a parameter.  Note this will take
        # some time so MP4Box logging info will be delayed.
        try:
            logging.info("MP4Box %s", filePathMP4)
            proc = subprocess.Popen(h264_mp4_cmd, shell=True, stdin=None,
                                    stdout=None, stderr=None, close_fds=True)
        except IOError:
            logging.error("subprocess %s", h264_mp4_cmd)
        if MOTION_RECENT_MAX > 0:
            saveRecent(MOTION_RECENT_MAX,
                       MOTION_RECENT_DIR,
                       filePathMP4,
                       MOTION_PREFIX)
        create_sync_lockfile(filename)

#------------------------------------------------------------------------------
def get_track_point(grayimage1, grayimage2):
    '''
    Process two cropped grayscale images.
    check for motion and return center point
    of motion for largest contour.
    '''
    movementCenterPoint = []  # initialize list of movementCenterPoints
    biggestArea = MIN_AREA
    # Get differences between the two greyed images
    differenceimage = cv2.absdiff(grayimage1, grayimage2)
    # Blur difference image to enhance motion vectors
    differenceimage = cv2.blur(differenceimage, (BLUR_SIZE, BLUR_SIZE))
    # Get threshold of blurred difference image
    # based on THRESHOLD_SENSITIVITY variable
    retval, thresholdimage = cv2.threshold(differenceimage,
                                           THRESHOLD_SENSITIVITY,
                                           255, cv2.THRESH_BINARY)
    try:
        # opencv2 syntax default
        contours, hierarchy = cv2.findContours(thresholdimage,
                                               cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        # opencv 3 syntax
        thresholdimage, contours, hierarchy = cv2.findContours(thresholdimage,
                                                               cv2.RETR_EXTERNAL,
                                                               cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        for c in contours:
            cArea = cv2.contourArea(c)
            if cArea > biggestArea:
                biggestArea = cArea
                (x, y, w, h) = cv2.boundingRect(c)
                cx = int(x + w/2)   # x center point of contour
                cy = int(y + h/2)   # y center point of contour
                movementCenterPoint = [cx, cy]
    return movementCenterPoint

#------------------------------------------------------------------------------
def track_distance(mPoint1, mPoint2):
    '''
    Return the triangulated distance between two tracking locations
    '''
    x1, y1 = mPoint1
    x2, y2 = mPoint2
    trackLen = abs(math.hypot(x2 - x1, y2 - y1))
    return trackLen

#------------------------------------------------------------------------------
def get_stream_pix_ave(streamData):
    '''
    Calculate the average pixel values for the specified stream
    used for determining day/night or twilight conditions
    '''
    pixAverage = int(np.average(streamData[..., 1]))
    return pixAverage

#------------------------------------------------------------------------------
def check_if_day_stream(currentDayMode, image):
    ''' Try to determine if it is day, night or twilight.'''
    dayPixAverage = 0
    currentDayMode = False
    dayPixAverage = get_stream_pix_ave(image)
    if dayPixAverage > NIGHT_TWILIGHT_THRESHOLD:
        currentDayMode = True
    return currentDayMode

#------------------------------------------------------------------------------
def time_to_sleep(currentDayMode):
    '''
    Based on weather it is day or night (exclude twilight)
    return sleepMode boolean based on variable
    settings for IMAGE_NO_NIGHT_SHOTS or IMAGE_NO_DAY_SHOTS config.py variables
    Note if both are enabled then no shots will be taken.
    '''
    if IMAGE_NO_NIGHT_SHOTS:
        if currentDayMode:
            sleepMode = False
        else:
            sleepMode = True
    elif IMAGE_NO_DAY_SHOTS:
        sleepMode = False
        if currentDayMode:
            sleepMode = True
    else:
        sleepMode = False
    return sleepMode

#------------------------------------------------------------------------------
def getSchedStart(dateToCheck):
    '''
    This function will try to extract a valid date/time from a
    date time formatted string variable
    If date/time is past then try to extract time
    and schedule for current date at extracted time
    '''
    goodDateTime = datetime.datetime.now()
    if len(dateToCheck) > 1:   # Check if TIMELAPSE_START_AT is set
        try:
            # parse and convert string to date/time or return error
            goodDateTime = parse(dateToCheck)
        except:
            # Is there a colon indicating possible time format exists
            if ":" in dateToCheck:
                timeTry = dateToCheck[dateToCheck.find(":") -2:]
                        # Try to extract time only from string
                try:
                    # See if a valid time is found returns with current day
                    goodDateTime = parse(timeTry)
                except:
                    logging.error("Bad Date and/or Time Format %s",
                                  dateToCheck)
                    logging.error('Use a Valid Date and/or Time '
                                  'Format Eg "DD-MMM-YYYY HH:MM:SS"')
                    goodDateTime = datetime.datetime.now()
                    logging.warning("Resetting date/time to Now: %s",
                                    goodDateTime)
        # Check if date/time is past
        if goodDateTime < datetime.datetime.now():
            if ":" in dateToCheck:  # Check if there is a time component
                # Extract possible time component
                timeTry = dateToCheck[dateToCheck.find(":") -2:]
                try:
                    # parse for valid time
                    # returns current day with parsed time
                    goodDateTime = parse(timeTry)
                except:
                    pass   # Do Nothing
    return goodDateTime

#------------------------------------------------------------------------------
def checkSchedStart(schedDate):
    '''
    Based on schedule date setting see if current
    datetime is past and return boolean
    to indicate processing can start for
    timelapse or motiontracking
    '''
    startStatus = False
    if schedDate < datetime.datetime.now():
        startStatus = True  # sched date/time has passed so start sequence
    return startStatus

#------------------------------------------------------------------------------
def check_timer(timer_start, timer_sec):
    '''
    Check if timelapse timer has expired
    Return updated start time status of expired timer True or False
    '''
    timer_expired = False
    rightNow = datetime.datetime.now()
    timeDiff = (rightNow - timer_start).total_seconds()
    if timeDiff >= timer_sec:
        timer_expired = True
        timer_start = rightNow
    return timer_start, timer_expired

#------------------------------------------------------------------------------
def timolo():
    '''
    Main motion and or motion tracking
    initialization and logic loop
    '''
    # Counter for show_dots() display if not motion found
    # shows system is working

    cam_tl_pos = 0    # TIMELAPSE_PANTILT_STOPS List Start position of pantilt
    pan, tilt = TIMELAPSE_PANTILT_STOPS[cam_tl_pos]
    dotCount = 0
    check_media_paths()
    timelapseNumCount = 0
    motionNumCount = 0

    tlstr = ""  # Used to display if timelapse is selected
    mostr = ""  # Used to display if motion is selected
    moCnt = "non"
    tlCnt = "non"

    daymode = False # Keep track of night and day based on dayPixAve

    motionFound = False
    take_timelapse = True
    stop_timelapse = False
    takeMotion = True
    stopMotion = False

    # Initialize some Timers
    pix_ave_timer = datetime.datetime.now()
    motion_force_timer = datetime.datetime.now()
    timelapseExitStart = datetime.datetime.now()
    startTL = getSchedStart(TIMELAPSE_START_AT)
    startMO = getSchedStart(MOTION_START_AT)
    trackLen = 0.0
    if SPACE_TIMER_HOURS > 0:
        lastSpaceCheck = datetime.datetime.now()
    if TIMELAPSE_ON:
        tlstr = "TimeLapse"
        # Check if timelapse subDirs reqd and create one if non exists
        tlPath = subDirChecks(TIMELAPSE_SUBDIR_MAX_HOURS,
                              TIMELAPSE_SUBDIR_MAX_FILES,
                              TIMELAPSE_DIR, TIMELAPSE_PREFIX)
        if TIMELAPSE_NUM_ON:
            timelapseNumCount = get_current_count(NUM_PATH_TIMELAPSE,
                                                  TIMELAPSE_NUM_START)
            tlCnt = str(timelapseNumCount)
    else:
        logging.warning("Timelapse is Suppressed per TIMELAPSE_ON=%s",
                        TIMELAPSE_ON)
        stop_timelapse = True

    if MOTION_TRACK_ON:
        logging.info("Start PiVideoStream ....")
        vs = PiVideoStream().start()
        vs.camera.rotation = IMAGE_ROTATION
        vs.camera.hflip = IMAGE_HFLIP
        vs.camera.vflip = IMAGE_VFLIP
        time.sleep(2)
        mostr = "Motion Tracking"
        # Check if motion subDirs required and
        # create one if required and non exists
        moPath = subDirChecks(MOTION_SUBDIR_MAX_HOURS,
                              MOTION_SUBDIR_MAX_FILES,
                              MOTION_DIR,
                              MOTION_PREFIX)
        if MOTION_NUM_ON:
            motionNumCount = get_current_count(NUM_PATH_MOTION,
                                               MOTION_NUM_START)
            moCnt = str(motionNumCount)
        trackTimeout = time.time()
        trackTimer = TRACK_TIMEOUT
        startPos = []
        startTrack = False
        image1 = vs.read()
        image2 = vs.read()
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        daymode = check_if_day_stream(daymode, image2)
        pixAve = get_stream_pix_ave(image2)
    else:
        vs = PiVideoStream().start()
        time.sleep(0.5)
        image2 = vs.read()  # use video stream to check for pixAve & daymode
        pixAve = get_stream_pix_ave(image2)
        daymode = check_if_day_stream(daymode, image2)
        vs.stop()
        logging.info("Motion Tracking is Suppressed per variable MOTION_TRACK_ON=%s",
                     MOTION_TRACK_ON)
        stopMotion = True

    if TIMELAPSE_ON and MOTION_TRACK_ON:
        tlstr = " and " + tlstr
    display_info(moCnt, tlCnt)  # Display config.py settings

    if LOG_TO_FILE_ON:
        logging.info("LOG_TO_FILE_ON=%s Logging to Console Disabled.",
                     LOG_TO_FILE_ON)
        logging.info("Sending Console Messages to %s", LOG_FILE_PATH)
        logging.info("Entering Loop for %s%s", mostr, tlstr)
    else:
        if PLUGIN_ON:
            logging.info("plugin %s - Start %s%s Loop ...",
                         PLUGIN_NAME, mostr, tlstr)
        else:
            logging.info("Start %s%s Loop ... ctrl-c Exits", mostr, tlstr)
    if MOTION_TRACK_ON and not checkSchedStart(startMO):
        logging.info('Motion Track: MOTION_START_AT = "%s"', MOTION_START_AT)
        logging.info("Motion Track: Sched Start Set For %s  Please Wait ...",
                     startMO)
    if TIMELAPSE_ON and not checkSchedStart(startTL):
        logging.info('Timelapse   : TIMELAPSE_START_AT = "%s"', TIMELAPSE_START_AT)
        logging.info("Timelapee   : Sched Start Set For %s  Please Wait ...",
                     startTL)
    logging.info("daymode=%s  MOTION_DOTS_ON=%s ", daymode, MOTION_DOTS_ON)
    dotCount = show_dots(MOTION_DOTS_MAX)  # reset motion dots

    first_pano = True  # Force a pano sequence on startup
    firstTimeLapse = True  # Force a timelapse on startup
    while True:  # Start main program Loop.
        motionFound = False
        if (MOTION_TRACK_ON and (not MOTION_NUM_RECYCLE_ON)
                and (motionNumCount > MOTION_NUM_START + MOTION_NUM_MAX)
                and (not stopMotion)):
            logging.warning("MOTION_NUM_RECYCLE_ON=%s and motionNumCount %i Exceeds %i",
                            MOTION_NUM_RECYCLE_ON, motionNumCount,
                            MOTION_NUM_START + MOTION_NUM_MAX)
            logging.warning("Suppressing Further Motion Tracking")
            logging.warning("To Reset: Change %s Settings or Archive Images",
                            CONFIG_FILENAME)
            logging.warning("Then Delete %s and Restart %s \n",
                            NUM_PATH_MOTION, PROG_NAME)
            takeMotion = False
            stopMotion = True
        if stop_timelapse and stopMotion and not PANO_ON and not VIDEO_REPEAT_ON:
            logging.warning("NOTICE: Motion, Timelapse, Pano and Video Repeat are Disabled")
            logging.warning("per Num Recycle=False and "
                            "Max Counter Reached or TIMELAPSE_EXIT_SEC Settings")
            logging.warning("Change %s Settings or Archive/Save Media Then",
                            CONFIG_FILENAME)
            logging.warning("Delete appropriate .dat File(s) to Reset Counter(s)")
            logging.warning("Exiting %s %s \n", PROG_NAME, PROG_VER)
            sys.exit(1)
        # if required check free disk space and delete older files (jpg)
        if SPACE_TIMER_HOURS > 0:
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
        # use image2 to check daymode as image1 may be average
        # that changes slowly, and image1 may not be updated
        if MOTION_TRACK_ON:
            if daymode != check_if_day_stream(daymode, image2):
                daymode = not daymode
                image2 = vs.read()
                image1 = image2
            else:
                image2 = vs.read()
        elif TIMELAPSE_ON:
            vs = PiVideoStream().start()
            time.sleep(0.5)
            image2 = vs.read()  # use video stream to check for daymode
            vs.stop()
            # check the timer for measuring pixel average of a stream frame
        pix_ave_timer, take_pix_ave = check_timer(pix_ave_timer, PIX_AVE_TIMER_SEC)
        if take_pix_ave:
            pixAve = get_stream_pix_ave(image2)
            daymode = check_if_day_stream(daymode, image2)
            if daymode != check_if_day_stream(daymode, image2):
                daymode = not daymode
        if not daymode and TIMELAPSE_ON:
            time.sleep(0.01)  # short delay to aviod high cpu usage at night

        if not time_to_sleep(daymode):
            # Don't take images if IMAGE_NO_NIGHT_SHOTS
            # or IMAGE_NO_DAY_SHOTS settings are valid
            if TIMELAPSE_ON and checkSchedStart(startTL):
                # Check for a scheduled date/time to start timelapse
                if firstTimeLapse:
                    timelapse_timer = datetime.datetime.now()
                    firstTimeLapse = False
                    take_timelapse = True
                else:
                    timelapse_timer, take_timelapse = check_timer(timelapse_timer,
                                                                  TIMELAPSE_TIMER_SEC)

                if ((not stop_timelapse) and take_timelapse and
                        TIMELAPSE_EXIT_SEC > 0):
                    if ((datetime.datetime.now() -
                         timelapseExitStart).total_seconds() >
                            TIMELAPSE_EXIT_SEC):
                        logging.info("TIMELAPSE_EXIT_SEC=%i Exceeded.",
                                     TIMELAPSE_EXIT_SEC)
                        logging.info("Suppressing Further Timelapse Images")
                        logging.info("To RESET: Restart %s to Restart "
                                     "TIMELAPSE_EXIT_SEC Timer. \n", PROG_NAME)
                        # Suppress further timelapse images
                        take_timelapse = False
                        stop_timelapse = True
                if ((not stop_timelapse) and TIMELAPSE_NUM_ON
                        and (not TIMELAPSE_NUM_RECYCLE_ON)):
                    if (TIMELAPSE_NUM_MAX > 0 and
                            timelapseNumCount > (TIMELAPSE_NUM_START + TIMELAPSE_NUM_MAX)):
                        logging.warning("TIMELAPSE_NUM_RECYCLE_ON=%s and Counter=%i Exceeds %i",
                                        TIMELAPSE_NUM_RECYCLE_ON, timelapseNumCount,
                                        TIMELAPSE_NUM_START + TIMELAPSE_NUM_MAX)
                        logging.warning("Suppressing Further Timelapse Images")
                        logging.warning("To RESET: Change %s Settings or Archive Images",
                                        CONFIG_FILENAME)
                        logging.warning("Then Delete %s and Restart %s \n",
                                        NUM_PATH_TIMELAPSE, PROG_NAME)
                        # Suppress further timelapse images
                        take_timelapse = False
                        stop_timelapse = True
                if take_timelapse and (not stop_timelapse):
                    # Reset the timelapse timer
                    if MOTION_DOTS_ON and MOTION_TRACK_ON:
                        # reset motion dots
                        dotCount = show_dots(MOTION_DOTS_MAX + 2)
                    else:
                        print("")
                    if PLUGIN_ON:
                        if TIMELAPSE_EXIT_SEC > 0:
                            exitSecProgress = (datetime.datetime.now() -
                                               timelapseExitStart).total_seconds()
                            logging.info("%s Sched TimeLapse  daymode=%s  Timer=%i sec"
                                         "  ExitSec=%i/%i Status",
                                         PLUGIN_NAME, daymode, TIMELAPSE_TIMER_SEC,
                                         exitSecProgress, TIMELAPSE_EXIT_SEC)
                        else:
                            logging.info("%s Sched TimeLapse  daymode=%s"
                                         "  Timer=%i sec  ExitSec=%i 0=Continuous",
                                         PLUGIN_NAME, daymode,
                                         TIMELAPSE_TIMER_SEC, TIMELAPSE_EXIT_SEC)
                    else:
                        if TIMELAPSE_EXIT_SEC > 0:
                            exitSecProgress = (datetime.datetime.now() -
                                               timelapseExitStart).total_seconds()
                            logging.info("Sched TimeLapse  daymode=%s  Timer=%i sec"
                                         "  ExitSec=%i/%i Status",
                                         daymode, TIMELAPSE_TIMER_SEC,
                                         exitSecProgress, TIMELAPSE_EXIT_SEC)
                        else:
                            logging.info("Sched TimeLapse  daymode=%s  Timer=%i sec"
                                         "  ExitSec=%i 0=Continuous",
                                         daymode, TIMELAPSE_TIMER_SEC,
                                         TIMELAPSE_EXIT_SEC)
                    tl_prefix = TIMELAPSE_PREFIX + IMAGE_NAME_PREFIX
                    filename = get_image_filename(tlPath, tl_prefix,
                                                  TIMELAPSE_NUM_ON,
                                                  timelapseNumCount)
                    if MOTION_TRACK_ON:
                        logging.info("Stop Motion Tracking PiVideoStream ...")
                        vs.stop()
                        time.sleep(STREAM_STOP_SEC)
                    # Time to take a Day or Night Time Lapse Image
                    if TIMELAPSE_PANTILT_ON and PANTILT_ON:
                        logging.info('Timelapse Pan Tilt at (%i, %i) cam_tl_pos %i/%i',
                                     pan, tilt, cam_tl_pos, len(TIMELAPSE_PANTILT_STOPS))
                        pantilthat.pan(pan)  # move pimoroni pantilt servos
                        time.sleep(PANTILT_SLEEP_SEC)
                        pantilthat.tilt(tilt)
                        time.sleep(PANTILT_SLEEP_SEC)
                    if daymode:
                        take_day_image(filename, TIMELAPSE_CAM_SLEEP_SEC)
                    else:
                        take_night_image(filename, pixAve)
                    timelapseNumCount = postImageProcessing(TIMELAPSE_NUM_ON,
                                                            TIMELAPSE_NUM_START,
                                                            TIMELAPSE_NUM_MAX,
                                                            timelapseNumCount,
                                                            TIMELAPSE_NUM_RECYCLE_ON,
                                                            NUM_PATH_TIMELAPSE,
                                                            filename, daymode)
                    if TIMELAPSE_PANTILT_ON and PANTILT_ON:
                        cam_tl_pos += 1
                        if cam_tl_pos >= len(TIMELAPSE_PANTILT_STOPS):
                            cam_tl_pos = 0
                        pan, tilt = TIMELAPSE_PANTILT_STOPS[cam_tl_pos]

                    if MOTION_TRACK_ON:
                        logging.info("Restart Motion Tracking PiVideoStream ....")
                        vs = PiVideoStream().start()
                        vs.camera.rotation = IMAGE_ROTATION
                        vs.camera.hflip = IMAGE_HFLIP
                        vs.camera.vflip = IMAGE_VFLIP
                        time.sleep(1)  # Allow camera to warm up and stream to start

                    if TIMELAPSE_RECENT_MAX > 0:
                        saveRecent(TIMELAPSE_RECENT_MAX, TIMELAPSE_RECENT_DIR,
                                   filename, tl_prefix)
                    if TIMELAPSE_MAX_FILES > 0:
                        deleteOldFiles(TIMELAPSE_MAX_FILES, TIMELAPSE_DIR,
                                       tl_prefix)
                    dotCount = show_dots(MOTION_DOTS_MAX)

                    tlPath = subDirChecks(TIMELAPSE_SUBDIR_MAX_HOURS,
                                          TIMELAPSE_SUBDIR_MAX_FILES,
                                          TIMELAPSE_DIR, TIMELAPSE_PREFIX)
                    next_timelapse_time = timelapse_timer + datetime.timedelta(seconds=TIMELAPSE_TIMER_SEC)
                    next_timelapse_at = ("%02d:%02d:%02d" % (next_timelapse_time.hour,
                                                             next_timelapse_time.minute,
                                                             next_timelapse_time.second))
                    logging.info('Next Timelapse at %s  Waiting ...',
                                 next_timelapse_at)
                    pantilt_go_home()

            if PANTILT_ON and PANO_ON:
                # force a pano on first startup then go by timer.
                if first_pano:
                    first_pano = False
                    start_pano = True
                    pano_seq_num = get_current_count(NUM_PATH_PANO,
                                                     PANO_NUM_START)
                    pano_timer = datetime.datetime.now()
                else:
                    # Check if pano timer expired and if so start a pano sequence
                    pano_timer, start_pano = check_timer(pano_timer, PANO_TIMER_SEC)

                if start_pano:
                     if (PANO_DAYONLY_ON and daymode) or not PANO_DAYONLY_ON:
                          if MOTION_TRACK_ON:
                               logging.info("Stop Motion Tracking PiVideoStream ...")
                               vs.stop()
                               time.sleep(STREAM_STOP_SEC)
                          pano_seq_num = take_pano(pano_seq_num)
                          if MOTION_TRACK_ON:
                               logging.info("Restart Motion Tracking PiVideoStream ....")
                               vs = PiVideoStream().start()
                               vs.camera.rotation = IMAGE_ROTATION
                               vs.camera.hflip = IMAGE_HFLIP
                               vs.camera.vflip = IMAGE_VFLIP
                               time.sleep(1)
                     else:
                          logging.info('Pano Turned Off During Night per PANO_DAYONLY_ON=%s',
                                       PANO_DAYONLY_ON)

                     next_pano_time = pano_timer + datetime.timedelta(seconds=PANO_TIMER_SEC)
                     next_pano_at = ("%02d:%02d:%02d" % (next_pano_time.hour,
                                                         next_pano_time.minute,
                                                         next_pano_time.second))
                     logging.info('Next Pano at %s  Waiting ...',
                                   next_pano_at)


            if MOTION_TRACK_ON and checkSchedStart(startMO) and takeMotion and (not stopMotion):
                # IMPORTANT - Night motion tracking may not work very well
                #             due to long exposure times and low light
                image2 = vs.read()
                grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
                movePoint1 = get_track_point(grayimage1, grayimage2)
                grayimage1 = grayimage2
                if movePoint1 and not startTrack:
                    startTrack = True
                    trackTimeout = time.time()
                    startPos = movePoint1
                image2 = vs.read()
                grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
                movePoint2 = get_track_point(grayimage1, grayimage2)
                if movePoint2 and startTrack:   # Two sets of movement required
                    trackLen = track_distance(startPos, movePoint2)
                    # wait until track well started
                    if trackLen > TRACK_TRIG_LEN_MIN:
                        # Reset tracking timer object moved
                        trackTimeout = time.time()
                        if MOTION_TRACK_INFO_ON:
                            logging.info("Track Progress From(%i,%i) To(%i,%i) trackLen=%i/%i px",
                                         startPos[0], startPos[1],
                                         movePoint2[0], movePoint2[1],
                                         trackLen, TRACK_TRIG_LEN)
                    # Track length triggered
                    if trackLen >= TRACK_TRIG_LEN:
                        # reduce chance of two objects at different positions
                        if trackLen >= TRACK_TRIG_LEN_MAX:
                            motionFound = False
                            if MOTION_TRACK_INFO_ON:
                                logging.info("TrackLen %i px Exceeded %i px Max Trig Len Allowed.",
                                             trackLen, TRACK_TRIG_LEN_MAX)
                        else:
                            motionFound = True
                            if PLUGIN_ON:
                                logging.info("%s Motion Triggered Start(%i,%i)"
                                             "  End(%i,%i) trackLen=%.i/%i px",
                                             PLUGIN_NAME, startPos[0], startPos[1],
                                             movePoint2[0], movePoint2[1],
                                             trackLen, TRACK_TRIG_LEN)
                            else:
                                logging.info("Motion Triggered Start(%i,%i)"
                                             "  End(%i,%i) trackLen=%i/%i px",
                                             startPos[0], startPos[1],
                                             movePoint2[0], movePoint2[1],
                                             trackLen, TRACK_TRIG_LEN)
                        image1 = vs.read()
                        image2 = image1
                        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                        grayimage2 = grayimage1
                        startTrack = False
                        startPos = []
                        trackLen = 0.0
                # Track timed out
                if (time.time() - trackTimeout > trackTimer) and startTrack:
                    image1 = vs.read()
                    image2 = image1
                    grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                    grayimage2 = grayimage1
                    if MOTION_TRACK_INFO_ON:
                        logging.info("Track Timer %.2f sec Exceeded. Reset Track",
                                     trackTimer)
                    startTrack = False
                    startPos = []
                    trackLen = 0.0
                if MOTION_FORCE_SEC > 0:
                    motion_force_timer, motion_force_start = check_timer(motion_force_timer,
                                                                         MOTION_FORCE_SEC)
                else:
                    motion_force_start = False

                if motion_force_start:
                    image1 = vs.read()
                    image2 = image1
                    grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                    grayimage2 = grayimage1
                    grayimage2 = grayimage1
                    dotCount = show_dots(MOTION_DOTS_MAX + 2) # New Line
                    logging.info("No Motion Detected for %s minutes. "
                                 "Taking Forced Motion Image.",
                                 (MOTION_FORCE_SEC / 60))
                if motionFound or motion_force_start:
                    motion_prefix = MOTION_PREFIX + IMAGE_NAME_PREFIX
                    if MOTION_TRACK_QUICK_PIC_ON:  # Do not stop PiVideoStream
                        filename = get_image_filename(moPath,
                                                      motion_prefix,
                                                      MOTION_NUM_ON,
                                                      motionNumCount)
                        take_mo_quick_pic(image2, filename)
                        motionNumCount = postImageProcessing(MOTION_NUM_ON,
                                                             MOTION_NUM_START,
                                                             MOTION_NUM_MAX,
                                                             motionNumCount,
                                                             MOTION_NUM_RECYCLE_ON,
                                                             NUM_PATH_MOTION,
                                                             filename, daymode)
                        if MOTION_RECENT_MAX > 0:
                            saveRecent(MOTION_RECENT_MAX,
                                       MOTION_RECENT_DIR,
                                       filename,
                                       motion_prefix)
                    else:
                        if MOTION_TRACK_ON:
                            logging.info("Stop PiVideoStream ...")
                            vs.stop()
                            time.sleep(STREAM_STOP_SEC)

                        # check if motion Quick Time Lapse option is On.
                        # This option supersedes MOTION_VIDEO_ON
                        if MOTION_TRACK_MINI_TL_ON and daymode:
                            filename = get_image_filename(moPath,
                                                          motion_prefix,
                                                          MOTION_NUM_ON,
                                                          motionNumCount)
                            with picamera.PiCamera() as camera:
                                camera.resolution = (image_width, image_height)
                                camera.vflip = IMAGE_VFLIP
                                camera.hflip = IMAGE_HFLIP
                                # valid rotation values 0, 90, 180, 270
                                camera.rotation = IMAGE_ROTATION
                                time.sleep(MOTION_CAM_SLEEP)
                                # This uses yield to loop through time lapse
                                # sequence but does not seem to be faster
                                # due to writing images
                                camera.capture_sequence(take_mo_mini_timelapse(moPath,
                                                                               motion_prefix,
                                                                               MOTION_NUM_ON,
                                                                               motionNumCount,
                                                                               daymode,
                                                                               NUM_PATH_MOTION))
                                camera.close()
                                motionNumCount = get_current_count(NUM_PATH_MOTION,
                                                                   MOTION_NUM_START)
                        else:
                            if MOTION_VIDEO_ON:
                                filename = getVideoName(MOTION_PATH,
                                                        motion_prefix,
                                                        MOTION_NUM_ON,
                                                        motionNumCount)
                                take_mo_video(filename, MOTION_VIDEO_TIMER_SEC,
                                          MOTION_VIDEO_FPS)
                            else:
                                filename = get_image_filename(moPath,
                                                              motion_prefix,
                                                              MOTION_NUM_ON,
                                                              motionNumCount)
                                if daymode:
                                    take_day_image(filename, MOTION_CAM_SLEEP)
                                else:
                                    take_night_image(filename, pixAve)
                            motionNumCount = postImageProcessing(MOTION_NUM_ON,
                                                                 MOTION_NUM_START,
                                                                 MOTION_NUM_MAX,
                                                                 motionNumCount,
                                                                 MOTION_NUM_RECYCLE_ON,
                                                                 NUM_PATH_MOTION,
                                                                 filename,
                                                                 daymode)
                            logging.info("Waiting for Next Motion Tracking Event ...")
                            if MOTION_RECENT_MAX > 0:
                                if not MOTION_VIDEO_ON:
                                   # prevent h264 video files from
                                   # being copied to recent
                                    saveRecent(MOTION_RECENT_MAX,
                                               MOTION_RECENT_DIR,
                                               filename,
                                               motion_prefix)
                        if MOTION_TRACK_ON:
                            logging.info("Restart PiVideoStream ....")
                            vs = PiVideoStream().start()
                            vs.camera.rotation = IMAGE_ROTATION
                            vs.camera.hflip = IMAGE_HFLIP
                            vs.camera.vflip = IMAGE_VFLIP
                            time.sleep(1)
                            image1 = vs.read()
                            image2 = image1
                            grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                            grayimage2 = grayimage1
                            trackLen = 0.0
                            trackTimeout = time.time()
                            startPos = []
                            startTrack = False
                    pantilt_go_home()
                    moPath = subDirChecks(MOTION_SUBDIR_MAX_HOURS,
                                          MOTION_SUBDIR_MAX_FILES,
                                          MOTION_DIR, MOTION_PREFIX)

                    if motionFound and motionCode:
                        # ===========================================
                        # Put your user code in userMotionCode() function
                        # In the File user_motion_code.py
                        # ===========================================
                        try:
                            user_motion_code.userMotionCode(filename)
                            dotCount = show_dots(MOTION_DOTS_MAX)
                        except ValueError:
                            logging.error("Problem running userMotionCode function from File %s",
                                          userMotionFilePath)
                else:
                    # show progress dots when no motion found
                    dotCount = show_dots(dotCount)

#------------------------------------------------------------------------------
def videoRepeat():
    '''
    This is a special dash cam video mode
    that overrides both timelapse and motion tracking settings
    It has it's own set of settings to manage start, video duration,
    number recycle mode, Etc.
    '''
    # Check if folder exist and create if required
    if not os.path.isdir(VIDEO_DIR):
        logging.info("Create videoRepeat Folder %s", VIDEO_DIR)
        os.makedirs(VIDEO_DIR)
    print("--------------------------------------------------------------------")
    print("VideoRepeat . VIDEO_REPEAT_ON=%s" % VIDEO_REPEAT_ON)
    print("   Info ..... Size=%ix%i  VIDEO_PREFIX=%s  VIDEO_FILE_SEC=%i seconds  VIDEO_FPS=%i"
          % (image_width, image_height, VIDEO_PREFIX, VIDEO_FILE_SEC, VIDEO_FPS))
    print("   Vid Path . VIDEO_DIR=%s" % VIDEO_DIR)
    print("   Sched .... VIDEO_START_AT=%s blank=Off or Set Valid Date and/or Time to Start Sequence"
          % VIDEO_START_AT)
    print("   Timer .... VIDEO_SESSION_MIN=%i minutes  0=Continuous" % VIDEO_SESSION_MIN)
    print("   Num Seq .. VIDEO_NUM_ON=%s  VIDEO_NUM_RECYCLE_ON=%s  VIDEO_NUM_START=%i"
          "  VIDEO_NUM_MAX=%i 0=Continuous"
          % (VIDEO_NUM_ON, VIDEO_NUM_RECYCLE_ON, VIDEO_NUM_START, VIDEO_NUM_MAX))
    print("--------------------------------------------------------------------")
    print("WARNING: VIDEO_REPEAT_ON=%s Suppresses TimeLapse and Motion Settings."
          % VIDEO_REPEAT_ON)
    startVideoRepeat = getSchedStart(VIDEO_START_AT)
    if not checkSchedStart(startVideoRepeat):
        logging.info('Video Repeat: VIDEO_START_AT = "%s" ', VIDEO_START_AT)
        logging.info("Video Repeat: Sched Start Set For %s  Please Wait ...",
                     startVideoRepeat)
        while not checkSchedStart(startVideoRepeat):
            pass
    videoStartTime = datetime.datetime.now()
    lastSpaceCheck = datetime.datetime.now()
    videoCount = 0
    videoNumCounter = VIDEO_NUM_START
    keepRecording = True
    while keepRecording:
        # if required check free disk space and delete older files
        # Set variables SPACE_TARGET_EXT='mp4' and
        # SPACE_MEDIA_DIR= to appropriate folder path
        if SPACE_TIMER_HOURS > 0:
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
        filename = getVideoName(VIDEO_DIR, VIDEO_PREFIX,
                                VIDEO_NUM_ON, videoNumCounter)
        take_mo_video(filename, VIDEO_FILE_SEC, VIDEO_FPS)
        timeUsed = (datetime.datetime.now() - videoStartTime).total_seconds()
        timeRemaining = (VIDEO_SESSION_MIN*60 - timeUsed) / 60.0
        videoCount += 1
        if VIDEO_NUM_ON:
            videoNumCounter += 1
            if VIDEO_NUM_MAX > 0:
                if videoNumCounter - VIDEO_NUM_START > VIDEO_NUM_MAX:
                    if VIDEO_NUM_RECYCLE_ON:
                        videoNumCounter = VIDEO_NUM_START
                        logging.info("Restart Numbering: VIDEO_NUM_RECYCLE_ON=%s "
                                     "and VIDEO_NUM_MAX=%i Exceeded",
                                     VIDEO_NUM_RECYCLE_ON, VIDEO_NUM_MAX)
                    else:
                        keepRecording = False
                        logging.info("Exit since VIDEO_NUM_RECYCLE_ON=%s "
                                     "and VIDEO_NUM_MAX=%i Exceeded  %i Videos Recorded",
                                     VIDEO_NUM_RECYCLE_ON, VIDEO_NUM_MAX, videoCount)
                logging.info("Recorded %i of %i Videos",
                             videoCount, VIDEO_NUM_MAX)
            else:
                logging.info("Recorded %i Videos  VIDEO_NUM_MAX=%i 0=Continuous",
                             videoCount, VIDEO_NUM_MAX)
        else:
            logging.info("Progress: %i Videos Recorded in Folder %s",
                         videoCount, VIDEO_DIR)
        if VIDEO_SESSION_MIN > 0:
            if timeUsed > VIDEO_SESSION_MIN * 60:
                keepRecording = False
                errorText = ("Stop Recording Since VIDEO_SESSION_MIN=%i minutes Exceeded \n",
                             VIDEO_SESSION_MIN)
                logging.warning(errorText)
                sys.stdout.write(errorText)
            else:
                logging.info("Remaining Time %.1f of %i minutes",
                             timeRemaining, VIDEO_SESSION_MIN)
        else:
            videoStartTime = datetime.datetime.now()
    logging.info("Exit: %i Videos Recorded in Folder %s",
                 videoCount, VIDEO_DIR)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    '''
    Initialization prior to launching
    appropriate pi-timolo options
    '''
    logging.info("Testing if Pi Camera is in Use")
    # Test if the pi camera is already in use
    ts = PiVideoStream().start()
    time.sleep(1)
    ts.stop()
    time.sleep(STREAM_STOP_SEC)
    logging.info("Pi Camera is Available.")
    if PLUGIN_ON:
        logging.info("Start pi-timolo per %s and plugins/%s.py Settings",
                     CONFIG_FILE_PATH, PLUGIN_NAME)
    else:
        logging.info("Start pi-timolo per %s Settings", CONFIG_FILE_PATH)

    if not VERBOSE_ON:
        print("NOTICE: Logging Disabled per variable VERBOSE_ON=False  ctrl-c Exits")

    try:
        pantilt_go_home()
        if VIDEO_REPEAT_ON:
            videoRepeat()
        else:
            timolo()
    except KeyboardInterrupt:
        print("")
        pantilt_go_home() # Ensure mouse is returned to home position
        if VERBOSE_ON:
            logging.info("User Pressed Keyboard ctrl-c")
            logging.info("Exiting %s %s", PROG_NAME, PROG_VER)
        else:
            sys.stdout.write("User Pressed Keyboard ctrl-c \n")
            sys.stdout.write("Exiting %s %s \n" % (PROG_NAME, PROG_VER))

    try:
        if PLUGIN_ON:
            if os.path.isfile(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.isfile(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
    except OSError as err:
        logging.warning("Failed To Remove File %s - %s", pluginCurrentpyc, err)
        sys.exit(1)
