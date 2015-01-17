                                 pi-timolo
  Raspberry (Pi) (Ti)me Lapse, (Mo)tion Detect using (Lo)w Light Settings
  ------------------------------------------------------------------------

Note regarding Version 2.2
--------------------------
This version fixes a bug that caused motion capture to go into a continuous loop
after forceTimer triggered. Also this version greatly simplifies the previous
convoluted checkIfDay() logic and is much simpler. I still need to do a bit of
code clean up. Note the sunriseThreshold and nightDayTimer variables are no
longer used. The sunset threshold is used and sets the day pixel average threshold
and may need to be tuned slightly higher or lower.  Currently I have full daylight
setting at 90 and lower lighting conditions during the day set to approx 55.
Claude ...
  
Introduction
------------
This is a picamara python module application using a Raspberry PI with a RPI camera
module. Use for Long Duration Time Lapse and/or Motion Detection projects.  
File names can be by Number Sequence or by Date/Time Naming.  Time Lapse and Motion
image files can be named and save images to different folders or the same folder.  
Optionally motion files can be uploaded to your web based google drive using a
precompiled (github) grive binary. (requires security setup).
The program uses low light long exposure for night motion and/or timelapse images.
The program can detect motion during low light, although the long exposure times
can cause blurring of moving objects.

This application uses the picamera python module and requires the latest
RPI firmware and updates to work properly.

Important
---------
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
-----------
SSH (putty) or Desktop Terminal login to RPI and perform the following

cd ~
mkdir pi-timolo (or a folder name of your choice)
cd ./pi-timolo
wget https://raw.github.com/pageauc/pi-timolo/master/pi-timolo.tar
tar -pxvf pi-timolo.tar
# Install dependancies and required software
sudo ./setup.sh
# Initialize pi-timolo.py files, motion and test motion.
python ./pi-timolo.py
# Verify motion then ctrl-c to exit pi-timolo.py
# Edit pi-timolo.py to change any desired settings per comments. ctrl-x to Save
nano pi-timolo.py
# test edit changes. ctrl-c to exit pi-timolo.py
python ./pi-timolo.py

See details below for setting up run at boot init.d, crontab, grive sync Etc.
          
Upgrade History
---------------
12-Dec This is a total rewrite and combines my previous pimotion, pimotion-orig and
my long duration rpi-timelapse projects into one program.  Motion and long duration
timelapse features can be run separately or together.  

Program Features
----------------
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
- Include precompiled grive for transferring files to your web based google drive.
  This allows syncing files for viewing on web browser or google drive app (android or ios)
- Includes a setup.sh script to install/update dependencies.
- Includes a skeleton init.d script pi-timolo.sh if you want to start the program on boot
- Allows logging of summary data to a file or detailed verbose data when enabled 


Background
----------
I have been working on a grive capable security camera using two types of
security camera cases. One is a small fake plastic security cam case
from Amazon.  Model A or B fits inside with wifi only.
http://www.amazon.com/gp/product/B004D8NZ52/ref=oh_details_o01_s00_i00?ie=UTF8&psc=1
Here is a larger aluminum camera case that I have a model B installed in.  
This one has room for a usb power supply etc.
http://www.amazon.com/Monoprice-108431-Outdoor-Camera-Switchable/dp/B007VDTTTM/ref=sr_1_72?ie=UTF8&qid=1393884556&sr=8-72&keywords=fake+security+camera
I may do a youtube video on How To setup these cases with the
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
via grive. Files are overwritten in Round robin fashion. If you need more
history you can write a routine to save google drive files from a
synchronized PC folder to a dated archive folder using a windows 
robocopy freefilesync or similar program through a batch file.
Synchronization uses a rpi compiled version of grive.  
This requires slightly modifying the source code to make it
compatible with the RPI.
  
The tar file is a complete setup including a precompiled grive to reduce the
effort required to get this working. To automate the security camera
operation, I have setup pi-timolo.py to run from a /etc/init.d/pi-timolo.sh
bash script by copying /etc/init.d/skeleton file to pi-timolo.sh script (sample included).
Then modified to run your pi-timolo.py script on boot. see later in post
for more setup detail.

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
-------------------------------
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

# Install required grive libraries from the internet
# Note this will take a while so be patient

sudo ./setup.sh 

Change pi-timolo.py settings as required
---------------------------------------
The script allows the use of a number sequence to restrict
the total number of files that need to get sync'd to my google drive
using grive.  Currently set to 500 images 
Please note this includes PIL imageFont and imageDraw python modules to
optionally put a date-time stamp on each images.
Make sure you are in the correct folder containing pi-timolo.py

pi-timolo.py reads configuration variables from a config.py file. If
you have different configurations you can keep a template library and
swap new settings in as needed.  There is a config-templates folder
with various typical settings. You can copy cp the required files
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

Details if you wish to compile grive yourself (Optional)
--------------------------------------------------------
You will need to download the tar file from the web link below and extract
it on your raspberry pi or compile a modified version of grive in order to
sync files to your google drive see instructions from url link below.  
Compiling takes a little while and you must edit the specified
/home/pi/grive/libgrive/src/drive/State.cc file per the web link below. 
If you have problems read the posts.  When you initialize grive with google
I opened a (putty) ssh session to the raspberry pi on my windows 7 PC and
then cut and pasted the grive -a url to chrome browser while logged
into google.  This takes you to a screen that returns a very
long security code.  I then cut and pasted this into the RPI session and
everything worked just fine.  I did not login to google on the pi.  
I only needed the PC to be logged in and paste the authentication code back
to the pi from the PC.  I don't think you need a logged in google account
on the pi as the post mentions.  At any rate it worked for me and I had to 
try several times since I was trying to avoid having grive executable in the
motion folder.  By using the -p option and copying the grive hidden
config files to the rpi motion folder I managed to get everything to work.
   
http://raspberrywebserver.com/serveradmin/back-up-your-pi-to-your-google-drive.html

or this link might be even better

http://www.pihomeserver.fr/en/2013/08/15/raspberry-pi-home-server-synchroniser-le-raspberry-pi-avec-votre-google-drive/

Once compile is successful copy the grive executable to the folder where
pi-timolo.py and sync.sh are located

Optional Setup grive security to your google account
----------------------------------------------------
If you want to synchronize image files to your google drive then follow the
instructions below
Note you must have a valid google account and google drive.
On a PC open a web browser eg chrome and login to your google account and
check that you have a google drive.

Important
---------
It is highly recommended that any web google drive documents you have be
moved to a separate google drive folder eg my_files.
This will prevent these files from getting sync'd back to the Raspberry Pi.
Moving your web google drive documents can be done from a web browser.

Initialize grive (Optional)
The operations below can be done using a (putty) ssh session from a
networked computer or directly from a RPI desktop terminal session and
a RPI web browser (eg Midori or Epiphany). Just make sure you are logged into
web google account before you start.
Note: running setup.sh on the RPI will also show detailed instructions
for setting up grive security token.

cd ~
cd pi-timolo   # or name of folder you created (modify subsequent paths accordingly)
sudo ./grive -a

or execute ./setup.sh for detailed security setup instructions.

This will display a web browser url.
You will need to highlight the displayed url on the RPI and paste into
the PC or RPI web browser URL bar. 
Note if you are using putty ssh then right click to paste RPI highlighted
url into the PC's web browser url bar 
The url will open a new web page and display a security hash token.  
Copy and paste this security token into grive via ssh session on rpi. 
In the grive -a session hit enter to accept the security token.
grive will indicate if the operation was successful

If you previously ran pi-timolo.py then a motion folder should already
be created under the pi-timolo folder (or whatever folder you picked)
If it does not exist run command below to create one.

./pi-timolo.py

or create motion or manually using mkdir command if desired.

Once grive has been initialized successfully with the grive -a option then
copy the /home/pi/pi-timolo/.grive and /home/pi/pi-timolo/.grive_state files to the
/home/pi/pi-timolo/motion folder or your folder name per above code. 
This will allow grive to be executed from the /home/pi/pi-timolofolder so it
does not have to be in the motion folder.

cd ~
cd pi-timolo
sudo cp ./.grive motion
sudo cp ./.grive_state motion
sudo ./sync.sh

You should see grive handshake with your google account and synchronize
files both ways between google and the RPI

Test pi-timolo.py and sync.sh together
-------------------------------------
To test you can launch pi-timolo.py from one ssh session and sync.sh from a
second ssh terminal session. 
Note: This can also be done from the RPI desktop using two terminal sessions.

First terminal session
----------------------
cd ~
cd pi-timolo # or whatever folder name you used.
sudo ./pi-timolo.py

Second terminal session
-----------------------
From a second ssh terminal run sync.sh (make sure that motion was detected
and files are in the motion folder to sync).  
You should see a /home/pi/pi-timolo/sync.lock file.  This is created by
pi-timolo.py when motion photos were created.

cd ~
cd pi-timolo # or whatever folder name you used.
sudo ./sync.sh

You should see files being synchronized in both directions.  This is normal.  
There are google drive apps for Apple, Android, Mac and PC.  Just do a
search for google drive in the appropriate app/play store This will allow you
to access your google drive on the web to view the raspberry pi 
motion capture security camera images You can also download and install the
google drive windows application to your PC.
Make sure you have a wifi or wired network connection to the internet that
will start when the RPI boots headless. 
see setup for crontab and init.d setup for further details
pymotion.py should start automatically and save images to the motion
folder. When the crontab is executed it will initiate a sync of images to your
google drive on the web.  
 
Note:
-----
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
-------------------------------------------------------------------------
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

Optional  (Only if you have setup grive security)
Create a crontab to automate syncronization to motion from the RPI
------------------------------------------------------------------------
From an logged in ssh or terminal session

sudo crontab -e

Paste the following line into the crontab file nano editor and modify
folder name and frequency if required. currently executes every minute. 

*/1 * * * * /home/pi/pi-timolo/sync.sh >/dev/nul

ctrl-x to exit nano and save crontab file
This cron job will run once a minute.  You can change to suit your needs.  
If grive is already running or there are no files to process then the
script simply exits. 
Also if grive has been running for more than 5 minutes it is killed.  
This can be changed in the script if you wish.

Reboot RPI and test operation by triggering motion and checking images are
successfully transmitted to your motion and optionally sync'd with your
google drive on the internet.  
Trouble shoot problems as required.

Good Luck
Claude Pageau 
