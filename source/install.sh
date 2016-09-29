#!/bin/sh
# Convenient speed2 install.sh script written by Claude Pageau 1-Jul-2016
ver="2.2"
echo "-------------------------------------------------------------"
echo "      pi-timolo Install.sh script ver $ver"
echo "Install or Upgrade pi-timolo Pi, Timelapse, Motion, Low Light"
echo "-------------------------------------------------------------"
echo "1 - Create folder /home/pi/pi-timolo"
cd ~
mkdir -p pi-timolo
cd ~/pi-timolo
pwd
echo "Done"
echo "-------------------------------------------------------------"
echo "2 - Downloading pi-timolo github repo files"
if [ -e config.py ]; then
  if [ ! -e config.py.orig ]; then
     echo "Save config.py to config.py.orig"
     cp config.py config.py.orig
  fi
  echo "Backup config.py to config.py.prev"
  cp config.py config.py.prev  
fi
wget -O config.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py
if [ $? -ne 0 ] ;  then
  wget -O config.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py
  wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py
  wget -O pi-timolo.sh https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.sh
  wget -O Readme.md https://raw.github.com/pageauc/pi-timolo/master/Readme.md
  wget -O install.sh https://raw.github.com/pageauc/pi-timolo/master/source/install.sh
  wget -O sync.sh https://raw.github.com/pageauc/pi-timolo/master/source/sync.sh
  wget -O webserver.py https://raw.github.com/pageauc/pi-timolo/master/source/webserver.py
  wget -O makedailymovie.sh https://raw.github.com/pageauc/pi-timolo/master/source/makedailymovie.sh
  wget -O makemovie.sh https://raw.github.com/pageauc/pi-timolo/master/source/makemovie.sh
  wget -O mvleavelast.sh https://raw.github.com/pageauc/pi-timolo/master/source/mvleavelast.sh
  wget -O myip.sh https://raw.github.com/pageauc/pi-timolo/master/source/myip.sh
  wget -O gdrive https://raw.github.com/pageauc/pi-timolo/master/source/gdrive
else
  wget -O config.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py
  wget -O pi-timolo.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py
  wget -O pi-timolo.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.sh
  wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/Readme.md
  wget -O install.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/install.sh
  wget -O sync.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/sync.sh
  wget -O webserver.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.py
  wget -O makedailymovie.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/makedailymovie.sh
  wget -O makemovie.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/makemovie.sh
  wget -O mvleavelast.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/mvleavelast.sh
  wget -O myip.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/myip.sh
  wget -O gdrive -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/gdrive
fi  
echo "Done"
echo "-------------------------------------------------------------"
echo "3 - Make required Files Executable"
chmod +x *py
chmod -x config.py
chmod +x *sh
if [ -e setup-timolo.sh ]; then
  rm setup-timolo.sh
fi
echo "Done"
echo "-------------------------------------------------------------"
echo "4 - Performing Raspbian System Update"
sudo apt-get -yq update
echo "Done"
echo "-------------------------------------------------------------"
echo "5 - Performing Raspbian System Upgrade"
sudo apt-get -yq upgrade
echo "Done"
echo "-------------------------------------------------------------"
echo "6 - Installing pi-timolo Dependencies"
sudo apt-get install -yq python-picamera python-imaging dos2unix python-pyexiv2 libav-tools
sudo apt-get install -yq fonts-freefont-ttf # Required for Jessie Lite Only
echo "Done"
if [ -e gdrive ]; then
  echo "-------------------------------------------------------------"
  echo "7 - Installing latest gdrive to /usr/local/bin/gdrive"
  sudo chmod +x gdrive
  sudo cp gdrive /usr/local/bin
  /usr/local/bin/gdrive | grep version
  echo "Done"
else
  echo "Error - Could not find gdrive file in current folder.  Please investigate ..."
  echo "        pi-timolo syncing feature will not be available."
fi
echo "-------------------------------------------------------------"
echo "8 - Installation Complete."
echo "-------------------------------------------------------------"
echo "See Readme.md for pi-timolo Program"
echo "Requirements, Configuration and Setting up gdrive security token"
echo
echo "Note:"
echo "1 - Reboot RPI if there are significant Raspbian system file updates."
echo "2 - If config.py already exists then old file named config.py.prev"
echo "3 - Check pi-timolo variable settings in config.py. See comments for details."
echo "    cd ~/pi-timolo"
echo "    nano config.py"
echo "    ctrl-x y to save and quit nano editor"
echo "4 - To start pi-timolo perform the following while in the pi-timolo folder"
echo "    ./pi-timolo.py"
echo
echo "Good Luck Claude" 
