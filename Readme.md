# pi-timolo
### Raspberry (Pi) - (Ti)melapse, (Mo)tion, (Lo)wlight
### Wiki https://github.com/pageauc/pi-timolo/wiki     
YouTube Videos https://www.youtube.com/playlist?list=PLLXJw_uJtQLa11A4qjVpn2D2T0pgfaSG0

**NEW Release 5.0** with optional video stream thread, improved day/night transitions with no greenish images + Misc updates
**NEW Release 6.0** with optional DateTime Named subfolders, recent files option and Disk Space Management + Misc updates 
**NEW Release 6.7** with videoRepeat option to take continuous video clips by filename datetime or seq num and exit by specified time or number of videos or run continuous and manage by freedisk space..  This is similar to a dash cam.  Requires the updated config.py.
**See Minimal Upgrade Below**

### Description
pi-timolo is a python picamara module application for a Raspberry PI computer (RPI).
A RPI camera module must be attached. pi-timolo can take timelapse and motion detection
images/videos, separately or together. Takes Long exposure Night (lowlight) images for
Time Lapse and/or Motion. Has smooth twilight transitions based on a threshold light
setting, so a real time clock is not required. Customization settings are saved in a config.py and conf files.
The application is primarily designed for headless operation and includes sync.sh that
can securely synchronize files with a users google drive.  This works well for remote security
cameras. Camera config.py settings can be administered remotely from a google drive using sync.sh.
Includes makevideo.sh to create timelapse or motion lapse videos from images, convid.sh to convert/combine 
h264 to mp4 format, a simple minumum or no setup web server to view images or videos and menubox.sh 
to admin settings and stop start pi-timolo and webserver as background tasks.
        
***NEW*** - Added two config.py templates config.py.stream uses video streaming thread (best with quad core) config.py.default
uses normal picamera image capture for motion detection and is less resource intensive for single core RPI's    
Make a backup of config.py then Copy a template over the original config.py per example below   

    cd ~/pi-timolo.py
    cp config.py config.py.bak
    cp config.py.stream config.py
    
***Note:*** use nano to reinstate any customized settings

see Github Wiki for More Details https://github.com/pageauc/pi-timolo/wiki    
 
### Quick Install
For Easy pi-timolo-install.sh onto raspbian RPI. 

    curl -L https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh | bash

From a computer logged into the RPI via SSH(Putty) or desktop terminal session  
* Use mouse to highlight curl command above, right click, copy.  
* Select RPI SSH(Putty) window, mouse right click, paste.   
The command will download and execute the GitHub pi-timolo-install.sh script   

**IMPORTANT** - A raspbian apt-get update and upgrade will be performed as part of install
so it may take some time if these are not up-to-date       

### Minimal Upgrade
If you are just interested in a minimal upgrade (must have pi-timolo previously installed)
from a logged in ssh or terminal session execute the following commands.  

    cd ~/pi-timolo
    cp config.py config.py.old
    wget -O config.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py
    wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py    
    
Edit config.py to transfer any customized settings from config.py.old  
    
### or Manual Install   
From logged in RPI SSH session or console terminal perform the following. You can review
the pi-timolo-install.sh script code before executing.

    cd ~
    wget https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh
    chmod +x pi-timolo-install.sh
    ./pi-timolo-install.sh
    
### Run pi-timolo 
Default is motion only see config.py for detailed settings   
    
    cd ~/pi-timolo
    ./pi-timolo.py   
 
### Menubox
The lastest version of pi-timolo has a whiptail admin menu system. The menu's allow
start/stop of pi-timolo.py and webserver.py as background tasks, as well as
editing configuration files, making timelapse videos from jpg images, converting or joining mp4 files Etc.    
To run from ssh console or terminal session.

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
