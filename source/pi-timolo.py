#!/usr/bin/python

# pi-timolo - Raspberry Pi Long Duration Timelapse, Motion Detection, with Low Light Capability
# written by Claude Pageau Dec-2014 (original issue)
# getStreamImage function based on utpalc code based on brainflakes lightweight motion detection code on Raspberry PI forum - Thanks
# Complete pi-timolo code and instructions are available on my github repo at https://github.com/pageauc

# 2.7 released 20-Jul-2015  added saving of exif metadata when text written to image sinc PIL does not retain this.
# 2.8 released 2-Aug-2015 updated gdrive and replaced mencoder with avconv

progVer = "ver 2.8"

import os
mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)

# Check for variable file to import and error out if not found.
configFilePath = baseDir + "config.py"
if not os.path.exists(configFilePath):
    msgStr = "ERROR - Missing config.py file - Could not find Configuration file %s" % (configFilePath)
    showMessage("readConfigFile", msgStr)
    quit()
else:
    # Read Configuration variables from config.py file
    from config import *

if verbose:
    print("------------------------------ Loading Python Libraries --------------------------------------")
else:
    print("Note: verbose=False (Disabled) Set verbose=True to Display Detailed Messages.")

# import remaining python libraries  
import sys
import time
import datetime
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
testWidth = 100            # width of rgb image stream used for motion detection and day/night changes
testHeight = 75            # height of rgb image stream used for motion detection and day/night changes
daymode = False            # default should always be False.
progNameVer = "%s %s" %(progName, progVer)
motionPath = baseDir + motionDir  # Store Motion images
motionNumPath = baseDir + motionPrefix + baseFileName + ".dat"  # dat file to save currentCount
timelapsePath = baseDir + timelapseDir  # Store Time Lapse images
timelapseNumPath = baseDir + timelapsePrefix + baseFileName + ".dat"  # dat file to save currentCount
lockFilePath = baseDir + baseFileName + ".sync"

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
    currentTime = "%04d%02d%02d_%02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return currentTime    
    
#-----------------------------------------------------------------------------------------------    
def showMessage(functionName, messageStr):
    if verbose:
        now = showTime()
        print ("%s %s - %s " % (now, functionName, messageStr))
    return
    
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
        msgStr = "Warning - Both Motion and Timelapse are turned OFF - motionOn=%s timelapseOn=%s"
        showMessage("checkConfig", msgStr)
    return 
    
#-----------------------------------------------------------------------------------------------    
def logToFile(dataToAppend):
    if logDataToFile:
        logFilePath = baseDir + baseFileName + ".log"
        if not os.path.exists(logFilePath):
            open(logFilePath, 'w').close()
            msgStr = "Create New Data Log File %s" % logFilePath
            showMessage("  logToFile", msgStr)
        filecontents = dataToAppend
        f = open(logFilePath, 'ab')
        f.write(filecontents)
        f.close()
    return
     
#-----------------------------------------------------------------------------------------------   
def takeTestImage():
    # Check if any parameter was passed to this script from the command line.
    # This is useful for taking a single image for aligning camera without editing script settings.
    mytime=showTime()
    testfilename = "takeTestImage.jpg"
    testfilepath = baseDir + testfilename
    takeDayImage(testfilepath)    
    imagetext = "%s %s" % (mytime, testfilename)
    writeTextToImage(testfilepath, imagetext, daymode)
    msgStr = "imageTestPrint=%s Captured Test Image to %s " % (imageTestPrint, testfilepath)
    showMessage ("takeTestImage", msgStr)
    sys.exit(2)
    return
    
#-----------------------------------------------------------------------------------------------
def displayInfo(motioncount, timelapsecount):
    if verbose:
        print("")
        print("Note: To Send Full Output to File Use command -   python -u ./%s | tee -a log.txt" % progName)
        print("      Set logDataToFile=True to Send checkIfDay Data to File %s.log" % progName)
        print("")
        print("%s" % progNameVer)     
        print("-------------------------------------- Settings ----------------------------------------------")
        print("Config File .. Title=%s" % configTitle)
        print("               config-template filename=%s" % configName)
        print("Image Info ... Size=%ix%i   Prefix=%s   VFlip=%s   HFlip=%s   Preview=%s" % (imageWidth, imageHeight, imageNamePrefix, imageVFlip, imageHFlip, imagePreview))
        shutStr = shut2Sec(nightMaxShut)
        print("    Low Light. twilightThreshold=%i  nightMaxShut=%s  nightMaxISO=%i   nightSleepSec=%i sec" % (twilightThreshold, shutStr, nightMaxISO, nightSleepSec))
        print("    No Shots . noNightShots=%s   noDayShots=%s" % (noNightShots, noDayShots))       
        if showDateOnImage:
            print("    Img Text . On=%s  Bottom=%s (False=Top)  WhiteText=%s (False=Black)  showTextWhiteNight=%s" % (showDateOnImage, showTextBottom, showTextWhite, showTextWhiteNight)) 
        else:
            print("    No Text .. showDateOnImage=%s  Text on Image Disabled"  % (showDateOnImage))
        print("Motion ....... On=%s  Prefix=%s  threshold=%i(How Much)  sensitivity=%i(How Many)  forceTimer=%i min(If No Motion)"  % (motionOn, motionPrefix, threshold, sensitivity, motionForce/60))
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
        print("Logging ...... verbose=%s (Details to Console)    logDataToFile=%s  logfile=%s" % ( verbose, logDataToFile, baseDir + baseFileName + ".log" ))
        print("------------------------------------ Log Activity --------------------------------------------")
    checkConfig()        
    return            
    
#-----------------------------------------------------------------------------------------------    
def checkImagePath():
    # Checks for image folders and creates them if they do not already exist.
    if motionOn:
        if not os.path.isdir(motionPath):
            msgStr = "Creating Image Motion Detection Storage Folder" + motionPath
            showMessage ("checkImagePath", msgStr)
            os.makedirs(motionPath)
    if timelapseOn:
        if not os.path.isdir(timelapsePath):
            msgStr = "Creating Time Lapse Image Storage Folder" + timelapsePath
            showMessage ("checkImagePath", msgStr)
            os.makedirs(timelapsePath)
    return
    
#-----------------------------------------------------------------------------------------------    
def getCurrentCount(numberpath, numberstart):
    # Create a .dat file to store currentCount or read file if it already Exists
    # Create numberPath file if it does not exist
    if not os.path.exists(numberpath):
        msgStr = "Creating File " + numberpath + " numberstart=" + str(numberstart)
        showMessage("getCurrentCount", msgStr)   
        open(numberpath, 'w').close()
        f = open(numberpath, 'w+')
        f.write(str(numberstart))
        f.close()
      # Read the numberPath file to get the last sequence number
    with open(numberpath, 'r') as f:
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
    font = ImageFont.truetype(font_path, 24, encoding='unic')
    text = TEXT.decode('utf-8')

    # Read exif data since ImageDraw does not save this metadata
    metadata = pyexiv2.ImageMetadata(imagename) 
    metadata.read()
    
    img = Image.open(imagename)
    draw = ImageDraw.Draw(img)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text(( x, y ), text, FOREGROUND, font=font)
    img.save(imagename)
    metadata.write()    # Write previously saved exif data to image file    
    msgStr = "Added " + textColour + " Text[" + datetoprint + "] on " + imagename
    showMessage("  writeDataToImage",msgStr)
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
            msgStr = "Create New Counter File writeCount=" + str(writeCount) + " " + counterpath
            showMessage("postImageProcessing", msgStr)
            open(counterpath, 'w').close()
        f = open(counterpath, 'w+')
        f.write(str(writeCount))
        f.close()
        msgStr = "Next Counter=" + str(writeCount) + " " + counterpath
        showMessage("  postImageProcessing", msgStr)
    return counter

def getVideoName(path, prefix, numberon, counter):
    # build image file names by number sequence or date/time
    if numberon:
        if motionVideoOn:
            filename = path + "/" + prefix + str(counter) + ".h264" 
    else:
        if motionVideoOn:
            rightNow = datetime.datetime.now()
            filename = "%s/%s%04d%02d%02d-%02d%02d%02d.h264" % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return filename    
 
#-----------------------------------------------------------------------------------------------       
def getImageName(path, prefix, numberon, counter):
    # build image file names by number sequence or date/time
    if numberon:
        filename = path + "/" + prefix + str(counter) + ".jpg"        
    else:
        rightNow = datetime.datetime.now()
        filename = "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)     
    return filename    
    
#-----------------------------------------------------------------------------------------------
def takeDayImage(filename):
    # Take a Day image using exp=auto and awb=auto
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight) 
        # camera.rotation = cameraRotate #Note use imageVFlip and imageHFlip variables
        time.sleep(0.5)   # sleep for a little while so camera can get adjustments
        if imagePreview:
            camera.start_preview()
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(filename)
    msgStr = "Size=%ix%i exp=auto awb=auto %s"  % (imageWidth, imageHeight, filename)
    dataToLog = showTime() + " takeDayImage " + msgStr + "\n"
    logToFile(dataToLog)
    showMessage("  takeDayImage", msgStr)
    return
     
#-----------------------------------------------------------------------------------------------   
def takeNightImage(filename):
    dayStream = getStreamImage(True)
    dayPixAve = getStreamPixAve(dayStream)
    currentShut, currentISO = getNightCamSettings(dayPixAve)
    # Take low light Night image (including twilight zones)
    with picamera.PiCamera() as camera:
        # Take Low Light image            
        # Set a framerate of 1/6fps, then set shutter
        camera.resolution = (imageWidth, imageHeight)
        if imagePreview:
            camera.start_preview()
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.framerate = Fraction(1, 6)
        camera.shutter_speed = currentShut
        camera.exposure_mode = 'off'
        camera.iso = currentISO
        # Give the camera a good long time to measure AWB
        # (you may wish to use fixed AWB instead)
        time.sleep(nightSleepSec)
        camera.capture(filename)
    shutSec = shut2Sec(currentShut)
    msgStr = "Size=%ix%i dayPixAve=%i ISO=%i shut=%s %s"  %( imageWidth, imageHeight, dayPixAve, currentISO, shutSec, filename )
    dataToLog = showTime() + " takeNightImage " + msgStr + "\n"
    logToFile(dataToLog)
    showMessage("  takeNightImage", msgStr)
    return        

#-----------------------------------------------------------------------------------------------
def takeQuickTimeLapse(motionPath, imagePrefix, motionNumOn, motionNumCount, daymode, motionNumPath):
    msgStr = "motion Quick Time Lapse for %i sec every %i sec" % (motionQuickTLTimer, motionQuickTLInterval)
    showMessage("Main", msgStr)
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
    msgStr = "Size %ix%i for %i sec %s" % (imageWidth, imageHeight, motionVideoTimer, filename)
    showMessage("  takeVideo", msgStr)        
    if motionVideoOn:
        with picamera.PiCamera() as camera:
            camera.resolution = (imageWidth, imageHeight)
            camera.start_recording(filename)
            camera.wait_recording(motionVideoTimer)
            camera.stop_recording()
    return
   
#-----------------------------------------------------------------------------------------------    
def createSyncLockFile(imagefilename):
    # If required create a lock file to indicate file(s) to process
    if createLockFile:
        if not os.path.exists(lockFilePath):
            open(lockFilePath, 'w').close()
            msgStr = "Create gdrive sync.sh Lock File " + lockFilePath
            showMessage("  createSyncLockFile", msgStr)
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
        time.sleep(0.5)
        camera.resolution = (testWidth, testHeight)
        with picamera.array.PiRGBArray(camera) as stream:
            if isDay:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto' 
            else:
                # Take Low Light image            
                # Set a framerate of 1/6fps, then set shutter
                # speed to 6s
                camera.framerate = Fraction(1, 6)
                camera.shutter_speed = nightMaxShut
                camera.exposure_mode = 'off'
                camera.iso = nightMaxISO
                # Give the camera a good long time to measure AWB
                # (you may wish to use fixed AWB instead)
                time.sleep( nightSleepSec )
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
    msgStr = "dayPixAve=%i ratio=%.3f ISO=%i shut=%i %s" % ( dayPixAve, ratio, outISO, outShut, shut2Sec(outShut)) 
    showMessage("  getNightCamSettings", msgStr)
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
    pixChanges = 0;
    pixColor = 1 # red=0 green=1 blue=2
    for w in range(0, testWidth):
        for h in range(0, testHeight):
            # get the diff of the pixel. Conversion to int
            # is required to avoid unsigned short overflow.
            pixDiff = abs(int(data1[h][w][pixColor]) - int(data2[h][w][pixColor]))
            if  pixDiff > threshold:
                pixChanges += 1
            if pixChanges > sensitivity:
                break; # break inner loop
        if pixChanges > sensitivity:
            break; #break outer loop.
    if pixChanges > sensitivity:
        motionDetected = True
    if motionDetected:
        dotCount = showDots(motionMaxDots + 2)      # New Line        
        msgStr = "Found Motion - threshold=" + str(threshold) + " sensitivity=" + str(sensitivity) + " Exceeded ..."
        showMessage("checkForMotion", msgStr)
    return motionDetected  
    
#----------------------------------------------------------------------------------------------- 
def dataLogger():
    # Replace main() with this function to log day/night pixAve to a file.
    # Note variable logDataToFile must be set to True in config.py  
    # You may want to delete pi-timolo.log to clear old data.
    print "dataLogger - One Moment Please ...."
    while True:
        dayStream = getStreamImage(True)
        dayPixAverage = getStreamPixAve(dayStream)    
        nightStream = getStreamImage(False)
        nightPixAverage = getStreamPixAve(nightStream)
        logdata  = "nightPixAverage=%i dayPixAverage=%i twilightThreshold=%i  " % ( nightPixAverage, dayPixAverage, twilightThreshold )
        showMessage("dataLogger",logdata)
        now = showTime()        
        logdata = now + " " + logdata
        logToFile(logdata)
        time.sleep(1)
    return    
    
#----------------------------------------------------------------------------------------------- 
def Main():
    # Main program initialization and logic loop
    dotCount = 0   # Counter for showDots() display if not motion found (shows system is working)
    checkImagePath()
    timelapseNumCount = 0
    motionNumCount = 0
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
    data1 = getStreamImage(True)
    daymode = checkIfDay(daymode, data1)
    if not daymode:
        data1 = getStreamImage(False)
    timelapseStart = datetime.datetime.now()
    checkDayTimer = timelapseStart
    checkMotionTimer = timelapseStart
    forceMotion = False   # Used for forcing a motion image if no motion for motionForce time exceeded
    msgStr = "Entering Motion Detect - Time Lapse Loop  Please Wait ..."
    showMessage("Main", msgStr)
    dotCount = showDots(motionMaxDots)  # reset motion dots
    # Start main program loop here.  Use Ctl-C to exit if run from terminal session.
    while True:
        daymode = checkIfDay(daymode, data1)
        data2 = getStreamImage(daymode)      # This gets the second stream of motion analysis
        rightNow = datetime.datetime.now()   # refresh rightNow time
        if not timeToSleep(daymode):  # Don't take images if noNightShots or noDayShots settings are valid
            if timelapseOn:
                takeTimeLapse = checkForTimelapse(timelapseStart)
                if takeTimeLapse:
                    dotCount = showDots(motionMaxDots + 2)      # reset motion dots              
                    msgStr = "Scheduled Time Lapse Image - daymode=" + str(daymode)
                    showMessage("Main", msgStr)    
                    imagePrefix = timelapsePrefix + imageNamePrefix            
                    filename = getImageName(timelapsePath, imagePrefix, timelapseNumOn, timelapseNumCount)
                    if daymode:
                        takeDayImage(filename)    
                    else:
                        takeNightImage(filename)
                    timelapseNumCount = postImageProcessing(timelapseNumOn, timelapseNumStart, timelapseNumMax, timelapseNumCount, timelapseNumRecycle, timelapseNumPath, filename, daymode)
                    timelapseStart = datetime.datetime.now()  # reset time lapse timer
                    dotCount = showDots(motionMaxDots)                  
            if motionOn:
                # IMPORTANT - Night motion detection may not work very well due to long exposure times and low light (may try checking red instead of green)
                # Also may need night specific threshold and sensitivity settings (Needs more testing)
                motionFound = checkForMotion(data1, data2)
                rightNow = datetime.datetime.now()
                timeDiff = (rightNow - checkMotionTimer).total_seconds()
                if timeDiff > motionForce:
                    dotCount = showDots(motionMaxDots + 2)      # New Line   
                    msgStr = "No Motion Detected for " + str(motionForce / 60) + " minutes. Taking Forced Motion Image."
                    showMessage("Main", msgStr)
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
        data1 = data2
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
    
    
