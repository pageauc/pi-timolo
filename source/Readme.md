# pi-timolo
##### Raspberry (Pi) - (Ti)me Lapse, (Mo)tion Detect (Lo)w Light

**Version 2.6 release notes**

- fixed bug that caused a hang when video mode was True
- Added a new quick time lapse after motion detected feature.
- cleaned up console display
- misc bug fixes
- Added gdrive binary for easy syncing of files with internet based google drive see https://github.com/odeke-em/drive/releases amd binary and https://github.com/odeke-em/drive for additional implementation details

**IMPORTANT**

The older config.py is NOT compatible with this release
since new variables have been added for quick timelapse feature


### Quick Setup
(assumes raspberry pi with RPI camera module installed and tested running updated raspbian
operating system installed on min 8gb SD card with expanded file system)

Use SSH (putty) or a Desktop Terminal login to RPI and perform the following.

Note if you are using an older raspbian build or previous Picamera python module,
and images are black or have problems then update Raspberry PI firmware per optional
firmware update command below.

From a (putty) ssh login or console terminal execute the following commands to upgrade
to latest firmware. This should resolve any picamera issues. Also it is advised
you use at least an 8 GB SD card with file system expanded using sudo raspi-config

Update Raspbian

    sudo apt-get update
    sudo apt-get upgrade

Update RPI firmware (optional: run if you are using older RPI firmware and having
problems with python picamera module errors or image quality issues)  

	sudo rpi-update

Hard boot to update firmware

	sudo shutdown -h now

Unplug and restart your Raspberry Pi.

Login and install pi-timolo

	cd ~
	mkdir pi-timolo
	cd ./pi-timolo
	wget https://raw.github.com/pageauc/pi-timolo/master/pi-timolo.tar
	tar -pxvf pi-timolo.tar
	sudo ./setup-timolo.sh
	python ./pi-timolo.py

Verify motion (per screen log entries) then ctrl-c to exit pi-timolo.py
Edit config.py file using nano editor to change any desired settings per comments.
ctrl-x y to Save

	nano config.py

Test edit changes.

	sudo ./pi-timolo.py
    

### Program Description

This is a python picamara module application for a Raspberry PI with a RPI camera
module. It is designed for Long Duration Time Lapse and/or Motion Detection projects.
I use mine for headless security cameras using the makedailymovie.sh to a remote NAS.
and also syncing to my google drive using gdrive.
File names can be by Number Sequence or by Date/Time Naming.  Time Lapse and Motion
image files can be named and saved to different folders or the same folder.  
Optionally motion files can be uploaded to your web based google drive using 
github program called gdrive (compiled binary included).
NOTE:
pi-timolo uses low light long exposure for night motion and/or timelapse images.
The program can detect motion during low light, although the long exposure times
can cause blurring of moving objects.

This application uses the picamera python module and requires recent Raspberry PI Raspbian
firmware and updates to work properly.
Here are some motion and time lapse sample YouTube videos

https://www.youtube.com/playlist?list=PLLXJw_uJtQLa11A4qjVpn2D2T0pgfaSG0

If you are looking for a good web based interactive RPI camera interface I would
highly recommend this application.  It is easy to install and works well. But I 
still prefer pi-timolo for remote headless camera situations.

http://elinux.org/RPi-Cam-Web-Interface

This interface can also be setup to use gdrive syncing.  Contact me if you need
details.

### Program Features

- Time lapse and motion detection can be run together or separately
- Configuration variables are saved in a config.py file. This allows 
  pi-timolo.py to be updated without having to redo variable values.
  This also allows swapping in different saved configurations.
- Auto detects day, night and twilight changes without using a clock.
  This is useful if the RPI reboots without an internet connection.
- Image date/time and name can be put directly on images. Position and color
  can be specified.
- Night motion and images use low light long exposure
- Includes a makemove.py script to help create timelapse avi files from images.
- Includes mvleavelast.sh script to move all but last file (since may still be active)
  This allows files to be moved to a folder mount point on a remote share if required.
- Includes a setup-timolo.sh script to install/update pi-timolo dependencies.
- Includes a skeleton init.d script pi-timolo.sh if you want to start the program on boot
- Allows logging of summary data to a file or detailed verbose data when enabled   
- Includes gdrive binary to sync files with your google drive using sync.sh script

  
### Background History

I have been working on a headless internet capable security camera using two types of
security camera cases. One is a small fake plastic security cam case
from Amazon.  Model A or B fits inside with wifi only.

http://www.amazon.com/gp/product/B004D8NZ52/ref=oh_details_o01_s00_i00?ie=UTF8&psc=1

Here is a larger aluminum camera case that I have a model B installed in.  
This one has room for a usb power supply etc.

http://www.amazon.com/Monoprice-108431-Outdoor-Camera-Switchable/dp/B007VDTTTM/ref=sr_1_72?ie=UTF8&qid=1393884556&sr=8-72&keywords=fake+security+camera

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

### Prerequisites

You must have a raspberry pi model A, A+, B, B+ or B-2 with the latest raspbian build
and a pi camera module installed and working. There are several tutorials
showing how to do this so it is not covered here. This assumes you know 
how to cut and paste into nano or similar text editor on the pi using
ssh (putty). You also need an operational internet connection via wifi
or wired connection. Wifi needs to be setup to work on boot with no desktop in
order for the camera to sync unattended with your google drive.  
I have written the pi-timolo python script and bash sync scripts to make it
somewhat independent of the folder names etc. This minimizes hard coding
folder names in the scripts. If you run the script manually from the
command line then settings and activity information can be enabled to display.

### Download and Setup Instructions

Use putty to ssh into an internet connected raspberry pi and execute the
following commands. Note change pi-timoloto a folder name of your choice
if required.

    sudo apt-get update
    cd ~
    mkdir pi-timolo
    cd ./pi-timolo

Download pimotion.tar file from my github account from a logged in
ssh using putty or desktop terminal session on your raspberry pi.

	wget https://raw.github.com/pageauc/pi-timolo/master/pi-timolo.tar

Extract tar files to current folder

	tar -pxvf pi-timolo.tar
	sudo ./setup-timolo.sh

A gdrive binary will be installed to /ur/local/bin as part of the setup.
This allows secure syncing of pi-timolo images with your google drive
using the sync.sh script.  The setup-timolo.sh script includes instructions
for configuring gdrive security

### Change pi-timolo.py settings as required

The script allows the use of a number sequence to restrict
the total number of files that need to get sync'd to my google drive
using gdrive.  Currently set to 500 images 
Please note this includes PIL imageFont and imageDraw python modules to
optionally put a date-time stamp on each images.
Make sure you are in the correct folder containing pi-timolo.py

pi-timolo.py reads configuration variables from a config.py file. If
you have different configurations you can keep a template library and
swap new settings in as needed. You can copy cp the required files
to overwrite the existing config.py if required.  Make sure you
save a copy of the config.py if you need to save those settings.

	nano config.py

Use nano editor to modify any pi-timolo.py script settings as required 
eg Threshold, Sensitivity, image prefix, numbering range, etc. 
See config.py code comments for details.
I have one of my pi-timolo.py camera image settings set to flipped due to the
camera module mounting position in the fake security camera case. 
Review the various config.py settings and edit as desired.
use ctrl-x to save file and exit nano editor.

Note:
I also setup a cronjob to reboot the rpi once a day but this may not be
necessary for you. I did it since I intend to leave the rpi security camera
run remotely and this gives a chance for system to recover should there
be a glitch. Also if you have problems check permissions.
The init.d will run as root so the files in the motion folder will
be owned by root.  
Just check to make sure you run with sudo ./pi-timolo.sh and sudo ./sync.sh
if you are in terminal sessions. Once you know sync.sh is working OK you 
can automate the sync by running it in as a cronjob.

### Setup init.d run on boot script

to auto launch pi-timolo.py on boot-up of raspberry pi
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
   
Change appropriate entries to point to your pi-timolo.py script and save
the file using ctrl-x

	sudo update-rc.d pi-timolo.sh defaults
	cd ~

Reboot RPI and test operation by triggering motion and checking images are
successfully saved to your motion folder.  
Trouble shoot problems as required.

### Setup google drive sync

To optionally install gdrive binary from source perform the following.

	cd /tmp
	wget https://github.com/odeke-em/drive/releases/download/v0.2.2-arm-binary/drive-arm-binary
	chmod +x drive-arm-binary
	sudo cp drive-arm-binary /usr/local/bin/gdrive
	cd ~
	gdrive version

Setup gdrive security for secure access to your google drive.
Note: This assumes you have a google drive with a google account eg gmail
and you are using a SSH terminal session logged into your Raspberry Pi computer
from a windows PC that has the Chrome browser installed and logged into your google account.
for additional details see https://github.com/odeke-em/drive

	cd ~
    cd pi-timolo
    sudo gdrive init
    
- This will display a long url in the RPI SSH session.
- use mouse left button to highlight the url (do NOT press enter)
- On the PC Chrome Browser window open a new tab and right click in the top url box
- Make sure you are logged into your google account eg gmail
- Right mouse click in the new tab url box and select paste and go
- This will display a google message to confirm access
- Accept and a security code box will be displayed
- Use left mouse to hightlight security code the right click and copy
- return to RPI SSH session and right click gdrive init prompt to paste security code
- Press enter to accept code. If OK no errors will be displayed.
- to confirm access to your google drive perform the following

	sudo gdrive ls
    
This should display the contents of your google drive root folder. 

If config.py has the motion setting createLockFile = True
then a pi-timolo.sync file will be created when motion images are created.
Check if a pi-timolo.sync file exists in the pi-timolo folder otherwise run

	sudo ./pi-timolo.py
    
and activate motion to create images and a new pi-timolo.sync file

run sync.sh script to test google drive syncing with specified local folder
default is ./motion

to run sync.sh executed the following

	sudo ./sync.sh

The sync.sh script will perform the following
- Checks if gdrive sync is already running.
- Runs gdrive only if it is not already running and Kills gdrive processes
if it has been running too long. default is > 600 seconds or 10 minutes
- Looks for pi-timolo.sync file created by pi-timolo.py indicating there are new files to sync
othewise is exits without attempting to resolve google drive files with specified local folder.
- If a pi-timolo.sync file exists then performs a gdrive push to sync local folder with the
specified google drive subfolder
- Reports if sync was successful or errors were encountered 

Suggest you run this script from a crontab every 5 minutes or so.  
Add appropriate line to crontab using command

	sudo crontab -e

Add example crontab entry per below then save and exit nano using ctrl-x y

	*/5 * * * * /home/pi/pi-timolo/sync.sh >/dev/nul


Good Luck
Claude Pageau 
