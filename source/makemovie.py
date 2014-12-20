#!/usr/bin/python
# written by Claude Pageau for use by pitimo.py image files.

print "initializing ...."
import StringIO
import subprocess
import os
import time
import csv
from datetime import datetime
import cgi, cgitb

imageWidth = 1920
imageHeight = 1080
imagePath = "timelapse"
movieName = "./makemovie.avi"
# movieName Can also include folder path, othewise file saved to current folder. 

# Aspect ratio of video eg SD=4/3 HD=16/9 Etc.
# Note put value in quotes.
aspectRatio = "16/9"
# Video fps (frames per second) vulue usually  between 2 to 30.  I recommend 5 fps to start
framesPerSec = 5

print "makemovie.py"
print "============"
print "Creating makemovie.txt file of *jpg files in google_drive folder." 
ls_params = " -t -r ./%s/*jpg > makemovie.txt" % imagePath
exit_status = subprocess.call("ls %s " % ls_params, shell=True)

print "Creating movie file %s using makemovie.txt" % ( movieName )
print "Settings = Image W=%s H=%s aspect=%s fps=%s filename=%s" % ( imageWidth, imageHeight, aspectRatio, framesPerSec, movieName )

mencoder_params = "-nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=%s:vbitrate=8000000 -vf scale=%s:%s -o %s -mf type=jpeg:fps=%s  mf://@makemovie.txt" % ( aspectRatio, imageWidth, imageHeight, movieName, framesPerSec )
print "memcoder_params = %s" % ( mencoder_params )
print "Creating Movie. This will take a while ......."
print "----------------------------------------------"


exit_status = subprocess.call("mencoder %s" % mencoder_params, shell=True)
print "makemovie.py"
print "============"
print "Finished timelapse movie filename=%s" % ( movieName )

