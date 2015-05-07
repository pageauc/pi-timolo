                                 pi-timolo
  Raspberry (Pi) (Ti)me Lapse, (Mo)tion Detect using (Lo)w Light Settings
  -----------------------------------------------------------------------

Note regarding Version 2.5
==========================
This version fixes a bug that caused a hang when video mode was True
A new feature adds quick time lapse after motion detected
The console display is cleaned up plus a number of other bug fixes
Please not the older config.py is not compatible with this release
since new variables have been added
Note:
This release does not include grive
As of 20-Apr-2015 grive no longer works until it can be modified.
I have included instructions for installing GDriveFS.  Here
https://www.raspberrypi.org/forums/viewtopic.php?p=753018&sid=d937a9e30526d324992968a7f4d73e6b#p753018

Claude ...
  
Introduction
============
This is a picamara python module application using a Raspberry PI with a RPI camera
module. Use for Long Duration Time Lapse and/or Motion Detection projects.  
File names can be by Number Sequence or by Date/Time Naming.  Time Lapse and Motion
image files can be named and save images to different folders or the same folder.  
Optionally motion files can be uploaded to your web based google drive using a
GDriveFS. (run setup-gdrivefs.sh for setup and instructions).
Note:
pi-timolo uses low light long exposure for night motion and/or timelapse images.
The program can detect motion during low light, although the long exposure times
can cause blurring of moving objects.

This application uses the picamera python module and requires the latest
RPI firmware and updates to work properly.
Here are some YouTube videos FYI https://www.youtube.com/playlist?list=PLLXJw_uJtQLa11A4qjVpn2D2T0pgfaSG0

Important
=========
Note if you are using an older raspbian build or previous Picamera python module
and images are black or have problems then update Raspberry PI firmware per commands.
From a (putty) ssh login or console terminal execute the following commands to upgrade
to latest firmware. This should resolve any picamera issues. It is advised
you use at least an 8 GB SD card

# Update Raspbian
sudo apt-get update
sudo apt-get upgrade

# Update RPI firmware
sudo rpi-update

# Hard boot to update firmware
sudo shutdown -h now

Unplug and restart your Raspberry Pi.

Quick Setup
===========
SSH (putty) or Desktop Terminal login to RPI and perform the following

cd ~
mkdir pi-timolo (or a folder name of your choice)
cd ./pi-timolo
wget https://raw.github.com/pageauc/pi-timolo/master/pi-timolo.tar
tar -pxvf pi-timolo.tar
# Install dependancies and required software
sudo ./setup-timolo.sh
# Initialize pi-timolo.py files, motion and test motion.
python ./pi-timolo.py
# Verify motion then ctrl-c to exit pi-timolo.py
# Edit config.py file using nano editor to change any desired settings per comments.
# ctrl-x y to Save
nano config.py
# test edit changes.
sudo ./pi-timolo.py

# If want to mount your web based google drive to a local RPI folder
# execute the setup-gdrivefs.sh script and follow instructions
sudo ./setup-gdrivefs.sh

If you want to run pi-timolo.sh headless on boot
See details below for setting up run init.d, crontab, rsync Etc.
          
Program Features
================
- Time lapse and motion detection can be run together or separately
- configuration variables are saved in a config.py file.  This allows
  pi-timolo.py to be updated without having to redo variable values.
  This also allows swapping in different saved configurations.   
- Auto detects day, night and twilight changes without using a clock.
- Image date/time and name can be put directly on images. Position and color
  can be specified.
- Night motion and images use low light long exposure
- Include a makemove.py script to help create timelapse avi files from images.
- Includes mvleavelast.sh script to move all but last file (since may still be active)
  This allows files to be moved to a folder mount point on a remote share if required.
- Includes a setup-timolo.sh script to install/update pi-timolo dependencies.
- Includes a skeleton init.d script pi-timolo.sh if you want to start the program on boot
- Allows logging of summary data to a file or detailed verbose data when enabled   
- Include setup-gdrivefs.sh to mount your google drive to a RPI folder. This script
  includes instructions.
  use rsync to sync files between local and google mount folders
  eg 
cd /home/pi/pi-timolo
rsync -vrtu motion gdrivefs/motion


Background
==========
I have been working on a grive capable security camera using two types of
security camera cases. One is a small fake plastic security cam case
from Amazon.  Model A or B fits inside with wifi only.
http://www.amazon.com/gp/product/B004D8NZ52/ref=oh_details_o01_s00_i00?ie=UTF8&psc=1
Here is a larger aluminum camera case that I have a model B installed in.  
This one has room for a usb power supply etc.
http://www.amazon.com/Monoprice-108431-Outdoor-Camera-Switchable/dp/B007VDTTTM/ref=sr_1_72?ie=UTF8&qid=1393884556&sr=8-72&keywords=fake+security+camera
I may do a YouTube video on How To setup these cases with the
raspberry pi computer and camera module installed.

After some work I now have the Raspberry Pi security camera's working
efficiently from a software point of view. The current configuration uses
the pi-timolo.py script to save files to a number sequence or a date-time
sequence. I also added some code to optionally put date/time information
directly on the photo images. This is convenient to see the exact time stamp
that the photo was taken. 
Using number sequencing allows limiting the number of files that need to
get synchronized to my google drive. 
It was too much to manage all the dated files and cleanup in google drive.  
This method restricts the number of motion files that need to get updated
via the GDriveFS. It is suggested you setup a cron rsync script.
  
The pi-timolo.tar file is a complete setup including instructions.
To automate the camera operation, I have setup pi-timolo.py to run from
a /etc/init.d/pi-timolo.sh bash script by copying /etc/init.d/skeleton file
to pi-timolo.sh script (sample included).

Prerequisites
=============
You must have a raspberry pi model A, A+, B or B+ with the latest raspbian build
and pi camera module installed and working. There are several tutorials
showing how to do this so it is not covered here. This assumes you know 
how to cut and paste into nano or similar text editor on the pi using
ssh (putty). You also need an operational internet connection via wifi
or wired connection. Wifi needs to be setup to work on boot with no desktop in
order for the camera to sync unattended with your google drive.  
I have written the pi-timolo python script and bash sync scripts to make it
somewhat independent of the folder names etc. This minimizes hard coding
folder names in the scripts. If you run the script manually from the
command line then settings and activity information can be enabled to display.

Download and Setup Instructions
===============================
Use putty to ssh into an internet connected raspberry pi and execute the
following commands. Note change pi-timoloto a folder name of your choice
if required.

sudo apt-get update
cd ~
mkdir pi-timolo
cd ./pi-timolo

# Download pimotion.tar file from my github account from a logged in
# ssh using putty or desktop terminal session on your raspberry pi.

wget https://raw.github.com/pageauc/pi-timolo/master/pi-timolo.tar

# Extract tar files to current folder

tar -pxvf pi-timolo.tar
sudo ./setup-timolo.sh

# If you wish to run GDriveFS to allow mounting your web based
# google drive to a local RPI folder then run setup command below
# This also include setup and security configuration instructions
# Note this will take a while so be patient

sudo ./setup-gdrivefs.sh 

Change pi-timolo.py settings as required
========================================
The script allows the use of a number sequence to restrict
the total number of files that need to get sync'd to my google drive
using grive.  Currently set to 500 images 
Please note this includes PIL imageFont and imageDraw python modules to
optionally put a date-time stamp on each images.
Make sure you are in the correct folder containing pi-timolo.py

pi-timolo.py reads configuration variables from a config.py file. If
you have different configurations you can keep a template library and
swap new settings in as needed.  There is a config-templates folder
with a few typical settings. You can copy cp the required files
to overwrite the existing config.py if required.  Make sure you
save a copy of the config.py if you need to save those settings.

nano config.py

Use nano editor to modify any pi-timolo.py script settings as required 
eg Threshold, Sensitivity, image prefix, numbering range, etc. 
See code comments for details.
I have one of my pi-timolo.py camera image settings set to flipped due to the
camera module mounting position in the fake security camera case. 
Review the various config.py settings and edit as desired.
use ctrl-x to save file and exit nano editor.

Note:
=====
I also setup a cronjob to reboot the rpi once a day but this may not be
necessary for you. I did it since I intend to leave the rpi security camera
run remotely and this gives a chance for system to recover should there
be a glitch. Also if you have problems check permissions.
The init.d will run as root so the files in the motion folder will
be owned by root.  
Just check to make sure you run with sudo ./pi-timolo.sh and sudo ./sync.sh
if you are in terminal sessions. Once you know sync.sh is working OK you 
can automate the sync by running it in as a cronjob.

Setup init.d script to auto launch pi-timolo.py on boot-up of raspberry pi
==========================================================================
Note there is a copy of the init.d pi-timolo.sh in the tar file so you should
be able to copy if instead of the skeleton file method below if you wish 
eg in the pimotion folder execute the following then skip to edit 
/etc/init.d/pi-timolo.sh using nano.

sudo cp pi-timolo.sh /etc/init.d

Check permissions for the /etc/init.d/pi-timolo.sh to make sure it is executable  
if required change permissions for pi-timolo.sh using chmod command 

ls -al /etc/init.d/pi-timolo.sh

cd /etc/init.d
chmod +x pi-timolo.sh
sudo nano pi-timolo.sh
   
# Change appropriate entries to point to your pi-timolo.py script and save
# the file using ctrl-x

sudo update-rc.d pi-timolo.sh defaults
cd ~

Reboot RPI and test operation by triggering motion and checking images are
successfully saved to your motion folder.  
Trouble shoot problems as required.

Good Luck
Claude Pageau 
