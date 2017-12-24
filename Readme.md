# pi-timolo
### Raspberry (Pi)camera, (Ti)melapse, (Mo)tion, (Lo)wlight
### For Details See [Wiki Instructions](https://github.com/pageauc/pi-timolo/wiki) and [YouTube Videos](https://www.youtube.com/playlist?list=PLLXJw_uJtQLa11A4qjVpn2D2T0pgfaSG0)

* ***NOTICE*** gdrive is no longer installed with pi-timolo-install.sh, I have been testing
rclone and it is now the default. See [Wiki - How to Setup Rclone](https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-rclone).
If ***/usr/local/bin/gdrive*** Exists, It Will Remain.   

### Quick Install
**IMPORTANT** - A raspbian apt-get update and upgrade will be performed as part of install
so it may take some time if these are not up-to-date.      

Step 1 Highlight curl command in code box below using mouse left button. Right click mouse in highlighted area and Copy.     
Step 2 On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.     

    curl -L https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh | bash

The command above will download and Run the GitHub pi-timolo-install.sh script. 
An upgrade will not overwrite configuration files.   

### Test Install
To Test Run default config.py - motion track(HD image) plus timelapse(5 min interval). 
 
    cd ~/pi-timolo
    ./pi-timolo.py

### For Detailed Instructions See [pi-timolo Wiki](https://github.com/pageauc/pi-timolo/wiki)

### Description
pi-timolo is a python 2/3 picamara module application for a Raspberry PI computer (RPI).
A RPI camera module must be attached. pi-timolo can take timelapse and motion detection
images/videos, separately or together. 

Takes Long exposure Night (lowlight) images for Time Lapse and/or Motion. Has smooth twilight transitions based on a threshold light
setting, so a real time clock is not required. Customization settings are saved in a config.py and conf files and optional special
purpose plugin config files.

The application is primarily designed for headless operation and includes sync.sh and rclone that
can securely synchronize files with a users remote storage service. This works well for remote security
cameras. Camera config.py settings can be administered remotely from a google drive using sync.sh.

Includes makevideo.sh to create timelapse or motion lapse videos from images, convid.sh to convert/combine 
h264 to mp4 format, a simple minumum or no setup web server to view images or videos and menubox.sh 
to admin settings and stop start pi-timolo and webserver as background tasks. Recently added
optional plugin feature that allows overlaying config.py settings with custom settings for
specific tasks.  
        
see Github Wiki for More Details https://github.com/pageauc/pi-timolo/wiki    

### Recent Release History
* Release 5.0 Added optional video stream thread, improved day/night transitions with no greenish images + Misc updates
* Release 6.0 Added optional DateTime Named subfolders, recent files option and Disk Space Management + Misc updates 
* Release 6.7 Added videoRepeat option to take continuous video clips by filename datetime or seq num and exit by
specified time or number of videos or run continuous and manage by freedisk space. This is similar to a dash cam. Requires the updated config.py.   
* Release 7.x Added openCV motion Tracking to track objects above a min size for a designated pixel track trigger length.
There is also a new motionTrackQuickPic feature that saves a stream image rather than switching to normal pi-camera non streaming mode.
RPI Forum Post details here https://www.raspberrypi.org/forums/viewtopic.php?p=1183663#p1183663   
* ***New Release 9.x*** Added Optional plugin Feature, made python3 compatible, Added rclone install and wiki
For plugins details see https://github.com/pageauc/pi-timolo/wiki/How-to-Use-Plugins
For rclone details see https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-rclone
For python3 Support Details see https://github.com/pageauc/pi-timolo/wiki/Prerequisites#python-3-support

**See Minimal Upgrade Below** if you have a recent pi-timolo version installed

### Minimal Upgrade
If you are just interested in a minimal upgrade (must have pi-timolo previously installed)
from a logged in ssh or terminal session execute the following commands.  

    cd ~/pi-timolo
    sudo apt-get install python-opencv
    cp config.py config.py.old
    cp pi-timolo.py pi-timolo.py.old
    wget -O config.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py
    wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py    
    
Edit config.py to transfer any customized settings from config.py.old  
    
### Manual Install   
From logged in RPI SSH session or console terminal perform the following. You can review
the pi-timolo-install.sh script code before executing.

    cd ~
    wget https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh
    chmod +x pi-timolo-install.sh
    ./pi-timolo-install.sh
    
### Menubox
pi-timolo has a whiptail administration menu system. The menu's allow
start/stop of pi-timolo.py and/or webserver.py as background tasks, as well as
editing configuration files, making timelapse videos from jpg images, converting or joining mp4 files Etc.    

To run menubox.sh from ssh console or terminal session execute commands below.

    cd ~/pi-timolo
    ./menubox.sh

![menubox main menu](menubox.png)
 
### Webserver
I have also written a standalone LAN based webserver.py to allow easy access to pi-timolo image and video files
on the Raspberry from another LAN computer web browser.  There is no setup required but the display
settings can be customized via variables in the config.py file or via menubox admin menuing.   
To run from ssh console or terminal session.
    
    cd ~/pi-timolo
    ./webserver.py

![webserver browser screen shot](webserver.png)
 
### Reference Links  
Detailed pi-timolo Wiki https://github.com/pageauc/pi-timolo/wiki  
YouTube Videos https://www.youtube.com/playlist?list=PLLXJw_uJtQLa11A4qjVpn2D2T0pgfaSG0
 
Good Luck
Claude Pageau 
