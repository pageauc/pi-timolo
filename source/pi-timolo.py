#!/usr/bin/python
"""
pi-timolo - Raspberry Pi Long Duration Timelapse, Motion Tracking,
with Low Light Capability
written by Claude Pageau Jul-2017 (release 7.x)
This release uses OpenCV to do Motion Tracking.
It requires updated config.py
"""
from __future__ import print_function
print('Loading ....')
import datetime
import logging
import os
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
try:
    from dateutil.parser import parse
except ImportError:
   print("ERROR : Could Not Import dateutil.parser")
   print("        Disabling timelapseStartAt, motionStartAt and VideoStartAt")
   print("See https://github.com/pageauc/pi-timolo/wiki/Basic-Trouble-Shooting#problems-with-python-pip-install-on-wheezy")
   print("        ----------------")
   # Disable get_sched_start if import fails for Raspbian wheezy or Jessie
   timelapseStartAt = ""
   motionStartAt = ""
   videoStartAt = ""

try:
    # pyexiv2 Transfers image exif data to writeTextToImage
    # For python3 install of pyexiv2 lib
    # See https://github.com/pageauc/pi-timolo/issues/79
    # Bypass pyexiv2 if library Not Found
    import pyexiv2
except ImportError:
    pass

progVer = "ver 11.00"   # Requires Latest 10.x release of config.py
__version__ = "11.00"   # May test for version number at a future time

mypath = os.path.abspath(__file__) # Find the full path of this python script
# get the path location only (excluding script name)
baseDir = os.path.dirname(mypath)
baseFileName = os.path.splitext(os.path.basename(mypath))[0]
progName = os.path.basename(__file__)
logFilePath = os.path.join(baseDir, baseFileName + ".log")
print('%s %s  written by Claude Pageau' % (progName, progVer))

# Check for config.py variable file to import and error out if not found.
configFilePath = os.path.join(baseDir, "config.py")
if not os.path.isfile(configFilePath):
    print('%s File Not Found. Cannot Import Configuration Variables.'
          % configFilePath)
    print('Run Console Command Below to Download File from GitHub Repo')
    print('wget -O config.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py')
    sys.exit(1)
else:
    # Read Configuration variables from config.py file
    print('Import Configuration Variables from File %s' % configFilePath)
    from config import *

# Setup Logging now that variables are imported from config.py/plugin
if logDataToFile:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=logFilePath,
                        filemode='w')
    logging.info("Sending Logging Data to %s  (Console Messages Disabled)",
                 logFilePath)
elif verbose:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Logging to Console per Variable verbose=True")
else:
    logging.basicConfig(level=logging.CRITICAL,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
try:
    import cv2
except ImportError:
    if sys.version_info > (2, 9):
        logging.error("python3 Failed to import cv2 opencv ver 3.x")
        logging.error("Try installing opencv for python3")
        logging.error("See https://github.com/pageauc/opencv3-setup")
    else:
        logging.error("python2 Failed to import cv2")
        logging.error("Try reinstalling per command")
        logging.error("sudo apt-get install python-opencv")
    logging.error("Exiting %s Due to Error", progName)
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
    logging.error("Exiting %s Due to Error", progName)
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
    logging.error("Exiting %s Due to Error", progName)
    sys.exit(1)
else:
    logging.info("Pi Camera Module is Enabled and Connected %s", camResult)

if pluginEnable:     # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(baseDir, "plugins")
    # Check if there is a .py at the end of pluginName variable
    if pluginName.endswith('.py'):
        pluginName = pluginName[:-3]    # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, pluginName + '.py')
    logging.info("pluginEnabled - loading pluginName %s", pluginPath)
    if not os.path.isdir(pluginDir):
        logging.error("plugin Directory Not Found at %s", pluginDir)
        logging.error("Rerun github curl install script to install plugins")
        logging.error("https://github.com/pageauc/pi-timolo/wiki/"
                      "How-to-Install-or-Upgrade#quick-install")
        logging.error("Exiting %s Due to Error", progName)
        sys.exit(1)
    elif not os.path.isfile(pluginPath):
        logging.error("File Not Found pluginName %s", pluginPath)
        logging.error("Check Spelling of pluginName Value in %s",
                      configFilePath)
        logging.error("------- Valid Names -------")
        validPlugin = glob.glob(pluginDir + "/*py")
        validPlugin.sort()
        for entry in validPlugin:
            pluginFile = os.path.basename(entry)
            plugin = pluginFile.rsplit('.', 1)[0]
            if not ((plugin == "__init__") or (plugin == "current")):
                logging.error("        %s", plugin)
        logging.error("------- End of List -------")
        logging.error("Note: pluginName Should Not have .py Ending.")
        logging.error("or Rerun github curl install command.  See github wiki")
        logging.error("https://github.com/pageauc/pi-timolo/wiki/"
                      "How-to-Install-or-Upgrade#quick-install")
        logging.error("Exiting %s Due to Error", progName)
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
            logging.error("Exiting %s Due to Error", progName)
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
            logging.warn("Failed Removal of %s - %s", pluginCurrentpyc, err)
else:
    logging.info("No Plugin Enabled per pluginEnable=%s", pluginEnable)

#==================================
#      System Variables
# Should Not need to be customized
#==================================
SECONDS2MICRO = 1000000    # Used to convert from seconds to microseconds
nightMaxShut = int(nightMaxShutSec * SECONDS2MICRO)
# default=5 seconds IMPORTANT- 6 seconds works sometimes
# but occasionally locks RPI and HARD reboot required to clear
darkAdjust = int((SECONDS2MICRO/5.0) * nightDarkAdjust)
daymode = False            # default should always be False.
motionPath = os.path.join(baseDir, motionDir)  # Store Motion images
# motion dat file to save currentCount
motionNumPath = os.path.join(baseDir, motionPrefix + baseFileName + ".dat")
motionStreamStopSec = .5  # default= 0.5 seconds  Time to close stream thread
timelapsePath = os.path.join(baseDir, timelapseDir)  # Store Time Lapse images
# timelapse dat file to save currentCount
timelapseNumPath = os.path.join(baseDir, timelapsePrefix + baseFileName + ".dat")
lockFilePath = os.path.join(baseDir, baseFileName + ".sync")
# Video Stream Settings for motion Tracking using opencv motion tracking
CAMERA_WIDTH = 320     # width of video stream
CAMERA_HEIGHT = 240    # height of video stream
# Colors for drawing lines
cvWhite = (255, 255, 255)
cvBlack = (0, 0, 0)
cvBlue = (255, 0, 0)
cvGreen = (0, 255, 0)
cvRed = (0, 0, 255)
LINE_THICKNESS = 1     # Thickness of opencv drawing lines
LINE_COLOR = cvWhite   # color of lines to highlight motion stream area
# Check if imageShowStream variable exists in config.py
# To show stream rectange on still image
try:
    imageShowStream
except:
    imageShowStream = False
bigImage = motionTrackQPBigger  # increase size of motionTrackQuickPic image
bigImageWidth = int(CAMERA_WIDTH * bigImage)
bigImageHeight = int(CAMERA_HEIGHT * bigImage)
CAMERA_FRAMERATE = motionTrackFrameRate  # camera framerate
TRACK_TRIG_LEN = motionTrackTrigLen  # Length of track to trigger speed photo
# Don't track progress until this Len reached.
TRACK_TRIG_LEN_MIN = int(motionTrackTrigLen / 6)
# Set max overshoot triglen allowed half cam height
TRACK_TRIG_LEN_MAX = int(CAMERA_HEIGHT / 2)
# Timeout seconds Stops motion tracking when no activity
TRACK_TIMEOUT = motionTrackTimeOut
# OpenCV Contour sq px area must be greater than this.
MIN_AREA = motionTrackMinArea
BLUR_SIZE = 10  # OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20  # OpenCV setting for difference image threshold
if debug:
    verbose = True
# Fix range Errors  Use zero to set default quality to 85
if imageJpegQuality < 1:
    imageJpegQuality = 85
elif imageJpegQuality > 100:
    imageJpegQuality = 100

#------------------------------------------------------------------------------
def userMotionCodeHere():
    """
    Users can put code here that needs to be run
    prior to taking motion capture images
    Eg Notify or activate something.
    """
    # Insert User code Below
    return

#------------------------------------------------------------------------------
class PiVideoStream:
    """
    Create a picamera in memory video stream and
    return a frame when update called
    """
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT),
                 framerate=CAMERA_FRAMERATE,
                 rotation=0,
                 hflip=False, vflip=False):
        # initialize the camera and stream
        try:
            self.camera = PiCamera()
        except:
            logging.error("PiCamera Already in Use by Another Process")
            logging.error("Exiting %s Due to Error", progName)
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
        self.frame = None
        self.stopped = False

    def start(self):
        """ start the thread to read frames from the video stream"""
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        """ keep looping infinitely until the thread is stopped"""
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
        """ return the frame most recently read """
        return self.frame

    def stop(self):
        """ indicate that the thread should be stopped """
        self.stopped = True

#------------------------------------------------------------------------------
def shut2Sec(shutspeed):
    """ Convert camera shutter speed setting to string """
    shutspeedSec = shutspeed/float(SECONDS2MICRO)
    shutstring = str("%.4f") % (shutspeedSec)
    return shutstring

#------------------------------------------------------------------------------
def showTime():
    """ Show current date time in text format """
    rightNow = datetime.datetime.now()
    currentTime = ("%04d-%02d-%02d %02d:%02d:%02d" % (rightNow.year,
                                                      rightNow.month,
                                                      rightNow.day,
                                                      rightNow.hour,
                                                      rightNow.minute,
                                                      rightNow.second))
    return currentTime

#------------------------------------------------------------------------------
def showDots(dotcnt):
    """
    If motionShowDots=True then display a progress
    dot for each cycle.  If motionTrackOn then this would
    normally be too fast and should be turned off
    """
    if motionDotsOn:
        if motionTrackOn and verbose:
            dotcnt += 1
            if dotcnt > motionDotsMax + 2:
                print("")
                dotcnt = 0
            elif dotcnt > motionDotsMax:
                print("")
                stime = showTime() + " ."
                sys.stdout.write(stime)
                sys.stdout.flush()
                dotcnt = 0
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
    return dotcnt

#------------------------------------------------------------------------------
def checkConfig():
    """
    Check if both motion track and
    timelapse are disabled and error out
    """
    if not motionTrackOn and not timelapseOn:
        errorText = ("Both Motion and Timelapse are turned OFF"
                     " - motionTrackOn=%s timelapseOn=%s \n"
                     % (motionTrackOn, timelapseOn))
        if verbose:
            logging.error(errorText)
        else:
            sys.stdout.write(errorText)
        sys.exit(1)

#------------------------------------------------------------------------------
def displayInfo(motioncount, timelapsecount):
    """ Display variable settings with plugin overlays if required """
    if verbose:
        print("----------------------------------- Settings "
              "-----------------------------------")
        print("Config File .. configName=%s  configTitle=%s"
              % (configName, configTitle))
        if pluginEnable:
            print("     Plugin .. pluginEnable=%s  pluginName=%s"
                  " (Overlays %s Variable Settings)"
                  % (pluginEnable, pluginName, configName))
        else:
            print("     Plugin .. pluginEnable=%s  Disabled (Using Only %s Settings)"
                  % (pluginEnable, configName))
        print("")
        print("Image Info ... Size=%ix%i  Prefix=%s"
              "  VFlip=%s  HFlip=%s  Rotation=%i  Preview=%s"
              % (imageWidth, imageHeight, imageNamePrefix,
                 imageVFlip, imageHFlip, imageRotation, imagePreview))
        print("               JpegQuality=%i where 1=Low 100=High(Min Compression) 0=85"
              % (imageJpegQuality))
        print("   Low Light.. nightTwilightThreshold=%i"
              "  nightDarkThreshold=%i  nightBlackThreshold=%i"
              % (nightTwilightThreshold, nightDarkThreshold, nightBlackThreshold))
        print("               nightMaxShutSec=%.2f  nightMaxISO=%i"
              "  nightDarkAdjust=%.2f  nightSleepSec=%i"
              % (nightMaxShutSec, nightMaxISO, nightDarkAdjust, nightSleepSec))
        print("   No Shots .. noNightShots=%s   noDayShots=%s"
              % (noNightShots, noDayShots))

        if showDateOnImage:
            print("   Img Text .. On=%s  Bottom=%s (False=Top)  WhiteText=%s (False=Black)"
                  % (showDateOnImage, showTextBottom, showTextWhite))
            print("               showTextWhiteNight=%s  showTextFontSize=%i px height"
                  % (showTextWhiteNight, showTextFontSize))
        else:
            print("    No Text .. showDateOnImage=%s  Text on Image is Disabled"
                  % (showDateOnImage))
        print("")
        if motionTrackOn:
            print("Motion Track.. On=%s  Prefix=%s  MinArea=%i sqpx"
                  "  TrigLen=%i-%i px  TimeOut=%i sec"
                  % (motionTrackOn, motionPrefix, motionTrackMinArea,
                     motionTrackTrigLen, TRACK_TRIG_LEN_MAX, motionTrackTimeOut))
            print("               motionTrackInfo=%s   motionDotsOn=%s"
                  % (motionTrackInfo, motionDotsOn))
            print("   Stream .... size=%ix%i  framerate=%i fps"
                  "  motionStreamStopSec=%.2f  QuickPic=%s"
                  % (CAMERA_WIDTH, CAMERA_HEIGHT, motionTrackFrameRate,
                     motionStreamStopSec, motionTrackQuickPic))
            print("   Img Path .. motionPath=%s  motionCamSleep=%.2f sec"
                  % (motionPath, motionCamSleep))
            print("   Sched ..... motionStartAt %s blank=Off or"
                  " Set Valid Date and/or Time to Start Sequence"
                  % motionStartAt)
            print("   Force ..... forceTimer=%i min (If No Motion)"
                  % (motionForce/60))
            print("   Lockfile .. On=%s  Path=%s  NOTE: For Motion Images Only."
                  % (createLockFile, lockFilePath))

            if motionNumOn:
                print("   Num Seq ... motionNumOn=%s  numRecycle=%s"
                      "  numStart=%i   numMax=%i  current=%s"
                      % (motionNumOn, motionNumRecycle, motionNumStart,
                         motionNumMax, motioncount))
                print("   Num Path .. motionNumPath=%s " % (motionNumPath))
            else:
                print("   Date-Time.. motionNumOn=%s  Image Numbering is Disabled"
                      % (motionNumOn))

            if motionQuickTLOn:
                print("   Quick TL .. motionQuickTLOn=%s   motionQuickTLTimer=%i"
                      " sec  motionQuickTLInterval=%i sec (0=fastest)"
                      % (motionQuickTLOn, motionQuickTLTimer,
                         motionQuickTLInterval))
            else:
                print("   Quick TL .. motionQuickTLOn=%s  Quick Time Lapse Disabled"
                      % motionQuickTLOn)

            if motionVideoOn:
                print("   Video ..... motionVideoOn=%s   motionVideoTimer=%i"
                      " sec  motionVideoFPS=%i (superseded by QuickTL)"
                      % (motionVideoOn, motionVideoTimer, motionVideoFPS))
            else:
                print("   Video ..... motionVideoOn=%s  Motion Video is Disabled"
                      % motionVideoOn)
            print("   Sub-Dir ... motionSubDirMaxHours=%i (0-off)"
                  "  motionSubDirMaxFiles=%i (0=off)"
                  % (motionSubDirMaxHours, motionSubDirMaxFiles))
            print("   Recent .... motionRecentMax=%i (0=off)  motionRecentDir=%s"
                  % (motionRecentMax, motionRecentDir))
        else:
            print("Motion ....... motionTrackOn=%s  Motion Tracking is Disabled)"
                  % motionTrackOn)
        print("")
        if timelapseOn:
            print("Time Lapse ... On=%s  Prefix=%s   Timer=%i sec"
                  "   timelapseExitSec=%i (0=Continuous)"
                  % (timelapseOn, timelapsePrefix,
                     timelapseTimer, timelapseExitSec))
            print("               timelapseMaxFiles=%i" % (timelapseMaxFiles))
            print("   Img Path .. timelapsePath=%s  timelapseCamSleep=%.2f sec"
                  % (timelapsePath, timelapseCamSleep))
            print("   Sched ..... timelapseStartAt %s blank=Off or"
                  " Set Valid Date and/or Time to Start Sequence"
                  % timelapseStartAt)
            if timelapseNumOn:
                print("   Num Seq ... On=%s  numRecycle=%s  numStart=%i   numMax=%i  current=%s"
                      % (timelapseNumOn, timelapseNumRecycle, timelapseNumStart,
                         timelapseNumMax, timelapsecount))
                print("   Num Path .. numPath=%s" % (timelapseNumPath))
            else:
                print("   Date-Time.. motionNumOn=%s  Numbering Disabled"
                      % timelapseNumOn)
            print("   Sub-Dir ... timelapseSubDirMaxHours=%i (0=off)"
                  "  timelapseSubDirMaxFiles=%i (0=off)"
                  % (timelapseSubDirMaxHours, timelapseSubDirMaxFiles))
            print("   Recent .... timelapseRecentMax=%i (0=off)  timelapseRecentDir=%s"
                  % (timelapseRecentMax, timelapseRecentDir))
        else:
            print("Time Lapse ... timelapseOn=%s  Timelapse is Disabled"
                  % timelapseOn)
        print("")
        if spaceTimerHrs > 0:   # Check if disk mgmnt is enabled
            print("Disk Space  .. Enabled - Manage Target Free Disk Space."
                  " Delete Oldest %s Files if Required"
                  % (spaceFileExt))
            print("               Check Every spaceTimerHrs=%i (0=off)"
                  "  Target spaceFreeMB=%i (min=100 MB)  spaceFileExt=%s"
                  % (spaceTimerHrs, spaceFreeMB, spaceFileExt))
            print("               Delete Oldest spaceFileExt=%s  spaceMediaDir=%s"
                  % (spaceFileExt, spaceMediaDir))
        else:
            print("Disk Space  .. spaceTimerHrs=%i "
                  "(Disabled) - Manage Target Free Disk Space. Delete Oldest %s Files"
                  % (spaceTimerHrs, spaceFileExt))
            print("            .. Check Every spaceTimerHrs=%i (0=Off)"
                  "  Target spaceFreeMB=%i (min=100 MB)"
                  % (spaceTimerHrs, spaceFreeMB))
        print("")
        print("Logging ...... verbose=%s (True=Enabled False=Disabled)"
              % verbose)
        print("   Log Path .. logDataToFile=%s  logFilePath=%s"
              % (logDataToFile, logFilePath))
        print("--------------------------------- Log Activity "
              "---------------------------------")
    checkConfig()

#------------------------------------------------------------------------------
def subDirLatest(directory):
    """ Scan for directories and return most recent """
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
def subDirCreate(directory, prefix):
    """
    Create a subdirectory in directory with
    unique name based on prefix and date time
    """
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
    """ Count number of files in a folder path """
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
    """
    Note to self need to add error checking
    extract the date-time from the directory name
    """
    dirName = os.path.split(directory)[1] # split dir path and keep dirName
    # remove prefix from dirName so just date-time left
    dirStr = dirName.replace(prefix, '')
    # convert string to datetime
    dirDate = datetime.datetime.strptime(dirStr, "%Y-%m-%d-%H:%M")
    rightNow = datetime.datetime.now()   # get datetime now
    diff = rightNow - dirDate  # get time difference between dates
    days, seconds = diff.days, diff.seconds
    dirAgeHours = days * 24 + seconds // 3600  # convert to hours
    if dirAgeHours > hrsMax:   # See if hours are exceeded
        makeNewDir = True
        logging.info('MaxHrs %i Exceeds %i for %s',
                     dirAgeHours, hrsMax, directory)
    else:
        makeNewDir = False
    return makeNewDir

#------------------------------------------------------------------------------
def subDirChecks(maxHours, maxFiles, directory, prefix):
    """ Check if motion SubDir needs to be created """
    if maxHours < 1 and maxFiles < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', directory)
        subDirPath = directory
    else:
        subDirPath = subDirLatest(directory)
        if subDirPath == directory:   # No subDir Found
            logging.info('No sub folders Found in %s', directory)
            subDirPath = subDirCreate(directory, prefix)
        # Check MaxHours Folder Age Only
        elif (maxHours > 0 and maxFiles < 1):
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                subDirPath = subDirCreate(directory, prefix)
        elif (maxHours < 1 and maxFiles > 0):   # Check Max Files Only
            if subDirCheckMaxFiles(subDirPath, maxFiles):
                subDirPath = subDirCreate(directory, prefix)
        elif maxHours > 0 and maxFiles > 0:   # Check both Max Files and Age
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                if subDirCheckMaxFiles(subDirPath, maxFiles):
                    subDirPath = subDirCreate(directory, prefix)
                else:
                    logging.info('MaxFiles Not Exceeded in %s', subDirPath)
    os.path.abspath(subDirPath)
    return subDirPath

#------------------------------------------------------------------------------
def checkMediaPaths():
    """
    Checks for image folders and
    create them if they do not already exist.
    """
    if motionTrackOn:
        if not os.path.isdir(motionPath):
            logging.info("Create Motion Media Folder %s", motionPath)
            try:
                os.makedirs(motionPath)
            except OSError as err:
                logging.error("Could Not Create %s - %s", motionPath, err)
                sys.exit(1)
            if os.path.isfile(motionNumPath):
                logging.info("Delete Motion dat File %s", motionNumPath)
                os.remove(motionNumPath)
    if timelapseOn:
        if not os.path.isdir(timelapsePath):
            logging.info("Create TimeLapse Image Folder %s", timelapsePath)
            try:
                os.makedirs(timelapsePath)
            except OSError as err:
                logging.error("Could Not Create %s - %s", motionPath, err)
                sys.exit(1)
            if os.path.isfile(timelapseNumPath):
                logging.info("Delete TimeLapse dat file %s", timelapseNumPath)
                os.remove(timelapseNumPath)
    # Check for Recent Image Folders and create if they do not already exist.
    if motionRecentMax > 0:
        if not os.path.isdir(motionRecentDir):
            logging.info("Create Motion Recent Folder %s", motionRecentDir)
            try:
                os.makedirs(motionRecentDir)
            except OSError as err:
                logging.error('Failed to Create %s - %s', motionRecentDir, err)
                sys.exit(1)
    if timelapseRecentMax > 0:
        if not os.path.isdir(timelapseRecentDir):
            logging.info("Create TimeLapse Recent Folder %s",
                         timelapseRecentDir)
            try:
                os.makedirs(timelapseRecentDir)
            except OSError as err:
                logging.error('Failed to Create %s - %s',
                              timelapseRecentDir, err)
                sys.exit(1)

#------------------------------------------------------------------------------
def deleteOldFiles(maxFiles, dirPath, prefix):
    """
    Delete Oldest files gt or eq to maxfiles that match filename prefix
    """
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
    """
    Create a symlink file in recent folder (timelapse or motion subfolder)
    Delete Oldest symlink file if recentMax exceeded.
    """
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
def filesToDelete(mediaDirPath, extension=imageFormat):
    """
    Deletes files of specified format extension
    by walking folder structure from specified mediaDirPath
    """
    return sorted(
        (os.path.join(dirname, filename)
         for dirname, dirnames, filenames in os.walk(mediaDirPath)
         for filename in filenames
         if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime, reverse=True)

#------------------------------------------------------------------------------
def freeSpaceUpTo(freeMB, mediaDir, extension=imageFormat):
    """
    Walks mediaDir and deletes oldest files until spaceFreeMB is achieved.
    You should Use with Caution this feature.
    """
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
    """ Perform Disk space checking and Clean up
        if enabled and return datetime done
        to reset ready for next sched date/time"""
    if spaceTimerHrs > 0:   # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if (datetime.datetime.now() - lastSpaceCheck).total_seconds() > spaceTimerHrs * 3600:
            lastSpaceCheck = datetime.datetime.now()
            if spaceFreeMB < 100:   # set freeSpaceMB to reasonable value if too low
                diskFreeMB = 100
            else:
                diskFreeMB = spaceFreeMB
            logging.info('spaceTimerHrs=%i  diskFreeMB=%i  spaceMediaDir=%s spaceFileExt=%s',
                         spaceTimerHrs, diskFreeMB, spaceMediaDir, spaceFileExt)
            freeSpaceUpTo(diskFreeMB, spaceMediaDir, spaceFileExt)
    return lastSpaceCheck

#------------------------------------------------------------------------------
def getCurrentCount(numberpath, numberstart):
    """ Create a .dat file to store currentCount
        or read file if it already Exists"""
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
            if numberpath.find(motionPrefix) > 0:
                filePath = motionPath + "/*" + imageFormat
                fprefix = motionPath + motionPrefix + imageNamePrefix
            else:
                filePath = timelapsePath + "/*" + imageFormat
                fprefix = timelapsePath + timelapsePrefix + imageNamePrefix
            try:
               # Scan image folder for most recent file
               # and try to extract most recent number counter
                newest = max(glob.iglob(filePath), key=os.path.getctime)
                writeCount = newest[len(fprefix)+1:newest.find(imageFormat)]
            except:
                writeCount = numberstart
            try:
                numbercounter = int(writeCount)+1
            except ValueError:
                numbercounter = numberstart
            logging.warn("Found Invalid Data in %s Resetting Counter to %s",
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
    """
    function to write date/time stamp
    directly on top or bottom of images.
    """
    if showTextWhite:
        FOREGROUND = (255, 255, 255) # rgb settings for white text foreground
        textColour = "White"
    else:
        FOREGROUND = (0, 0, 0)  # rgb settings for black text foreground
        textColour = "Black"
        if showTextWhiteNight and (not currentDayMode):
            # rgb settings for black text foreground
            FOREGROUND = (255, 255, 255)
            textColour = "White"
    img = cv2.imread(imagename)
    height, width, channels = img.shape
    # centre text and compensate for graphics text being wider
    x = int((width/2) - (len(imagename)*2))
    if showTextBottom:
        y = (height - 50)  # show text at bottom of image
    else:
        y = 10  # show text at top of image
    TEXT = imageNamePrefix + datetoprint
    font_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
    font = ImageFont.truetype(font_path, showTextFontSize, encoding='unic')
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
    img.save(imagename)
    logging.info("Added %s Text [ %s ]", textColour, datetoprint)
    try:
        metadata.write() # Write previously saved exif data to image file
    except:
        logging.warn("Image EXIF Data Not Transferred.")
    logging.info("Saved %s", imagename)

#------------------------------------------------------------------------------
def postImageProcessing(numberon, counterstart, countermax, counter,
                        recycle, counterpath, filename, currentDaymode):
    """ If required process text to display directly on image """
    if not motionVideoOn:
        rightNow = datetime.datetime.now()
        if showDateOnImage:
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
            writeTextToImage(filename, imageText, currentDaymode)
        if createLockFile and motionTrackOn:
            createSyncLockFile(filename)
    # Process currentCount for next image if number sequence is enabled
    if numberon:
        counter += 1
        if countermax > 0:
            if counter > counterstart + countermax:
                if recycle:
                    counter = counterstart
                else:
                    counter = counterstart + countermax + 1
                    logging.warn("Exceeded Image Count numberMax=%i for %s \n",
                                 countermax, filename)
        # write next image counter number to dat file
        writeCount = str(counter)
        if not os.path.isfile(counterpath):
            logging.info("Create New Counter File writeCount=%s %s",
                         writeCount, counterpath)
            open(counterpath, 'w').close()
        f = open(counterpath, 'w+')
        f.write(str(writeCount))
        f.close()
        logging.info("Next Counter=%s %s", writeCount, counterpath)
    return counter

#------------------------------------------------------------------------------
def getVideoName(path, prefix, numberon, counter):
    """ build image file names by number sequence or date/time"""
    if numberon:
        if motionVideoOn or videoRepeatOn:
            filename = os.path.join(path, prefix + str(counter) + ".h264")
    else:
        if motionVideoOn or videoRepeatOn:
            rightNow = datetime.datetime.now()
            filename = ("%s/%s%04d%02d%02d-%02d%02d%02d.h264"
                        % (path, prefix,
                           rightNow.year, rightNow.month, rightNow.day,
                           rightNow.hour, rightNow.minute, rightNow.second))
    return filename

#------------------------------------------------------------------------------
def getImageName(path, prefix, numberon, counter):
    """ build image file names by number sequence or date/time """
    if numberon:
        filename = os.path.join(path, prefix + str(counter) + imageFormat)
    else:
        rightNow = datetime.datetime.now()
        filename = ("%s/%s%04d%02d%02d-%02d%02d%02d%s"
                    % (path, prefix,
                       rightNow.year, rightNow.month, rightNow.day,
                       rightNow.hour, rightNow.minute, rightNow.second,
                       imageFormat))
    return filename

#------------------------------------------------------------------------------
def takeTrackQuickPic(image, filename):
    """ Enlarge and Save stream image if motionTrackQuickPic=True"""
    big_image = cv2.resize(image, (bigImageWidth, bigImageHeight))
    cv2.imwrite(filename, big_image)
    logging.info("Saved %ix%i Image to %s",
                 bigImageWidth, bigImageHeight, filename)

#------------------------------------------------------------------------------
def showBox(filename):
    """
    Show stream image detection area on image to align camera
    This is a quick fix for restricting motion detection
    to a portion of the final image. Change the stream image size
    on line 206 and 207 above
    Adjust track config.py file motionTrackTrigLen as required.
    """
    working_image = cv2.imread(filename)
    x1y1 = (int((imageWidth - CAMERA_WIDTH)/2),
            int((imageHeight - CAMERA_HEIGHT)/2))
    x2y2 = (x1y1[0] + CAMERA_WIDTH,
            x1y1[1] + CAMERA_HEIGHT)
    cv2.rectangle(working_image, x1y1, x2y2, LINE_COLOR, LINE_THICKNESS)
    cv2.imwrite(filename, working_image)

#------------------------------------------------------------------------------
def takeDayImage(filename, cam_sleep_time):
    """ Take a Day image using exp=auto and awb=auto """
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight)
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.rotation = imageRotation # Valid values are 0, 90, 180, 270
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        time.sleep(cam_sleep_time) # use motion or TL camera sleep to get AWB
        if imagePreview:
            camera.start_preview()
        if imageFormat == ".jpg":   # Set quality if image is jpg
            camera.capture(filename, quality=imageJpegQuality)
        else:
            camera.capture(filename)
        camera.close()

    if imageShowStream:    # Show motion area on full image to align camera
        showBox(filename)

    logging.info("camSleepSec=%.2f exp=auto awb=auto Size=%ix%i ",
                 cam_sleep_time, imageWidth, imageHeight)
    # showDateOnImage displays FilePath so avoid showing twice
    if not showDateOnImage:
        logging.info("FilePath  %s", filename)

#------------------------------------------------------------------------------
def getShut(pxAve):
    """
    Calculate a shutter speed based on image pixel average
    """
    px = pxAve + 1  # avoid division by zero
    offset = nightMaxShut - ((nightMaxShut / float(nightDarkThreshold) * px))
    brightness = offset * (1/float(nightDarkAdjust))
    # hyperbolic curve + brightness adjust
    shut = (nightMaxShut * (1 / float(px))) + brightness
    return int(shut)

#------------------------------------------------------------------------------
def takeNightImage(filename, pixelAve):
    """ Take low light Twilight or Night image """
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight)
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.rotation = imageRotation # valid values are 0, 90, 180, 270
        time.sleep(1)
        # Use Twilight Threshold variable framerate_range
        if pixelAve >= nightDarkThreshold:
            camera.framerate_range = (Fraction(1, 6), Fraction(30, 1))
            time.sleep(1)
            camera.iso = nightMaxISO
            logging.info("%ix%i  TwilightThresh=%i/%i  MaxISO=%i uses framerate_range",
                         imageWidth, imageHeight,
                         pixelAve, nightTwilightThreshold,
                         nightMaxISO)
            time.sleep(4)
        else:
            # Set the framerate to a fixed value
            camera.framerate = Fraction(1, 6)
            time.sleep(1)
            camera.iso = nightMaxISO
            if pixelAve <= nightBlackThreshold:  # Black Threshold (very dark)
                camera.shutter_speed = nightMaxShut
                logging.info("%ix%i  BlackThresh=%i/%i shutSec=%s  MaxISO=%i  nightSleepSec=%i",
                             imageWidth, imageHeight,
                             pixelAve, nightBlackThreshold,
                             shut2Sec(nightMaxShut), nightMaxISO, nightSleepSec)
            else: # Dark Threshold (Between Twilight and Black)
                camShut = getShut(pixelAve)
                if camShut > nightMaxShut:
                    camShut = nightMaxShut
                # Set the shutter for long exposure
                camera.shutter_speed = camShut
                logging.info("%ix%i  DarkThresh=%i/%i  shutSec=%s  MaxISO=%i  nightSleepSec=%i",
                             imageWidth, imageHeight,
                             pixelAve, nightDarkThreshold,
                             shut2Sec(camShut), nightMaxISO, nightSleepSec)
            time.sleep(nightSleepSec)
            camera.exposure_mode = 'off'
        if imageFormat == ".jpg":
            camera.capture(filename, format='jpeg', quality=imageJpegQuality)
        else:
            camera.capture(filename)
        camera.close()

    if imageShowStream:    # Show motion area on full image to align camera
        showBox(filename)

    # showDateOnImage displays FilePath to avoid showing twice
    if not showDateOnImage:
        logging.info("FilePath %s", filename)

#------------------------------------------------------------------------------
def takeQuickTimeLapse(moPath, imagePrefix, NumOn, motionNumCount,
                       currentDayMode, NumPath):
    """ Take a quick timelapse sequence using yield if motion triggered """
    logging.info("Start Sequence for %i sec every %i sec",
                 motionQuickTLTimer, motionQuickTLInterval)
    checkTimeLapseTimer = datetime.datetime.now()
    keepTakingImages = True
    imgCnt = 0
    filename = getImageName(moPath, imagePrefix, NumOn, motionNumCount)
    while keepTakingImages:
        yield filename
        rightNow = datetime.datetime.now()
        timelapseDiff = (rightNow - checkTimeLapseTimer).total_seconds()
        motionNumCount = postImageProcessing(NumOn,
                                             motionNumStart,
                                             motionNumMax,
                                             motionNumCount,
                                             motionNumRecycle,
                                             NumPath, filename,
                                             currentDayMode)
        filename = getImageName(moPath, imagePrefix, NumOn, motionNumCount)
        if timelapseDiff > motionQuickTLTimer:
            keepTakingImages = False
        else:
            imgCnt += 1
            if motionRecentMax > 0:
                saveRecent(motionRecentMax,
                           motionRecentDir,
                           filename,
                           imagePrefix)
            time.sleep(motionQuickTLInterval)
    logging.info('End Sequence Total %i Images in %i seconds',
                 imgCnt, timelapseDiff)

#------------------------------------------------------------------------------
def takeVideo(filename, duration, fps=25):
    """ Take a short motion video if required """
    # Working folder for h264 videos
    h264_work = os.path.join(baseDir, "h264_work")
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
                 imageWidth, imageHeight, duration, fps)
    if motionVideoOn or videoRepeatOn:
        with picamera.PiCamera() as camera:
            camera.resolution = (imageWidth, imageHeight)
            camera.vflip = imageVFlip
            camera.hflip = imageHFlip
            # rotation can be used if camera is on side
            camera.rotation = imageRotation
            camera.framerate = fps
            if showDateOnImage:
                rightNow = datetime.datetime.now()
                dateTimeText = (" Started at %04d-%02d-%02d %02d:%02d:%02d "
                                % (rightNow.year,
                                   rightNow.month,
                                   rightNow.day,
                                   rightNow.hour,
                                   rightNow.minute,
                                   rightNow.second))
                camera.annotate_text_size = showTextFontSize
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
        if motionRecentMax > 0:
            saveRecent(motionRecentMax,
                       motionRecentDir,
                       filePathMP4,
                       motionPrefix)
        createSyncLockFile(filename)

#------------------------------------------------------------------------------
def createSyncLockFile(imagefilename):
    """
    If required create a lock file to indicate file(s) to process
    """
    if createLockFile:
        if not os.path.isfile(lockFilePath):
            open(lockFilePath, 'w').close()
            logging.info("Create Lock File %s", lockFilePath)
        rightNow = datetime.datetime.now()
        now = ("%04d%02d%02d-%02d%02d%02d"
               % (rightNow.year, rightNow.month, rightNow.day,
                  rightNow.hour, rightNow.minute, rightNow.second))
        filecontents = (now + " createSyncLockFile - " + imagefilename +
                        " Ready to sync using sudo ./sync.sh command.")
        f = open(lockFilePath, 'w+')
        f.write(filecontents)
        f.close()

#------------------------------------------------------------------------------
def trackPoint(grayimage1, grayimage2):
    """
    Process two cropped grayscale images.
    check for motion and return center point
    of motion for largest contour.
    """
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
def trackDistance(mPoint1, mPoint2):
    """
    Return the triangulated distance between two tracking locations
    """
    x1, y1 = mPoint1
    x2, y2 = mPoint2
    trackLen = abs(math.hypot(x2 - x1, y2 - y1))
    return trackLen

#------------------------------------------------------------------------------
def getStreamPixAve(streamData):
    """
    Calculate the average pixel values for the specified stream
    used for determining day/night or twilight conditions
    """
    pixAverage = int(np.average(streamData[..., 1]))
    return pixAverage

#------------------------------------------------------------------------------
def checkIfDayStream(currentDayMode, image):
    """ Try to determine if it is day, night or twilight."""
    dayPixAverage = 0
    dayPixAverage = getStreamPixAve(image)
    if dayPixAverage > nightTwilightThreshold:
        currentDayMode = True
    else:
        currentDayMode = False
    return currentDayMode

#------------------------------------------------------------------------------
def timeToSleep(currentDayMode):
    """
    Based on weather it is day or night (exclude twilight)
    return sleepMode boolean based on variable
    settings for noNightShots or noDayShots config.py variables
    Note if both are enabled then no shots will be taken.
    """
    if noNightShots:
        if currentDayMode:
            sleepMode = False
        else:
            sleepMode = True
    elif noDayShots:
        if currentDayMode:
            sleepMode = True
        else:
            sleepMode = False
    else:
        sleepMode = False
    return sleepMode

#------------------------------------------------------------------------------
def getSchedStart(dateToCheck):
    """
    This function will try to extract a valid date/time from a
    date time formatted string variable
    If date/time is past then try to extract time
    and schedule for current date at extracted time
    """
    goodDateTime = datetime.datetime.now()
    if len(dateToCheck) > 1:   # Check if timelapseStartAt is set
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
                    logging.warn("Resetting date/time to Now: %s",
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
    """
    Based on schedule date setting see if current
    datetime is past and return boolean
    to indicate processing can start for
    timelapse or motiontracking
    """
    startStatus = False
    if schedDate < datetime.datetime.now():
        startStatus = True  # sched date/time has passed so start sequence
    return startStatus

#------------------------------------------------------------------------------
def checkForTimelapse(timelapseStart):
    """ Check if timelapse timer has expired """
    rightNow = datetime.datetime.now()
    timeDiff = (rightNow - timelapseStart).total_seconds()
    if timeDiff > timelapseTimer:
        timelapseStart = rightNow
        timelapseFound = True
    else:
        timelapseFound = False
    return timelapseFound

#------------------------------------------------------------------------------
def timolo():
    """
    Main motion and or motion tracking
    initialization and logic loop
    """
    # Counter for showDots() display if not motion found
    # shows system is working
    dotCount = 0
    checkMediaPaths()
    timelapseNumCount = 0
    motionNumCount = 0
    tlstr = ""  # Used to display if timelapse is selected
    mostr = ""  # Used to display if motion is selected
    moCnt = "non"
    tlCnt = "non"
    daymode = False # Keep track of night and day based on dayPixAve
    # Forcing motion if no motion for motionForce time exceeded
    forceMotion = False
    motionFound = False
    takeTimeLapse = True
    stopTimeLapse = False
    takeMotion = True
    stopMotion = False
    firstTimeLapse = True
    timelapseStart = datetime.datetime.now()
    timelapseExitStart = timelapseStart
    checkMotionTimer = timelapseStart
    startTL = getSchedStart(timelapseStartAt)
    startMO = getSchedStart(motionStartAt)
    trackLen = 0.0
    if spaceTimerHrs > 0:
        lastSpaceCheck = datetime.datetime.now()
    if timelapseOn:
        tlstr = "TimeLapse"
        # Check if timelapse subDirs reqd and create one if non exists
        tlPath = subDirChecks(timelapseSubDirMaxHours,
                              timelapseSubDirMaxFiles,
                              timelapseDir, timelapsePrefix)
        if timelapseNumOn:
            timelapseNumCount = getCurrentCount(timelapseNumPath,
                                                timelapseNumStart)
            tlCnt = str(timelapseNumCount)
    else:
        logging.warn("Timelapse is Suppressed per timelapseOn=%s",
                     timelapseOn)
        stopTimeLapse = True
    logging.info("Start PiVideoStream ....")
    vs = PiVideoStream().start()
    vs.camera.rotation = imageRotation
    vs.camera.hflip = imageHFlip
    vs.camera.vflip = imageVFlip
    time.sleep(1)

    if motionTrackOn:
        mostr = "Motion Tracking"
        # Check if motion subDirs required and
        # create one if required and non exists
        moPath = subDirChecks(motionSubDirMaxHours,
                              motionSubDirMaxFiles,
                              motionDir,
                              motionPrefix)
        if motionNumOn:
            motionNumCount = getCurrentCount(motionNumPath, motionNumStart)
            moCnt = str(motionNumCount)
        trackTimeout = time.time()
        trackTimer = TRACK_TIMEOUT
        startPos = []
        startTrack = False
        image1 = vs.read()
        image2 = vs.read()
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    else:
        image2 = vs.read()  # use video stream to check for daymode
        logging.warn("Motion Tracking is Suppressed per motionTrackOn=%s",
                     motionTrackOn)
        stopMotion = True
    daymode = checkIfDayStream(daymode, image2)
    pixAve = getStreamPixAve(image2)
    if timelapseOn and motionTrackOn:
        tlstr = " and " + tlstr
    displayInfo(moCnt, tlCnt)  # Display config.py settings
    if logDataToFile:
        logging.info("logDataToFile=%s Logging to Console Disabled.",
                     logDataToFile)
        logging.info("Sending Console Messages to %s", logFilePath)
        logging.info("Entering Loop for %s%s", mostr, tlstr)
    else:
        if pluginEnable:
            logging.info("plugin %s - Start %s%s Loop ...",
                         pluginName, mostr, tlstr)
        else:
            logging.info("Start %s%s Loop ... ctrl-c Exits", mostr, tlstr)
    if motionTrackOn and not checkSchedStart(startMO):
        logging.info('Motion Track: motionStartAt = "%s"', motionStartAt)
        logging.info("Motion Track: Sched Start Set For %s  Please Wait ...",
                     startMO)
    if timelapseOn and not checkSchedStart(startTL):
        logging.info('Timelapse   : timelapseStartAt = "%s"', timelapseStartAt)
        logging.info("Timelapee   : Sched Start Set For %s  Please Wait ...",
                     startTL)
    logging.info("daymode=%s  motionDotsOn=%s ", daymode, motionDotsOn)
    dotCount = showDots(motionDotsMax)  # reset motion dots
    while True:  # Start main program Loop.
        motionFound = False
        forceMotion = False
        if (motionTrackOn and (not motionNumRecycle)
                and (motionNumCount > motionNumStart + motionNumMax)
                and (not stopMotion)):
            logging.warning("motionNumRecycle=%s and motionNumCount %i Exceeds %i",
                            motionNumRecycle, motionNumCount,
                            motionNumStart + motionNumMax)
            logging.warn("Suppressing Further Motion Tracking")
            logging.warn("To Reset: Change %s Settings or Archive Images",
                         configName)
            logging.warn("Then Delete %s and Restart %s \n",
                         motionNumPath, progName)
            takeMotion = False
            stopMotion = True
        if stopTimeLapse and stopMotion:
            logging.warn("NOTICE: Both Motion and Timelapse Disabled")
            logging.warn("per Num Recycle=False and "
                         "Max Counter Reached or timelapseExitSec Settings")
            logging.warn("Change %s Settings or Archive/Save Media Then",
                         configName)
            logging.warn("Delete appropriate .dat File(s) to Reset Counter(s)")
            logging.warn("Exiting %s %s \n", progName, progVer)
            sys.exit(1)
        # if required check free disk space and delete older files (jpg)
        if spaceTimerHrs > 0:
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
        # use image2 to check daymode as image1 may be average
        # that changes slowly, and image1 may not be updated
        if motionTrackOn:
            if daymode != checkIfDayStream(daymode, image2):
                daymode = not daymode
                image2 = vs.read()
                image1 = image2
            else:
                image2 = vs.read()
        else:
            image2 = vs.read()
            # if daymode has changed, reset background
            # to avoid false motion trigger
            if daymode != checkIfDayStream(daymode, image2):
                daymode = not daymode
        pixAve = getStreamPixAve(image2)
        rightNow = datetime.datetime.now() # refresh rightNow time
        if not timeToSleep(daymode):
            # Don't take images if noNightShots
            # or noDayShots settings are valid
            if timelapseOn and checkSchedStart(startTL):
               # Check for a scheduled date/time to start timelapse
                if firstTimeLapse:
                    firstTimeLapse = False
                    takeTimeLapse = True
                else:
                    takeTimeLapse = checkForTimelapse(timelapseStart)
                if ((not stopTimeLapse) and takeTimeLapse and
                        timelapseExitSec > 0):
                    if ((datetime.datetime.now() -
                         timelapseExitStart).total_seconds() >
                            timelapseExitSec):
                        logging.info("timelapseExitSec=%i Exceeded.",
                                     timelapseExitSec)
                        logging.info("Suppressing Further Timelapse Images")
                        logging.info("To RESET: Restart %s to Restart "
                                     "timelapseExitSec Timer. \n", progName)
                        # Suppress further timelapse images
                        takeTimeLapse = False
                        stopTimeLapse = True
                if ((not stopTimeLapse) and timelapseNumOn
                        and (not timelapseNumRecycle)):
                    if (timelapseNumMax > 0 and
                            timelapseNumCount > (timelapseNumStart + timelapseNumMax)):
                        logging.warn("timelapseNumRecycle=%s and Counter=%i Exceeds %i",
                                     timelapseNumRecycle, timelapseNumCount,
                                     timelapseNumStart + timelapseNumMax)
                        logging.warn("Suppressing Further Timelapse Images")
                        logging.warn("To RESET: Change %s Settings or Archive Images",
                                     configName)
                        logging.warn("Then Delete %s and Restart %s \n",
                                     timelapseNumPath, progName)
                        # Suppress further timelapse images
                        takeTimeLapse = False
                        stopTimeLapse = True
                if takeTimeLapse and (not stopTimeLapse):
                    if motionDotsOn and motionTrackOn:
                        # reset motion dots
                        dotCount = showDots(motionDotsMax + 2)
                    else:
                        print("")
                    if pluginEnable:
                        if timelapseExitSec > 0:
                            exitSecProgress = (datetime.datetime.now() -
                                               timelapseExitStart).total_seconds()
                            logging.info("%s Sched TimeLapse  daymode=%s  Timer=%i sec"
                                         "  ExitSec=%i/%i Status",
                                         pluginName, daymode, timelapseTimer,
                                         exitSecProgress, timelapseExitSec)
                        else:
                            logging.info("%s Sched TimeLapse  daymode=%s"
                                         "  Timer=%i sec  ExitSec=%i 0=Continuous",
                                         pluginName, daymode,
                                         timelapseTimer, timelapseExitSec)
                    else:
                        if timelapseExitSec > 0:
                            exitSecProgress = (datetime.datetime.now() -
                                               timelapseExitStart).total_seconds()
                            logging.info("Sched TimeLapse  daymode=%s  Timer=%i sec"
                                         "  ExitSec=%i/%i Status",
                                         daymode, timelapseTimer,
                                         exitSecProgress, timelapseExitSec)
                        else:
                            logging.info("Sched TimeLapse  daymode=%s  Timer=%i sec"
                                         "  ExitSec=%i 0=Continuous",
                                         daymode, timelapseTimer,
                                         timelapseExitSec)
                    imagePrefix = timelapsePrefix + imageNamePrefix
                    filename = getImageName(tlPath, imagePrefix,
                                            timelapseNumOn, timelapseNumCount)
                    logging.info("Stop PiVideoStream ...")
                    vs.stop()
                    time.sleep(motionStreamStopSec)
                    # reset time lapse timer
                    timelapseStart = datetime.datetime.now()
                    if daymode:
                        takeDayImage(filename, timelapseCamSleep)
                    else:
                        takeNightImage(filename, pixAve)
                    timelapseNumCount = postImageProcessing(timelapseNumOn,
                                                            timelapseNumStart,
                                                            timelapseNumMax,
                                                            timelapseNumCount,
                                                            timelapseNumRecycle,
                                                            timelapseNumPath,
                                                            filename, daymode)
                    if timelapseRecentMax > 0:
                        saveRecent(timelapseRecentMax, timelapseRecentDir,
                                   filename, imagePrefix)
                    if timelapseMaxFiles > 0:
                        deleteOldFiles(timelapseMaxFiles, timelapseDir,
                                       imagePrefix)
                    dotCount = showDots(motionDotsMax)
                    logging.info("Restart PiVideoStream ....")
                    vs = PiVideoStream().start()
                    vs.camera.rotation = imageRotation
                    vs.camera.hflip = imageHFlip
                    vs.camera.vflip = imageVFlip
                    time.sleep(1)
                    tlPath = subDirChecks(timelapseSubDirMaxHours,
                                          timelapseSubDirMaxFiles,
                                          timelapseDir, timelapsePrefix)
            if motionTrackOn and checkSchedStart(startMO) and takeMotion and (not stopMotion):
                # IMPORTANT - Night motion tracking may not work very well
                #             due to long exposure times and low light
                image2 = vs.read()
                grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
                movePoint1 = trackPoint(grayimage1, grayimage2)
                grayimage1 = grayimage2
                if movePoint1 and not startTrack:
                    startTrack = True
                    trackTimeout = time.time()
                    startPos = movePoint1
                image2 = vs.read()
                grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
                movePoint2 = trackPoint(grayimage1, grayimage2)
                if movePoint2 and startTrack:   # Two sets of movement required
                    trackLen = trackDistance(startPos, movePoint2)
                    # wait until track well started
                    if trackLen > TRACK_TRIG_LEN_MIN:
                        # Reset tracking timer object moved
                        trackTimeout = time.time()
                        if motionTrackInfo:
                            logging.info("Track Progress From(%i,%i) To(%i,%i) trackLen=%i/%i px",
                                         startPos[0], startPos[1],
                                         movePoint2[0], movePoint2[1],
                                         trackLen, TRACK_TRIG_LEN)
                    # Track length triggered
                    if trackLen > TRACK_TRIG_LEN:
                        # reduce chance of two objects at different positions
                        if trackLen > TRACK_TRIG_LEN_MAX:
                            motionFound = False
                            if motionTrackInfo:
                                logging.info("TrackLen %i px Exceeded %i px Max Trig Len Allowed.",
                                             trackLen, TRACK_TRIG_LEN_MAX)
                        else:
                            motionFound = True
                            if pluginEnable:
                                logging.info("%s Motion Triggered Start(%i,%i)"
                                             "  End(%i,%i) trackLen=%.i/%i px",
                                             pluginName, startPos[0], startPos[1],
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
                    if motionTrackInfo:
                        logging.info("Track Timer %.2f sec Exceeded. Reset Track",
                                     trackTimer)
                    startTrack = False
                    startPos = []
                    trackLen = 0.0
                rightNow = datetime.datetime.now()
                timeDiff = (rightNow - checkMotionTimer).total_seconds()
                if motionForce > 0 and timeDiff > motionForce:
                    image1 = vs.read()
                    image2 = image1
                    grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                    grayimage2 = grayimage1
                    dotCount = showDots(motionDotsMax + 2) # New Line
                    logging.info("No Motion Detected for %s minutes. "
                                 "Taking Forced Motion Image.",
                                 (motionForce / 60))
                    checkMotionTimer = rightNow
                    forceMotion = True
                if motionFound or forceMotion:
                    imagePrefix = motionPrefix + imageNamePrefix
                    if motionTrackQuickPic:  # Do not stop PiVideoStream
                        filename = getImageName(moPath,
                                                imagePrefix,
                                                motionNumOn,
                                                motionNumCount)
                        takeTrackQuickPic(image2, filename)
                        motionNumCount = postImageProcessing(motionNumOn,
                                                             motionNumStart,
                                                             motionNumMax,
                                                             motionNumCount,
                                                             motionNumRecycle,
                                                             motionNumPath,
                                                             filename, daymode)
                    else:
                        if motionTrackOn:
                            logging.info("Stop PiVideoStream ...")
                            vs.stop()
                            time.sleep(motionStreamStopSec)
                        checkMotionTimer = rightNow
                        if forceMotion:
                            forceMotion = False
                        # check if motion Quick Time Lapse option is On.
                        # This option supersedes motionVideoOn
                        if motionQuickTLOn and daymode:
                            filename = getImageName(moPath,
                                                    imagePrefix,
                                                    motionNumOn,
                                                    motionNumCount)
                            with picamera.PiCamera() as camera:
                                camera.resolution = (imageWidth, imageHeight)
                                camera.vflip = imageVFlip
                                camera.hflip = imageHFlip
                                # valid rotation values 0, 90, 180, 270
                                camera.rotation = imageRotation
                                time.sleep(motionCamSleep)
                                # This uses yield to loop through time lapse
                                # sequence but does not seem to be faster
                                # due to writing images
                                camera.capture_sequence(takeQuickTimeLapse(moPath,
                                                                           imagePrefix,
                                                                           motionNumOn,
                                                                           motionNumCount,
                                                                           daymode,
                                                                           motionNumPath))
                                camera.close()
                                motionNumCount = getCurrentCount(motionNumPath,
                                                                 motionNumStart)
                        else:
                            if motionVideoOn:
                                filename = getVideoName(motionPath,
                                                        imagePrefix,
                                                        motionNumOn,
                                                        motionNumCount)
                                takeVideo(filename, motionVideoTimer,
                                          motionVideoFPS)
                            else:
                                filename = getImageName(moPath,
                                                        imagePrefix,
                                                        motionNumOn,
                                                        motionNumCount)
                                if daymode:
                                    takeDayImage(filename, motionCamSleep)
                                else:
                                    takeNightImage(filename, pixAve)
                            motionNumCount = postImageProcessing(motionNumOn,
                                                                 motionNumStart,
                                                                 motionNumMax,
                                                                 motionNumCount,
                                                                 motionNumRecycle,
                                                                 motionNumPath,
                                                                 filename,
                                                                 daymode)
                            if motionRecentMax > 0:
                                if not motionVideoOn:
                                   # prevent h264 video files from
                                   # being copied to recent
                                    saveRecent(motionRecentMax,
                                               motionRecentDir,
                                               filename,
                                               imagePrefix)
                        if motionTrackOn:
                            logging.info("Restart PiVideoStream ....")
                            vs = PiVideoStream().start()
                            vs.camera.rotation = imageRotation
                            vs.camera.hflip = imageHFlip
                            vs.camera.vflip = imageVFlip
                            time.sleep(1)
                            image1 = vs.read()
                            image2 = image1
                            grayimage1 = cv2.cvtColor(image1,
                                                      cv2.COLOR_BGR2GRAY)
                            grayimage2 = grayimage1
                            trackLen = 0.0
                            trackTimeout = time.time()
                            startPos = []
                            startTrack = False
                            forceMotion = False
                    moPath = subDirChecks(motionSubDirMaxHours,
                                          motionSubDirMaxFiles,
                                          motionDir, motionPrefix)
                    if motionFound:
                        # ===========================================
                        # Put your user code in userMotionCodeHere()
                        # function at top of this script
                        # ===========================================
                        userMotionCodeHere()
                        dotCount = showDots(motionDotsMax)
                else:
                    # show progress dots when no motion found
                    dotCount = showDots(dotCount)

#------------------------------------------------------------------------------
def videoRepeat():
    """
    This is a special dash cam video mode
    that overrides both timelapse and motion tracking settings
    It has it's own set of settings to manage start, video duration,
    number recycle mode, Etc.
    """
    # Check if folder exist and create if required
    if not os.path.isdir(videoPath):
        logging.info("Create videoRepeat Folder %s", videoPath)
        os.makedirs(videoPath)
    print("--------------------------------------------------------------------")
    print("VideoRepeat . videoRepeatOn=%s" % videoRepeatOn)
    print("   Info ..... Size=%ix%i  videoPrefix=%s  videoDuration=%i seconds  videoFPS=%i"
          % (imageWidth, imageHeight, videoPrefix, videoDuration, videoFPS))
    print("   Vid Path . videoPath=%s" % videoPath)
    print("   Sched .... videoStartAt=%s blank=Off or Set Valid Date and/or Time to Start Sequence"
          % videoStartAt)
    print("   Timer .... videoTimer=%i minutes  0=Continuous" % videoTimer)
    print("   Num Seq .. videoNumOn=%s  videoNumRecycle=%s  videoNumStart=%i"
          "  videoNumMax=%i 0=Continuous"
          % (videoNumOn, videoNumRecycle, videoNumStart, videoNumMax))
    print("--------------------------------------------------------------------")
    print("WARNING: videoRepeatOn=%s Suppresses TimeLapse and Motion Settings."
          % videoRepeatOn)
    startVideoRepeat = getSchedStart(videoStartAt)
    if not checkSchedStart(startVideoRepeat):
        logging.info('Video Repeat: videoStartAt = "%s" ', videoStartAt)
        logging.info("Video Repeat: Sched Start Set For %s  Please Wait ...",
                     startVideoRepeat)
        while not checkSchedStart(startVideoRepeat):
            pass
    videoStartTime = datetime.datetime.now()
    lastSpaceCheck = datetime.datetime.now()
    videoCount = 0
    videoNumCounter = videoNumStart
    keepRecording = True
    while keepRecording:
        # if required check free disk space and delete older files
        # Set variables spaceFileExt='mp4' and
        # spaceMediaDir= to appropriate folder path
        if spaceTimerHrs > 0:
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
        filename = getVideoName(videoPath, videoPrefix,
                                videoNumOn, videoNumCounter)
        takeVideo(filename, videoDuration, videoFPS)
        timeUsed = (datetime.datetime.now() - videoStartTime).total_seconds()
        timeRemaining = (videoTimer*60 - timeUsed) / 60.0
        videoCount += 1
        if videoNumOn:
            videoNumCounter += 1
            if videoNumMax > 0:
                if videoNumCounter - videoNumStart > videoNumMax:
                    if videoNumRecycle:
                        videoNumCounter = videoNumStart
                        logging.info("Restart Numbering: videoNumRecycle=%s "
                                     "and videoNumMax=%i Exceeded",
                                     videoNumRecycle, videoNumMax)
                    else:
                        keepRecording = False
                        logging.info("Exit since videoNumRecycle=%s "
                                     "and videoNumMax=%i Exceeded  %i Videos Recorded",
                                     videoNumRecycle, videoNumMax, videoCount)
                logging.info("Recorded %i of %i Videos",
                             videoCount, videoNumMax)
            else:
                logging.info("Recorded %i Videos  videoNumMax=%i 0=Continuous",
                             videoCount, videoNumMax)
        else:
            logging.info("Progress: %i Videos Recorded in Folder %s",
                         videoCount, videoPath)
        if videoTimer > 0:
            if timeUsed > videoTimer * 60:
                keepRecording = False
                errorText = ("Stop Recording Since videoTimer=%i minutes Exceeded \n",
                             videoTimer)
                logging.warn(errorText)
                sys.stdout.write(errorText)
            else:
                logging.info("Remaining Time %.1f of %i minutes",
                             timeRemaining, videoTimer)
        else:
            videoStartTime = datetime.datetime.now()
    logging.info("Exit: %i Videos Recorded in Folder %s",
                 videoCount, videoPath)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    """ Initialization prior to launching appropriate pi-timolo options """
    logging.info("Testing if Pi Camera is in Use")
    # Test if the pi camera is already in use
    ts = PiVideoStream().start()
    time.sleep(1)
    ts.stop()
    time.sleep(motionStreamStopSec)
    logging.info("Pi Camera is Available.")
    if pluginEnable:
        logging.info("Start pi-timolo per %s and plugins/%s.py Settings",
                     configFilePath, pluginName)
    else:
        logging.info("Start pi-timolo per %s Settings", configFilePath)
    if not verbose:
        print("NOTICE: Logging Disabled per variable verbose=False  ctrl-c Exits")
    try:
        if videoRepeatOn:
            videoRepeat()
        else:
            timolo()
    except KeyboardInterrupt:
        print("")
        if verbose:
            logging.info("User Pressed Keyboard ctrl-c")
            logging.info("Exiting %s %s", progName, progVer)
        else:
            sys.stdout.write("User Pressed Keyboard ctrl-c \n")
            sys.stdout.write("Exiting %s %s \n" % (progName, progVer))
    try:
        if pluginEnable:
            if os.path.isfile(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.isfile(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
    except OSError as err:
        logging.warn("Failed To Remove File %s - %s", pluginCurrentpyc, err)
        sys.exit(1)
