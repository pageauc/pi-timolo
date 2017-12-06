"""
shopcam plugin Senario

The shopcam settings below will monitor camera view using motion tracking.
When motion tracking is triggered, the camera will take a sequence of
time lapse images with motionQuickTLInterval seconds between images and continue
for motionQuickTLTimer seconds duration then stop and monitor for another 
motion tracking event.

Once the camera is setup you do not have to manage it for a each work session timelapse 
sequence, since it is only activated when work motion is tracked.  If work takes longer than 
motionQuickTLInterval then the next motion will trigger another timelapse sequence per settings.
Ideal for a timelapse project that spans many days with work happening at differnt times. 

Edit the settings below to suit your project needs. 
if config.py variable pluginEnable=True and pluginName=shopcam
then these settings will override the config.py settings.

"""
# Customize Settings Below to Suit your Project Needs
# ---------------------------------------------------

motionQuickTLTimer = 3600     # On motion do timelapse sequence for 60 minutes
motionQuickTLInterval =  300  # Take image every 5 minutes until timer runs out

imageNamePrefix = 'shop-tl-'  # default= 'shop-tl-' for all image file names. Eg garage-
imageWidth = 1920             # default= 1920 Full Size Image Width in px
imageHeight = 1080            # default= 1080  Full Size Image Height in px
imageVFlip = True             # default= False True Flips image Vertically
imageHFlip = True             # default= False True Flips image Horizontally
showDateOnImage = False       # default= True False=Do Not display date/time text on images

motionPrefix = "mo-"          # default= "mo-" Prefix for all Motion Detect images
motionDir = "media/shopcam"   # default= "media/shop_TL"  Folder Path for Motion Detect Image Storage
motionNumOn = True            # default= True  True=filenames by sequenced Number  False=filenames by date/time
motionNumRecycle = False      # default= True when NumMax reached restart at NumStart instead of exiting
motionNumStart = 10000        # default= 10000 Start 0f motion number sequence
motionNumMax  = 0             # default= 0 Max number of motion images desired. 0=Continuous


# Do not change these settings.
motionTrackOn = True          # Turn on Motion Tracking
motionQuickTLOn = True        # Turn on motion timelapse sequence mode
motionVideoOn = False         # Take images not video
motionTrackQuickPic = False   # Turn off quick picture from video stream
timelapseOn = False           # Turn off normal time lapse mode so only motion mode used.
videoRepeatOn = False         # Turn on Video Repeat Mode IMPORTANT Overrides timelapse and motion
motionForce = 0               # Do not force motion image if no motion for a period of time
