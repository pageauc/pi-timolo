#!/usr/bin/python

# pi-timolo - Raspberry Pi Long Duration Timelapse, Motion Detection, with Low Light Capability
# written by Claude Pageau Dec-2014 (original issue)
# getStreamImage function based on utpalc code based on brainflakes lightweight motion detection code on Raspberry PI forum - Thanks
# Complete pi-timolo code and wiki instructions are available on my github repo at https://github.com/pageauc/pi-timolo

# 2.7 released 20-Jul-2015  added saving of exif metadata when text written to image sinc PIL does not retain this.
# 2.8 released 2-Aug-2015 updated gdrive and replaced mencoder with avconv
# 2.92 release 22-Mar-2016 fixed getCurrentCount when file contains non integer data due to a write error or corruption.
# 2.93 release 21-Jul-2016 improved getCurrentCount logic and changed default motion image size to 128x80 per picamra default
# 2.94 release 14-Aug-2016 implemented camera.rotation = cameraRotate but not yet fully tested
# 2.95 release 20-Dec-2016 Updated logging to be more pythonic and minor bug fix
# 2.96 release 26-Dec-2016 Fixed fatal bug error in logging when verbose = False 
# 2.97 release 28-Dec-2016 Modified logging setup to simplify and better display messages
# 2.98 release 04-Jan-2017 Added convid.sh and associated changes.  Added flip to video option 
# 2.99 release 06-Jan-2017 Added sync_lock option to motion video
# 3.00 release 09-Jan-2017 Added takeVideo subprocess to convert h264
# 3.10 release 12-Jan-2017 Added takeVideo annotate datetime text using image text settings on and size.
# 4.00 release 23-Jan-2017 Added menubox.sh and sh config vars stored in conf files so upgrades won't delete settings  
# 4.10 release 09-Mar-2017 Moved position of camera.exposure_mode = 'off' for night shots
# 4.20 release 13-Mar-2017 Updated takeNightImage settings

progVer = "ver 4.20"

import datetime
import glob
import logging
import os
import sys
import time
import subprocess

mypath = os.path.abspath(__file__)  # Find the full path of this python script
baseDir = os.path.dirname(mypath)  # get the path location only (excluding script name)
baseFileName = os.path.splitext(os.path.basename(mypath))[0]
progName = os.path.basename(__file__)
logFilePath = os.path.join(baseDir, baseFileName + ".log")
print("----------------------------------------------------------------------------------------------")
print("%s %s" %( progName, progVer ))

# Check for variable file to import and error out if not found.
configFilePath = os.path.join(baseDir, "config.py")
if not os.path.exists(configFilePath):
    print("ERROR - Cannot Import Configuration Variables. Missing Configuration File %s" % ( configFilePath ))
    quit()
else:
    # Read Configuration variables from config.py file
    print("Importing Configuration Variables from File %s" % ( configFilePath ))    
    from config import *
  
# Now that variable are imported from config.py Setup Logging 
if logDataToFile:
    print("Sending Logging Data to %s  (Console Messages Disabled)" %( logFilePath ))
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=logFilePath,
                    filemode='w')   
elif verbose:
    print("Logging to Console per Variable verbose=True")    
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
else:
    print("Logging Disabled per Variable verbose=False")
    logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

print("Loading Python Libraries ...")                   
# import remaining python libraries  
import picamera
import picamera.array
import numpy as np
import pyexiv2
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from fractions import Fraction
  
#==================================
#      System Variables
# Should not need to be customized
#==================================

SECONDS2MICRO = 1000000    # Used to convert from seconds to microseconds
nightMaxShut = int(nightMaxShut * SECONDS2MICRO)  # default=5 sec IMPORTANT- 6 sec works sometimes but occasionally locks RPI and HARD reboot required to clear
nightMinShut = int(nightMinShut * SECONDS2MICRO)  # lowest shut camera setting for transition from day to night (or visa versa)
testWidth = 128            # width of rgb image stream used for motion detection and day/night changes
testHeight = 80            # height of rgb image stream used for motion detection and day/night changes
daymode = False            # default should always be False.
motionPath = os.path.join(baseDir, motionDir)  # Store Motion images
motionNumPath = os.path.join(baseDir, motionPrefix + baseFileName + ".dat")  # dat file to save currentCount
timelapsePath = os.path.join(baseDir, timelapseDir)  # Store Time Lapse images
timelapseNumPath = os.path.join(baseDir, timelapsePrefix + baseFileName + ".dat")  # dat file to save currentCount
lockFilePath = os.path.join(baseDir, baseFileName + ".sync")

#-----------------------------------------------------------------------------------------------
def userMotionCodeHere():
    # Users can put code here that needs to be run prior to taking motion capture images
    # Eg Notify or activate something.

    # User code goes here

    return

#-----------------------------------------------------------------------------------------------
def shut2Sec (shutspeed):
    shutspeedSec = shutspeed/float(SECONDS2MICRO)
    shutstring = str("%.3f sec") % ( shutspeedSec )
    return shutstring

#-----------------------------------------------------------------------------------------------    
def showTime():
    rightNow = datetime.datetime.now()
    currentTime = "%04d-%02d-%02d %02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return currentTime

#-----------------------------------------------------------------------------------------------
def showDots(dotcnt):
    if motionOn and verbose:
        dotcnt += 1
        if dotcnt > motionMaxDots + 2:
            print("")
            dotcnt = 0
        elif dotcnt > motionMaxDots:
            print("")
            stime = showTime() + " ."
            sys.stdout.write(stime) 
            sys.stdout.flush()
            dotcnt = 0
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
    return dotcnt

#-----------------------------------------------------------------------------------------------    
def checkConfig():
    if not motionOn and not timelapseOn:
        logging.warning("Both Motion and Timelapse are turned OFF - motionOn=%s timelapseOn=%s", motionOn, timelapseOn)
    return

#-----------------------------------------------------------------------------------------------   
def takeTestImage():
    # Check if any parameter was passed to this script from the command line.
    # This is useful for taking a single image for aligning camera without editing script settings.
    mytime=showTime()
    testfilename = "takeTestImage.jpg"
    testfilepath = os.path.join(baseDir, testfilename)
    takeDayImage(testfilepath)    
    imagetext = "%s %s" % (mytime, testfilename)
    writeTextToImage(testfilepath, imagetext, daymode)
    logging.info("imageTestPrint=%s Captured Test Image to %s " % (imageTestPrint, testfilepath))
    sys.exit(2)
    return

#-----------------------------------------------------------------------------------------------
def displayInfo(motioncount, timelapsecount):
    if verbose:  
        print("-------------------------------------- Settings ----------------------------------------------")
        print("Config File .. Title=%s" % configTitle)
        print("               config-template filename=%s" % configName)
        print("Image Info ... Size=%ix%i   Prefix=%s   VFlip=%s   HFlip=%s   Preview=%s" % (imageWidth, imageHeight, imageNamePrefix, imageVFlip, imageHFlip, imagePreview))
        shutStr = shut2Sec(nightMaxShut)
        print("    Low Light. twilightThreshold=%i  nightMaxShut=%s  nightMaxISO=%i   nightSleepSec=%i sec" % (twilightThreshold, shutStr, nightMaxISO, nightSleepSec))
        print("    No Shots . noNightShots=%s   noDayShots=%s" % (noNightShots, noDayShots))
        if showDateOnImage:
            print("    Img Text . On=%s  Bottom=%s (False=Top)  WhiteText=%s (False=Black)  showTextWhiteNight=%s" % (showDateOnImage, showTextBottom, showTextWhite, showTextWhiteNight)) 
            print("               showTextFontSize=%i px height" % (showTextFontSize))
        else:
            print("    No Text .. showDateOnImage=%s  Text on Image Disabled"  % (showDateOnImage))
        print("Motion ....... On=%s  Prefix=%s  threshold=%i(How Much)  sensitivity=%i(How Many)"  % (motionOn, motionPrefix, threshold, sensitivity))
        print("               forceTimer=%i min(If No Motion)"  % (motionForce/60))
        print("               Number of previous images to use to check for motion=%i"  % (motionAverage))
        print("               Use video port for motion image capture? %s"  % (useVideoPort))
        print("               motionPath=%s" % (motionPath))
        if motionNumOn:
            print("    Num Seq .. motionNumOn=%s  current=%s   numStart=%i   numMax=%i   numRecycle=%s"  % (motionNumOn, motioncount, motionNumStart, motionNumMax, motionNumRecycle))
            print("               motionNumPath=%s " % (motionNumPath))
        else:
            print("    Date-Time. motionNumOn=%s  Image Numbering Disabled" % (motionNumOn))
        if motionQuickTLOn:
            print("    Quick TL . motionQuickTLOn=%s   motionQuickTLTimer=%i sec  motionQuickTLInterval=%i sec (0=fastest)" % (motionQuickTLOn, motionQuickTLTimer, motionQuickTLInterval))
        else:
            print("    Quick TL . motionQuickTLOn=%s  Quick Time Lapse Disabled" % (motionQuickTLOn))
        if motionVideoOn:
            print("    Video .... motionVideoOn=%s   motionVideoTimer=%i sec   (superseded by QuickTL)" % (motionVideoOn, motionVideoTimer))
        else:
            print("    Video .... motionVideoOn=%s  Motion Video Disabled" % (motionVideoOn))
        print("Time Lapse ... On=%s  Prefix=%s   Timer=%i sec   timeLapseExit=%i sec (0=Continuous)" % (timelapseOn, timelapsePrefix, timelapseTimer, timelapseExit)) 
        print("               timelapsePath=%s" % (timelapsePath))
        if timelapseNumOn:
            print("    Num Seq .. On=%s  current=%s   numStart=%i   numMax=%i   numRecycle=%s"  % (timelapseNumOn, timelapsecount, timelapseNumStart, timelapseNumMax, timelapseNumRecycle))
            print("               numPath=%s" % (timelapseNumPath))
        else:
            print("    Date-Time. motionNumOn=%s  Numbering Disabled" % (timelapseNumOn))
        if createLockFile:
            print("gdrive Sync .. On=%s  Path=%s  Note: syncs for motion images only." % (createLockFile, lockFilePath))  
        print("Logging ...... verbose=%s (True = Log To Console)" % ( verbose ))
        print("               logDataToFile=%s  logFilePath=%s" % ( logDataToFile, logFilePath ))
        print("------------------------------------ Log Activity --------------------------------------------")
    checkConfig()
    return

#-----------------------------------------------------------------------------------------------    
def checkImagePath():
    # Checks for image folders and creates them if they do not already exist.
    if motionOn:
        if not os.path.isdir(motionPath):
            logging.info("Creating Image Motion Detection Storage Folder %s", motionPath)
            os.makedirs(motionPath)
    if timelapseOn:
        if not os.path.isdir(timelapsePath):
            logging.info("Creating Time Lapse Image Storage Folder %s", timelapsePath)
            os.makedirs(timelapsePath)
    return

#-----------------------------------------------------------------------------------------------    
def getCurrentCount(numberpath, numberstart):
    # Create a .dat file to store currentCount or read file if it already Exists
    # Create numberPath file if it does not exist
    if not os.path.exists(numberpath):
        logging.info("Creating New File %s numberstart= %s", numberpath, numberstart)
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
        except ValueError:   # Found Corrupt dat file since cannot convert to integer
            # Try to determine if this is motion or timelapse
            if numberpath.find(motionPrefix) > 0:
                filePath = motionPath + "/*.jpg"
                fprefix = motionPath + motionPrefix + imageNamePrefix
            else:
                filePath = timelapsePath + "/*.jpg"
                fprefix = timelapsePath + timelapsePrefix + imageNamePrefix
            try:
               # Scan image folder for most recent file and try to extract numbercounter
                newest = max(glob.iglob(filePath), key=os.path.getctime)
                writeCount = newest[len(fprefix)+1:newest.find(".jpg")]
            except:
                writeCount = numberstart
            try:
                numbercounter = int(writeCount)+1
            except ValueError:
                numbercounter = numberstart
            logging.error("Invalid Data in File %s Reset numbercounter to %s", numberpath, numbercounter)

        f = open(numberpath, 'w+')
        f.write(str(numbercounter))
        f.close()
        f = open(numberpath, 'r')
        writeCount = f.read()
        f.closed
        numbercounter = int(writeCount)
    return numbercounter

#-----------------------------------------------------------------------------------------------
def writeTextToImage(imagename, datetoprint, daymode):
    # function to write date/time stamp directly on top or bottom of images.
    if showTextWhite:
        FOREGROUND = ( 255, 255, 255 )  # rgb settings for white text foreground
        textColour = "White"
    else:
        FOREGROUND = ( 0, 0, 0 )  # rgb settings for black text foreground
        textColour = "Black"
        if showTextWhiteNight and ( not daymode):
            FOREGROUND = ( 255, 255, 255 )  # rgb settings for black text foreground
            textColour = "White"
    # centre text and compensate for graphics text being wider
    x = int((imageWidth/2) - (len(imagename)*2))
    if showTextBottom:
        y = (imageHeight - 50)  # show text at bottom of image 
    else:
        y = 10  # show text at top of image
    TEXT = imageNamePrefix + datetoprint
    font_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
    font = ImageFont.truetype(font_path, showTextFontSize, encoding='unic')
    text = TEXT.decode('utf-8')

    # Read exif data since ImageDraw does not save this metadata
    img = Image.open(imagename)
    metadata = pyexiv2.ImageMetadata(imagename) 
    metadata.read()
    
    draw = ImageDraw.Draw(img)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text(( x, y ), text, FOREGROUND, font=font)
    img.save(imagename)
    metadata.write()    # Write previously saved exif data to image file
    logging.info("Added %s Text[%s] on %s", textColour, datetoprint, imagename)
    return

#----------------------------------------------------------------------------------------------- 
def postImageProcessing(numberon, counterstart, countermax, counter, recycle, counterpath, filename, daymode):
    # If required process text to display directly on image
    if (not motionVideoOn):
        rightNow = datetime.datetime.now()
        if showDateOnImage:
            dateTimeText = "%04d%02d%02d_%02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
            if numberon:
                counterStr = "%i    "  % ( counter )
                imageText =  counterStr + dateTimeText
            else:
                imageText = dateTimeText
            # Now put the imageText on the current image
            writeTextToImage(filename, imageText, daymode)
        if createLockFile and motionOn:
            createSyncLockFile(filename)
    # Process currentCount for next image if number sequence is enabled
    if numberon:
        counter += 1
        if countermax > 0:
            if (counter > counterstart + countermax):
                if recycle:
                    counter = counterstart
                else:
                    print("%s - Exceeded Image Count numberMax=%i" % ( progName, countermax ))
                    print("Exiting %s" % progName)
                    sys.exit(2)              
        # write next image counter number to dat file
        currentTime = showTime()        
        writeCount = str(counter)
        if not os.path.exists(counterpath):
            logging.info("Create New Counter File writeCount=%s %s", writeCount, counterpath)
            open(counterpath, 'w').close()
        f = open(counterpath, 'w+')
        f.write(str(writeCount))
        f.close()
        logging.info("Next Counter=%s %s", writeCount, counterpath)
    return counter

#-----------------------------------------------------------------------------------------------    
def getVideoName(path, prefix, numberon, counter):
    # build image file names by number sequence or date/time
    if numberon:
        if motionVideoOn:
            filename = os.path.join(path, prefix + str(counter) + ".h264")
    else:
        if motionVideoOn:
            rightNow = datetime.datetime.now()
            filename = "%s/%s%04d%02d%02d-%02d%02d%02d.h264" % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return filename

#-----------------------------------------------------------------------------------------------
def getImageName(path, prefix, numberon, counter):
    # build image file names by number sequence or date/time
    if numberon:
        filename = os.path.join(path, prefix + str(counter) + ".jpg")   
    else:
        rightNow = datetime.datetime.now()
        filename = "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)     
    return filename

#-----------------------------------------------------------------------------------------------
def takeDayImage(filename):
    # Take a Day image using exp=auto and awb=auto
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight) 
        time.sleep(0.5)   # sleep for a little while so camera can get adjustments
        if imagePreview:
            camera.start_preview()
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.rotation = imageRotation #Note use imageVFlip and imageHFlip variables
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        time.sleep(2)   # sleep for a little while to messure AWB
        camera.capture(filename, use_video_port=useVideoPort)
    logging.info("Size=%ix%i exp=auto awb=auto %s" % (imageWidth, imageHeight, filename))
    return

#-----------------------------------------------------------------------------------------------   
def takeNightImage(filename):
    dayStream = getStreamImage(True)
    dayPixAve = getStreamPixAve(dayStream)
    currentShut, currentISO = getNightCamSettings(dayPixAve)
    # Take low light Night image (including twilight zones)
    with picamera.PiCamera() as camera:
        # Take Low Light image
        # Set a framerate_range then set shutter
        camera.resolution = (imageWidth, imageHeight)
        camera.framerate_range = (Fraction(1, 6), Fraction(30, 1))
        camera.sensor_mode = 3
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.rotation = imageRotation #Note use imageVFlip and imageHFlip variables
        camera.shutter_speed = currentShut
        camera.iso = currentISO
        # Give the camera a good long time to measure AWB
        time.sleep(nightSleepSec)
        camera.exposure_mode = 'off'
        if imagePreview:
            camera.start_preview()        
        camera.capture(filename)
    shutSec = shut2Sec(currentShut)
    logging.info("Size=%ix%i dayPixAve=%i ISO=%i shut=%s %s" % (imageWidth, imageHeight, dayPixAve, currentISO, shutSec, filename))
    return

#-----------------------------------------------------------------------------------------------
def takeQuickTimeLapse(motionPath, imagePrefix, motionNumOn, motionNumCount, daymode, motionNumPath):
    logging.info("motion Quick Time Lapse for %i sec every %i sec" % (motionQuickTLTimer, motionQuickTLInterval))

    checkTimeLapseTimer = datetime.datetime.now()
    keepTakingImages = True
    filename = getImageName(motionPath, imagePrefix, motionNumOn, motionNumCount)
    while keepTakingImages:
        yield filename
        rightNow = datetime.datetime.now()
        timelapseDiff = (rightNow - checkTimeLapseTimer).total_seconds()
        if timelapseDiff > motionQuickTLTimer:
            keepTakingImages=False
        else:
            motionNumCount = postImageProcessing(motionNumOn, motionNumStart, motionNumMax, motionNumCount, motionNumRecycle, motionNumPath, filename, daymode)    
            filename = getImageName(motionPath, imagePrefix, motionNumOn, motionNumCount)
            time.sleep(motionQuickTLInterval)

#-----------------------------------------------------------------------------------------------
def takeVideo(filename):
    # Take a short motion video if required
    logging.info("Size %ix%i for %i sec %s" % (imageWidth, imageHeight, motionVideoTimer, filename))
    if motionVideoOn:
        with picamera.PiCamera() as camera:
            camera.resolution = (imageWidth, imageHeight)
            camera.vflip = imageVFlip
            camera.hflip = imageHFlip
            camera.rotation = imageRotation #Note use imageVFlip and imageHFlip variables
            if showDateOnImage:
                rightNow = datetime.datetime.now()            
                dateTimeText = " Started at %04d-%02d-%02d %02d:%02d:%02d " % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
                camera.annotate_text_size = showTextFontSize
                camera.annotate_foreground = picamera.Color('black')
                camera.annotate_background = picamera.Color('white')               
                camera.annotate_text = dateTimeText              
            camera.start_recording(filename)
            camera.wait_recording(motionVideoTimer)
            camera.stop_recording()
        # This creates a subprocess that runs convid.sh with the filename as a parameter
        try:
            convid = "%s/convid.sh %s" % ( baseDir, filename )        
            proc = subprocess.Popen(convid, shell=True,
                             stdin=None, stdout=None, stderr=None, close_fds=True) 
        except IOError:
            print("subprocess %s failed" %s ( convid ))
        else:        
            print("unidentified error")
        createSyncLockFile(filename)            
    return

#-----------------------------------------------------------------------------------------------    
def createSyncLockFile(imagefilename):
    # If required create a lock file to indicate file(s) to process
    if createLockFile:
        if not os.path.exists(lockFilePath):
            open(lockFilePath, 'w').close()
            logging.info("Create gdrive sync.sh Lock File %s", lockFilePath)
        rightNow = datetime.datetime.now()
        now = "%04d%02d%02d-%02d%02d%02d" % ( rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second )
        filecontents = now + " createSyncLockFile - "  + imagefilename + " Ready to sync using sudo ./sync.sh command." 
        f = open(lockFilePath, 'w+')
        f.write(filecontents)
        f.close()
    return

#----------------------------------------------------------------------------------------------- 
def getStreamImage(isDay):
    # Capture an image stream to memory based on daymode
    with picamera.PiCamera() as camera:
        camera.resolution = (testWidth, testHeight)
        with picamera.array.PiRGBArray(camera) as stream:
            if isDay:
                time.sleep(0.5)            
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto' 
                camera.capture(stream, format='rgb', use_video_port=useVideoPort)
            else:
                # Take Low Light image            
                # Set a framerate_range then set shutter
                # speed to 6s
                camera.framerate_range = (Fraction(1, 6), Fraction(30, 1))
                camera.sensor_mode = 3                
                camera.shutter_speed = nightMaxShut
                camera.iso = nightMaxISO
                # Give the camera a good long time to measure AWB
                # Note sleep time is hard coded and not set by nightSleepSec
                time.sleep( 10 )
                camera.exposure_mode = 'off'                
                camera.capture(stream, format='rgb')
            return stream.array

#-----------------------------------------------------------------------------------------------
def getStreamPixAve(streamData):
    # Calculate the average pixel values for the specified stream (used for determining day/night or twilight conditions)
    pixAverage = int(np.average(streamData[...,1]))
    return pixAverage

#-----------------------------------------------------------------------------------------------
def getNightCamSettings(dayPixAve):
    # Calculate Ratio for adjusting shutter and ISO values
    if dayPixAve <= twilightThreshold:
        ratio = ((twilightThreshold - dayPixAve)/float(twilightThreshold)) 
        outShut = int(nightMaxShut * ratio)
        outISO  = int(nightMaxISO * ratio)
    else:
        ratio = 0.0
        outShut = nightMinShut
        outISO = nightMinISO 
    # Do some Bounds Checking to avoid potential problems
    if outShut < nightMinShut:
        outShut = nightMinShut
    if outShut > nightMaxShut:
        outShut = nightMaxShut
    if outISO < nightMinISO:
        outISO = nightMinISO
    if outISO > nightMaxISO:
        outISO = nightMaxISO
    logging.info("dayPixAve=%i ratio=%.3f ISO=%i shut=%i %s" % ( dayPixAve, ratio, outISO, outShut, shut2Sec(outShut)))
    return outShut, outISO

#-----------------------------------------------------------------------------------------------    
def checkIfDay(currentDayMode, dataStream):
    # Try to determine if it is day, night or twilight.  
    dayPixAverage = 0 
    if currentDayMode:
        dayPixAverage = getStreamPixAve(dataStream)
    else:
        dayStream = getStreamImage(True)
        dayPixAverage = getStreamPixAve(dayStream) 
        
    if dayPixAverage > twilightThreshold:
        currentDayMode = True
    else:
        currentDayMode = False
    return currentDayMode

#-----------------------------------------------------------------------------------------------    
def timeToSleep(currentDayMode):
    if noNightShots:
       if currentDayMode:
          sleepMode=False
       else:
          sleepMode=True
    elif noDayShots:
        if currentDayMode:
           sleepMode=True
        else:
           sleepMode=False
    else:
        sleepMode=False
    return sleepMode

#----------------------------------------------------------------------------------------------- 
def checkForTimelapse (timelapseStart):
    # Check if timelapse timer has expired
    rightNow = datetime.datetime.now()
    timeDiff = ( rightNow - timelapseStart).total_seconds()
    if timeDiff > timelapseTimer:
        timelapseStart = rightNow
        timelapseFound = True
    else:
        timelapseFound = False 
    return timelapseFound

#----------------------------------------------------------------------------------------------- 
def checkForMotion(data1, data2):
    # Find motion between two data streams based on sensitivity and threshold
    motionDetected = False
    pixColor = 3 # red=0 green=1 blue=2 all=3  default=1
    if pixColor == 3:
        pixChanges = (np.absolute(data1-data2)>threshold).sum()/3
    else:
        pixChanges = (np.absolute(data1[...,pixColor]-data2[...,pixColor])>threshold).sum()
    if pixChanges > sensitivity:
        motionDetected = True
    if motionDetected:
        dotCount = showDots(motionMaxDots + 2)      # New Line
        logging.info("Found Motion - threshold=%s  sensitivity=%s changes=%s", threshold, sensitivity, pixChanges)
    return motionDetected  

#----------------------------------------------------------------------------------------------- 
def dataLogger():
    # Replace main() with this function to log day/night pixAve to a file.
    # Note variable logDataToFile must be set to True in config.py  
    # You may want to delete pi-timolo.log to clear old data.
    print("dataLogger - One Moment Please ....")
    while True:
        dayStream = getStreamImage(True)
        dayPixAverage = getStreamPixAve(dayStream)
        nightStream = getStreamImage(False)
        nightPixAverage = getStreamPixAve(nightStream)
        logging.info("nightPixAverage=%i dayPixAverage=%i twilightThreshold=%i " % (nightPixAverage, dayPixAverage, twilightThreshold))
        time.sleep(1)
    return

#----------------------------------------------------------------------------------------------- 
def Main():
    # Main program initialization and logic loop
    dotCount = 0   # Counter for showDots() display if not motion found (shows system is working)
    checkImagePath()
    timelapseNumCount = 0
    motionNumCount = 0
    try:  #if motionAverage hasn't been included in config file (so it works with previous versions)
        global motionAverage
        if motionAverage > 1:
            resetSensitivity = sensitivity*150   # number of changed pixels to trigger reset of background average
            if resetSensitivity > testHeight*testWidth*2:
                resetSensitivity = testHeight*testWidth*2  #limit the resetSensitivity
        else:
            motionAverage = 1
    except NameError:
        motionAverage = 1
    try:
        global useVideoPort
        useVideoPort = useVideoPort
    except NameError:
        useVideoPort = False
    moCnt = "non"
    tlCnt = "non"
    if timelapseOn:
        if timelapseNumOn:
            timelapseNumCount = getCurrentCount(timelapseNumPath, timelapseNumStart)
            tlCnt = str(timelapseNumCount)
    if motionOn:
        if motionNumOn:
            motionNumCount = getCurrentCount(motionNumPath, motionNumStart)
            moCnt = str(motionNumCount) 
    displayInfo(moCnt, tlCnt)
    if imageTestPrint:
        takeTestImage() # prints one image and exits if imageTestPrint = True in config.py
    daymode = False
    data1 = getStreamImage(True).astype(float)  #All functions should still work with float instead of int - just takes more memory
    daymode = checkIfDay(daymode, data1)
    data2 = getStreamImage(daymode)  # initialise data2 to use in main loop
    if not daymode:
        data1 = data2.astype(float)
    timelapseStart = datetime.datetime.now()
    checkDayTimer = timelapseStart
    checkMotionTimer = timelapseStart
    forceMotion = False   # Used for forcing a motion image if no motion for motionForce time exceeded
    logging.info("Entering Loop for Time Lapse and/or Motion Detect  Please Wait ...")
    dotCount = showDots(motionMaxDots)  # reset motion dots
    # Start main program loop here.  Use Ctl-C to exit if run from terminal session.
    while True:
        # use data2 to check daymode as data1 may be average that changes slowly, and data1 may not be updated
        if daymode != checkIfDay(daymode, data2):  # if daymode has changed, reset background, to avoid false motion trigger
            daymode = not daymode
            data2 = getStreamImage(daymode)  #get new stream
            data1 = data2.astype(float)    #reset background
        else:
            data2 = getStreamImage(daymode)      # This gets the second stream of motion analysis
        rightNow = datetime.datetime.now()   # refresh rightNow time
        if not timeToSleep(daymode):  # Don't take images if noNightShots or noDayShots settings are valid
            if timelapseOn:
                takeTimeLapse = checkForTimelapse(timelapseStart)
                if takeTimeLapse:
                    timelapseStart = datetime.datetime.now()  # reset time lapse timer
                    dotCount = showDots(motionMaxDots + 2)      # reset motion dots
                    logging.info("Scheduled Time Lapse Image - daymode=%s", daymode)
                    imagePrefix = timelapsePrefix + imageNamePrefix
                    filename = getImageName(timelapsePath, imagePrefix, timelapseNumOn, timelapseNumCount)
                    if daymode:
                        takeDayImage(filename)
                    else:
                        takeNightImage(filename)
                    timelapseNumCount = postImageProcessing(timelapseNumOn, timelapseNumStart, timelapseNumMax, timelapseNumCount, timelapseNumRecycle, timelapseNumPath, filename, daymode)
                    dotCount = showDots(motionMaxDots)
            if motionOn:
                # IMPORTANT - Night motion detection may not work very well due to long exposure times and low light (may try checking red instead of green)
                # Also may need night specific threshold and sensitivity settings (Needs more testing)
                motionFound = checkForMotion(data1, data2)
                if motionAverage > 1 and (np.absolute(data2-data1)>threshold).sum() > resetSensitivity:
                    data1 = data2.astype(float)
                else:
                    data1 = data1+(data2-data1)/motionAverage
                rightNow = datetime.datetime.now()
                timeDiff = (rightNow - checkMotionTimer).total_seconds()
                if timeDiff > motionForce:
                    dotCount = showDots(motionMaxDots + 2)      # New Line
                    logging.info("No Motion Detected for %s minutes. Taking Forced Motion Image.", (motionForce / 60))
                    checkMotionTimer = rightNow
                    forceMotion = True
                if motionFound or forceMotion:
                    dotCount = showDots(motionMaxDots + 2)      # New Line 
                    checkMotionTimer = rightNow
                    if forceMotion:
                        forceMotion = False
                    imagePrefix = motionPrefix + imageNamePrefix 
                    # check if motion Quick Time Lapse option is On.  This option supersedes motionVideoOn 
                    if motionQuickTLOn and daymode:
                        filename = getImageName(motionPath, imagePrefix, motionNumOn, motionNumCount)
                        with picamera.PiCamera() as camera:
                            camera.resolution = (imageWidth, imageHeight)
                            camera.vflip = imageVFlip
                            camera.hflip = imageHFlip
                            time.sleep(.5)
                            # This uses yield to loop through time lapse sequence but does not seem to be faster due to writing images
                            camera.capture_sequence(takeQuickTimeLapse(motionPath, imagePrefix, motionNumOn, motionNumCount, daymode, motionNumPath))
                            motionNumCount = getCurrentCount(motionNumPath, motionNumStart)
                    else:                        
                        if motionVideoOn:
                            filename = getVideoName(motionPath, imagePrefix, motionNumOn, motionNumCount)
                            takeVideo(filename)
                        else:
                            filename = getImageName(motionPath, imagePrefix, motionNumOn, motionNumCount)
                            if daymode:
                                takeDayImage(filename)
                            else:
                                takeNightImage(filename)
                        motionNumCount = postImageProcessing(motionNumOn, motionNumStart, motionNumMax, motionNumCount, motionNumRecycle, motionNumPath, filename, daymode)
                    if motionFound:
                        # =========================================================================
                        # Put your user code in userMotionCodeHere() function at top of this script
                        # =========================================================================                    
                        userMotionCodeHere()
                        dotCount = showDots(motionMaxDots)
                else:
                    dotCount = showDots(dotCount)  # show progress dots when no motion found
    return

#-----------------------------------------------------------------------------------------------    
if __name__ == '__main__':
    try:
        if debug:
            dataLogger()
        else:
            Main()
    finally:
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("%s - Exiting Program" % progName)
        print("+++++++++++++++++++++++++++++++++++")
        print("")
