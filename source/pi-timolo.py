#!/usr/bin/python

# pitimolo - Raspberry Pi Long Duration Timelapse, Motion Detection, with Low Light Capability
# written by Claude Pageau Dec-2014 (original issue)
# getStreamImage function based on utpalc code based on brainflakes lightweight motion detection code on Raspberry PI forum - Thanks

progVer = "ver 1.10"

# Read Configuration variables from config.py file
import os
mypath=os.path.abspath(__file__)   # Find the full path of this python script
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
    from config import *

if verbose:
    print("------------------------------ Loading Python Libraries --------------------------------------")
else:
    print("Note: verbose=False (Disabled) Set verbose=True to Display Detailed Messages.")

# python libraries to load   
import sys
import time
import datetime
import picamera
import picamera.array
import numpy as np
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

def userMotionCodeHere():
    # Users can put code here that needs to be run prior to taking motion capture images
    # Eg Notify or activate something.
    
    # User code goes here
    
    return    

def shut2Sec (shutspeed):
    shutspeedSec = shutspeed/float(SECONDS2MICRO)
    shutstring = str("%.3f sec") % ( shutspeedSec )
    return shutstring
    
def showTime():
    rightNow = datetime.datetime.now()
    currentTime = "%04d%02d%02d_%02d-%02d-%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return currentTime    
    
def showMessage(functionName, messageStr):
    if verbose:
        now = showTime()
        print ("%s %s - %s " % (now, functionName, messageStr))
    return

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
    
def checkConfig():
    if not motionOn and not timelapseOn:
        msgStr = "Warning - Both Motion and Timelapse are turned OFF - motionOn=%s timelapseOn=%s"
        showMessage("checkConfig", msgStr)
    return 
    
def logToFile(dataToAppend):
    if logDataToFile:
        logFilePath = baseDir + baseFileName + ".log"
        if not os.path.exists(logFilePath):
            open(logFilePath, 'w').close()
            msgStr = "Created New Data Logging File %s" % logFilePath
            showMessage("  logToFile", msgStr)
        filecontents = dataToAppend
        f = open(logFilePath, 'ab')
        f.write(filecontents)
        f.close()
    return
    
def takeTestImage():
    # Check if any parameter was passed to this script from the command line.
    # This is useful for taking a single image for aligning camera without editing script settings.
    mytime=showTime()
    testfilename = "takeTestImage.jpg"
    testfilepath = baseDir + testfilename
    takeDayImage(testfilepath)    
    imagetext = "%s %s" % (mytime, testfilename)
    writeTextToImage(testfilepath, imagetext)
    msgStr = "imageTestPrint=%s Captured Test Image to %s " % (imageTestPrint, testfilepath)
    showMessage ("takeTestImage", msgStr)
    sys.exit(2)
    return

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
        print("Images ....... Size=%ix%i   Prefix=%s   VFlip=%s   HFlip=%s   Preview=%s" % (imageWidth, imageHeight, imageNamePrefix, imageVFlip, imageHFlip, imagePreview))
        print("               noNightShots=%s   noDayShots=%s" % (noNightShots, noDayShots))
        print("Thresholds ... PixAverages[ Sunset=%i  Sunrise=%i ]  nightDayTimer=%i sec(Periodic Day/Night Checks)" % (sunsetThreshold, sunriseThreshold, nightDayTimer))
        shutStr = shut2Sec(nightMaxShut)
        print("               nightMaxShut=%i %s  nightMaxISO=%i   nightSleep=%i sec" % (nightMaxShut, shutStr, nightMaxISO, nightSleepSec))
        print("Image Text ... On=%s  Bottom=%s (Top=False)   WhiteText=%s (False=Black)" % (showDateOnImage, showTextBottom, showTextWhite)) 
        print("Motion ....... On=%s  Prefix=%s  threshold=%i(How Much)  sensitivity=%i(How Many)  forceTimer=%i sec(If No Motion)"  % (motionOn, motionPrefix, threshold, sensitivity, motionForce))
        print("               videoOn=%s   videoTime=%i sec" % (motionVideoOn, motionVideoTimer))
        print("               motionPath=%s" % (motionPath))
        if motionNumOn:
            print("Motion Num ... On=%s  current=%s   numStart=%i   numMax=%i   numRecycle=%s"  % (motionNumOn, motioncount, motionNumStart, motionNumMax, motionNumRecycle))
            print("               numPath=%s " % (motionNumPath))
        if createLockFile:
            print("Grive Sync ... On=%s  Path=%s  Note: syncs for motion images only." % (createLockFile, lockFilePath))       
        print("Time Lapse ... On=%s  Prefix=%s   Timer=%i sec   timeLapseExit=%i sec(0=Continuous)" % (timelapseOn, timelapsePrefix, timelapseTimer, timelapseExit)) 
        print("               timelapsePath=%s" % (timelapsePath))
        if timelapseNumOn:
            print("TL Numbering . On=%s  current=%s   numStart=%i   numMax=%i   numRecycle=%s"  % (timelapseNumOn, timelapsecount, timelapseNumStart, timelapseNumMax, timelapseNumRecycle))
            print("               numPath=%s" % (timelapseNumPath))
        print("Logging ...... verbose=%s (Details to Console)    logDataToFile=%s  logfile=%s" % ( verbose, logDataToFile, baseDir + baseFileName + ".log" ))
        print("------------------------------------ Log Activity --------------------------------------------")
    checkConfig()        
    return            
    
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

def writeTextToImage( imagename, datetoprint ):
    # function to write date/time stamp directly on top or bottom of images.
    if showTextWhite:
        FOREGROUND = ( 255, 255, 255 )  # rgb settings for white text foreground
    else:
        FOREGROUND = ( 0, 0, 0 )  # rgb settings for black text foreground
    
    if not daymode and showTextWhiteNight: # Force night Text to be white
        FOREGROUND = ( 255, 255, 255 )  # rgb settings for white text foreground
    
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
    img = Image.open(imagename)
    draw = ImageDraw.Draw(img)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text(( x, y ),text,FOREGROUND,font=font)
    img.save(imagename)
    msgStr = "Completed - Text=" + datetoprint + " to filename" + imagename
    showMessage("  writeDataToImage",msgStr)
    return
 
def postImageProcessing(numberon, counterstart, countermax, counter, recycle, counterpath, filename):
    # If required process text to display directly on image
    if not motionVideoOn:
        rightNow = datetime.datetime.now()
        if showDateOnImage:
            dateTimeText = "%04d%02d%02d-%02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
            if numberon:
                counterStr = "%i    "  % ( counter )
                imageText =  counterStr + dateTimeText
            else:
                imageText = dateTimeText
            # Now put the imageText on the current image
            writeTextToImage(filename, imageText)
            if createLockFile:
                createGriveLockFile(filename)
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
        msgStr = "Completed - Next Counter=" + str(writeCount) + " " + counterpath
        showMessage("  postImageProcessing", msgStr)
    return counter
       
def getFileName(path, prefix, numberon, counter):
    # build image file names by number sequence or date/time
    if numberon:
        filename = path + "/" + prefix + str(counter) + ".jpg"
        if motionVideoOn:
            filename = path + "/" + prefix + str(counter) + ".h264"        
    else:
        rightNow = datetime.datetime.now()
        filename = "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
        if motionVideoOn:
            filename = "%s/%s%04d%02d%02d-%02d%02d%02d.h264" % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return filename    

def takeDayImage(filename):
    # Take a Day image using exp=auto and awb=auto
    autowait = 0.5
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight) 
        # camera.rotation = cameraRotate #Note use imageVFlip and imageHFlip variables
        time.sleep(autowait)   # sleep for a little while so camera can get adjustments
        if imagePreview:
            camera.start_preview()
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(filename)
    msgStr = "Captured - Image=" + str(imageWidth) + "x" + str(imageHeight) + " VFlip=" + str(imageVFlip) +" HFlip=" + str(imageHFlip) + " autowait=" + str(autowait) + " sec " + filename
    showMessage("  takeDayImage", msgStr)
    return
    
def takeNightImage(filename, currentShut, currentISO):
    # Take low light Night image (including twilight zones)
    with picamera.PiCamera() as camera:
        # Take Low Light image            
        # Set a framerate of 1/6fps, then set shutter
        # speed to 6s and ISO to 800
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
    msgStr = "- Image=%ix%i VFlip=%s HFlip=%s nightSleepSec=%i ISO=%i shut=%i %s %s"  %( imageWidth, imageHeight, imageVFlip, imageHFlip, nightSleepSec, currentISO, currentShut, shut2Sec(currentShut), filename )
    dataToLog = showTime() + " takeNightImage " + msgStr + "\n"
    logToFile(dataToLog)
    showMessage("  takeNightImage", msgStr)
    return        

def takeVideo(filename):
    # Take a short motion video if required
    msgStr = "Capturing Motion Video Size %ix%i for %i seconds to %s" % (imageWidth, imageHeight, motionVideoTimer, filename)
    showMessage("  takeVideo", msgStr)        
    if motionVideoOn:
        with picamera.PiCamera() as camera:
            camera.resolution = (imageWidth, imageHeight)
            camera.start_recording(filename)
            camera.wait_recording(motionVideoTimer)
            camera.stop_recording()
    return
    
def createGriveLockFile(imagefilename):
    # If required create a lock file to indicate grive (sync.sh) has file(s) to process
    if createLockFile:
        if not os.path.exists(lockFilePath):
            open(lockFilePath, 'w').close()
            msgStr = "Created grive sync.sh Lock File " + lockFilePath
            showMessage("  createGriveLockFile", msgStr)
        rightNow = datetime.datetime.now()
        now = "%04d%02d%02d-%02d%02d%02d" % ( rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second )
        filecontents = now + " createGriveLockFile - "  + imagefilename + " Ready to sync using sudo ./sync.sh command." 
        f = open(lockFilePath, 'w+')
        f.write(filecontents)
        f.close()
    return          
 
def getStreamImage(daymode):
    # Capture an image stream to memory based on daymode
    isDay = daymode
    with picamera.PiCamera() as camera:
        time.sleep(0.1)
        camera.resolution = (testWidth, testHeight)
        with picamera.array.PiRGBArray(camera) as stream:
            if isDay:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto' 
            else:
                # Take Low Light image            
                # Set a framerate of 1/6fps, then set shutter
                # speed to 6s and ISO to 800
                camera.framerate = Fraction(1, 6)
                camera.shutter_speed = nightMaxShut
                camera.exposure_mode = 'off'
                camera.iso = nightMaxISO
                # Give the camera a good long time to measure AWB
                # (you may wish to use fixed AWB instead)
                time.sleep( nightSleepSec )
            camera.capture(stream, format='rgb')
            return stream.array

def getStreamPixAve(streamData):
    # Calculate the average pixel values for the specified stream (used for determining day/night or twilight conditions)
    pixAverage = int(np.average(streamData[...,0]))
    return pixAverage

def getTwilghtCamSettings (sunset, dayPixAve):
    # Calculate Ratio
    ratio = (sunsetThreshold - dayPixAve)/float(sunsetThreshold) 
    outShut = int(nightMaxShut * ratio)
    outISO  = int(nightMaxISO * ratio)      
    # Do some Bounds Checking to avoid problems        
    if outShut < nightMinShut:
        outShut = nightMinShut
    if outShut > nightMaxShut:
        outShut = nightMaxShut
    if outISO < nightMinISO:
        outISO = nightMinISO
    if outISO > nightMaxISO:
        outISO = nightMaxISO
    msgStr = "Camera Settings - sunset=%s dayPixAve=%i ratio=%.3f ISO=%i shut=%i %s" % ( sunset, dayPixAve, ratio, outISO, outShut, shut2Sec(outShut)) 
    showMessage("  getTwilightCamSettings", msgStr)
    return outShut, outISO
    
def checkIfDay(currentDayMode, sunSet, dataStream):
    # Try to determine if it is day, night or twilight.  
    # Best if program started during full day or full night to avoid common twilight light conditions
    dayPixAverage = 0      # initialize since may not be used for Full Night
    nightPixAverage = 0    # initialize since may not be used for Full Day
    shut = 99              # initialize since daymode needs a dummy return value
    ISO = 99               # initialize since daymode needs a dummy return value
    status = "Unknown"
    if currentDayMode:
        # Currently in DAY Mode since currentDayMode=True camera is in Day Auto settings
        dayPixAverage = getStreamPixAve(dataStream)
        if dayPixAverage > sunsetThreshold:
            status = "1D- Full Day"
            currentDayMode = True
            sunSet = True
        else:
            # Confirm if it is really day by overexposure of night shot
            nightStream = getStreamImage(False)
            nightPixAverage = getStreamPixAve(nightStream)
            if nightPixAverage > 253 and dayPixAverage > sunsetThreshold: 
                status = "2D- Full Day"
                currentDayMode = True
                sunSet = True
                # Check for Twilight Conditions            
            else:
                # Should be in SunSet Twilight
                status = "3D- SunSet Twilight"
                currentDayMode = False
                sunSet = True
                dataStream = nightStream
                shut, ISO = getTwilghtCamSettings (sunSet, dayPixAverage)  
    else:
        nightPixAverage = getStreamPixAve(dataStream)
        dayStream = getStreamImage(True)
        dayPixAverage = getStreamPixAve(dayStream)
        if sunSet:
            if nightPixAverage > sunriseThreshold and dayPixAverage < sunsetThreshold:
                status = "1N- SunSet Twilight"
                currentDayMode = False
                sunSet = True
                shut, ISO = getTwilghtCamSettings(sunSet, dayPixAverage)                      
            else:
                status = "2N- Full Night"
                currentDayMode = False
                sunSet = False
                shut = nightMaxShut
                ISO  = nightMaxISO
        else: 
            if nightPixAverage > 253 and dayPixAverage > sunsetThreshold:
                # It is Day
                status = "3N- Full Day"
                currentDayMode = True
                sunSet = True                    
                dataStream = dayStream
            else:
                if nightPixAverage > sunriseThreshold and dayPixAverage < sunsetThreshold:                
                    status = "4N- SunRise Twilight"
                    currentDayMode = False
                    sunSet = False
                    shut, ISO = getTwilghtCamSettings(sunSet, dayPixAverage)
                else:
                    status = "5N- Full Night"
                    currentDayMode=False
                    sunSet = False
                    shut = nightMaxShut
                    ISO = nightMaxISO         
    if currentDayMode:
        msgStr = "- currentDayMode=%s -%s- dayPixAverage=%i nightPixAverage=%i"   %  (currentDayMode, status, dayPixAverage, nightPixAverage)
    else:    
        msgStr = "- currentDayMode=%s -%s- dayPixAverage=%i nightPixAverage=%i ISO=%i Shut=%i %s"   %  (currentDayMode, status, dayPixAverage, nightPixAverage, ISO, shut, shut2Sec(shut))
    showMessage("  checkIfDay", msgStr)
    dataToLog = showTime() + " checkIfDay " + msgStr + "\n"
    logToFile(dataToLog)
    return dataStream, sunSet, currentDayMode, shut, ISO
    
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
    
def timeToSleep(daymode):
    if noNightShots:
       if daymode:
          sleepMode=False
       else:
          sleepMode=True
    elif noDayShots:
        if daymode:
           sleepMode=True
        else:
           sleepMode=False
    else:
        sleepMode=False    
    return sleepMode
    
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
        msgStr = "Found Motion - sensitivity=" + str(sensitivity) + " Exceeded ..."
        showMessage("checkForMotion", msgStr)
    return motionDetected  
 
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
        logdata  = "nightPixAverage=%i  sunriseThreshold=%i  dayPixAverage=%i  sunsetThreshold=%i  " % ( nightPixAverage, sunriseThreshold, dayPixAverage, sunsetThreshold )
        showMessage("dataLogger",logdata)
        logdata = now + " " + logdata
        logToFile(logdata)
        time.sleep(60)
    return    
 
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
    # image stream is taken with low light settings and if Day will be almost all white pix val >240
    msgStr = "Checking if Day or Night  One Moment Please ...."
    showMessage("Main", msgStr)
    daymode = False
    sunset = False
    nightStream = getStreamImage(daymode)
    streamData, daymode, sunset, newShut, newISO = checkIfDay(daymode, sunset, nightStream)
    data1 = streamData
    timelapseStart = datetime.datetime.now()
    checkDayTimer = timelapseStart
    checkMotionTimer = timelapseStart
    forceMotion = False   # Used for forcing a motion image if no motion for motionForce time exceeded
    msgStr = "Entering Motion Detection and Time Lapse Loop  Working ..."
    showMessage("Main", msgStr)
    dotCount = showDots(motionMaxDots)  # reset motion dots
    # Start main program loop here.  Use Ctl-C to exit if required.
    while True:
        data2 = getStreamImage(daymode)      # This gets the second stream of motion analysis
        rightNow = datetime.datetime.now()   # refresh rightNow time

        if not timeToSleep(daymode):
            if timelapseOn:
                takeTimeLapse = checkForTimelapse(timelapseStart)
                if takeTimeLapse:
                    imagePrefix = timelapsePrefix + imageNamePrefix            
                    filename = getFileName(timelapsePath, imagePrefix, timelapseNumOn, timelapseNumCount)
                    tdaymode = daymode
                    streamData, daymode, sunset, newShut, newISO = checkIfDay( daymode, sunset, data2)
                    dotCount = showDots(motionMaxDots + 2)      # reset motion dots              
                    msgStr = "Scheduled Time Lapse Image - daymode=" + str(daymode)
                    showMessage("Main", msgStr)    
                    if not tdaymode == daymode:  # if daymode changed then avoid false motion below by making streams the same 
                        data1 = streamData
                        data2 = streamData
                    if daymode:
                        takeDayImage(filename)    
                    else:
                        takeNightImage(filename, newShut, newISO)
                    timelapseNumCount = postImageProcessing(timelapseNumOn, timelapseNumStart, timelapseNumMax, timelapseNumCount, timelapseNumRecycle, timelapseNumPath, filename)
                    timelapseStart = datetime.datetime.now()  # reset timelapse timer
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
                    if motionFound:
                        dotCount = showDots(motionMaxDots + 2)      # New Line   
                    imagePrefix = motionPrefix + imageNamePrefix            
                    filename = getFileName(motionPath, imagePrefix, motionNumOn, motionNumCount)
                    if daymode:
                        takeDayImage(filename)
                    else:
                        takeNightImage(filename, newShut, newISO)
                    motionNumCount = postImageProcessing(motionNumOn, motionNumStart, motionNumMax, motionNumCount, motionNumRecycle, motionNumPath, filename)
                    dotCount = showDots(motionMaxDots)
                    if motionFound:
                        # =========================================================================
                        # Put your user code in userMotionCodeHere() function at top of this script
                        # =========================================================================                    
                        userMotionCodeHere()
                        if motionVideoOn:
                           takeVideo(filename)
                        dotCount = showDots(motionMaxDots)       
                else:
                    dotCount = showDots(dotCount)  # show progress dots when no motion found
 
        # Check if day/night checking timer is exceeded
        rightNow = datetime.datetime.now()
        timeDiff = ( rightNow - checkDayTimer).total_seconds()
        if timeDiff > nightDayTimer:
            dotCount = showDots(motionMaxDots + 2 )      # New Line              
            msgStr = "Check Day/Night - nightDayTimer=" + str(nightDayTimer) + " sec Exceeded ... timeToSleep=" + str(timeToSleep(daymode))
            showMessage("Main", msgStr)
            checkDayTimer = rightNow
            tdaymode = daymode  # used to check if daymode has changed
            streamData, sunset, daymode, newShut, newISO = checkIfDay(tdaymode, sunset, data2)
            dotCount = showDots(motionMaxDots)      # reset motion dots             
            if not tdaymode == daymode:
                data2 = streamData
        data1 = data2
    return
    
if __name__ == '__main__':
    try:
        Main()
    finally:
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("%s - Exiting Program" % progName)
        print("+++++++++++++++++++++++++++++++++++")
        print("")
    
    
