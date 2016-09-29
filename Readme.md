# pi-timolo
### Raspberry (Pi) - (Ti)melapse, (Mo)tion, (Lo)wlight

For easy pi-timolo install onto raspbian RPI. 

    curl -L https://raw.github.com/pageauc/pi-timolo/master/source/install.sh | bash

From a computer logged into the RPI via ssh(Putty) session use mouse to highlight command above, right click, copy.  
Then select ssh(Putty) window, mouse right click, paste.  The command should 
download and execute the github install.sh script for pi-timolo.

pi-timolo is a python picamara module application for a Raspberry PI computer.
A RPI camera module must be attached. It can take timelapse and motion detection
images separately or together. Takes Long exposure Night (lowlight) images for
Time Lapse and/or Motion. Has smooth twilight transitions based on a threshold light
setting, so a real time clock is not required. Customization settings are saved in a config.py file.
The application is primarily designed for headless operation and include sync.sh that
can securely synchronize files with a users google drive.  This works well for remote security
cameras.  

### For Details See [pi-timolo Wiki](https://github.com/pageauc/pi-timolo/wiki) and [YouTube Videos](https://www.youtube.com/playlist?list=PLLXJw_uJtQLa11A4qjVpn2D2T0pgfaSG0)
        
Good Luck
Claude Pageau 
