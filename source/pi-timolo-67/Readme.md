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

### This version is superceded by the new version 7.x release located here https://github.com/pageauc/pi-timolo.
The new version uses opencv motion tracking.  You can still use this version by copying these files over an existing
recent version.

### To install version 6.7

Install into an existing pi-timolo install per the following.  From a logged in Putty SSH or terminal session execute the following.

    cd ~/pi-timolo
    cp pi-timolo.py pi-timolo.old
    cp config.py config.py.old
    wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-67/pi-timolo.py 
    wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-67/config.py     
    wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-67/config.py.default
    
    