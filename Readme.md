# pi-timolo
### Raspberry (Pi) - (Ti)melapse, (Mo)tion, (Lo)wlight

### Quick Install
For Easy pi-timolo-install.sh onto raspbian RPI. 

    curl -L https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh | bash

#### or Manual Install   
From logged in RPI SSH session or console terminal perform the following.

    wget https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh
    chmod +x pi-timolo-install.sh
    ./pi-timolo-install.sh
    cd pi-timolo
    ./pi-timolo.py

NOTE - You may have to run sudo ./pi-timolo.py depending on permissions       
From a computer logged into the RPI via ssh(Putty) session use mouse to highlight command above, right click, copy.  
Then select ssh(Putty) window, mouse right click, paste.  The command should 
download and execute the github pi-timolo-install.sh script for pi-timolo program   
Note - a raspbian apt-get update and upgrade will be performed as part of install 
so it may take some time if these are not up-to-date

#### For Detailed Instructions See pi-timolo Wiki at https://github.com/pageauc/pi-timolo/wiki   

### Links

YouTube Videos https://www.youtube.com/playlist?list=PLLXJw_uJtQLa11A4qjVpn2D2T0pgfaSG0

### Description
pi-timolo is a python picamara module application for a Raspberry PI computer.
A RPI camera module must be attached. It can take timelapse and motion detection
images separately or together. Takes Long exposure Night (lowlight) images for
Time Lapse and/or Motion. Has smooth twilight transitions based on a threshold light
setting, so a real time clock is not required. Customization settings are saved in a config.py file.
The application is primarily designed for headless operation and include sync.sh that
can securely synchronize files with a users google drive.  This works well for remote security
cameras.  
        
Good Luck
Claude Pageau 
