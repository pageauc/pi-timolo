#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="3.21"
TIMOLO_DIR='pi-timolo'  # Default folder install location

cd ~
if [ -d "$TIMOLO_DIR" ] ; then
  STATUS="Upgrade"
  echo "Upgrade rpi-speed-camera files"
else  
  echo "New rpi-speed-camera Install"
  STATUS="New Install"
  mkdir -p $TIMOLO_DIR
  echo "$TIMOLO_DIR Folder Created"
fi 

cd $TIMOLO_DIR
INSTALL_PATH=$( pwd )

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "-------------------------------------------------------------"
echo "      pi-timolo Install.sh script ver $ver"
echo "Install or Upgrade pi-timolo Pi, Timelapse, Motion, Low Light"
echo "-------------------------------------------------------------"
echo "1 - Downloading pi-timolo github repo files"
echo ""
if [ -e config.py ]; then
  if [ ! -e config.py.orig ]; then
     echo "Save config.py to config.py.orig"
     cp config.py config.py.orig
  fi
  echo "Backup config.py to config.py.prev"
  cp config.py config.py.prev
else
  wget -O config.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py     
fi
wget -O config_new.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py
if [ $? -ne 0 ] ;  then
  wget -O config_new.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py
  wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py
  wget -O pi-timolo.sh https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.sh  
  wget -O pi-timolo-install.sh https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh
  wget -O Readme.md https://raw.github.com/pageauc/pi-timolo/master/Readme.md
  wget -O sync.sh https://raw.github.com/pageauc/pi-timolo/master/source/sync.sh
  wget -O webserver.py https://raw.github.com/pageauc/pi-timolo/master/source/webserver.py
  wget -O webserver.sh https://raw.github.com/pageauc/pi-timolo/master/source/webserver.sh  
  wget -O convid.sh https://raw.github.com/pageauc/pi-timolo/master/source/convid.sh  
  wget -O makevideo.sh https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.sh
  wget -O mvleavelast.sh https://raw.github.com/pageauc/pi-timolo/master/source/mvleavelast.sh
  wget -O myip.sh https://raw.github.com/pageauc/pi-timolo/master/source/myip.sh
  wget -O gdrive https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
else
  wget -O pi-timolo.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py
  wget -O pi-timolo.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.sh
  wget -O pi-timolo-install.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh  
  wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/Readme.md
  wget -O sync.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/sync.sh
  wget -O webserver.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.py
  wget -O webserver.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.sh 
  wget -O convid.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/convid.sh 
  wget -O makevideo.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.sh
  wget -O mvleavelast.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/mvleavelast.sh
  wget -O myip.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/myip.sh
  wget -O gdrive -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
fi  
echo "Done Download"
echo "-------------------------------------------------------------"
echo "2 - Make Required Files Executable"
echo ""
chmod +x *py
chmod -x config*py
chmod +x *sh
echo "Done Permissions"
echo "-------------------------------------------------------------"
# check if system was updated today
NOW="$( date +%d-%m-%y )"
LAST="$( date -r /var/lib/dpkg/info +%d-%m-%y )"
if [ "$NOW" == "$LAST" ] ; then
  echo "4 Raspbian System is Up To Date"
  echo ""  
else
  echo "3 - Performing Raspbian System Update"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y update
  echo "Done Update"
  echo "-------------------------------------------------------------"
  echo "4 - Performing Raspbian System Upgrade"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y upgrade
  echo "Done Upgrade"
fi  
echo "------------------------------------------------"
echo ""  
echo "5 - Installing pi-timolo Dependencies"
echo ""
sudo apt-get install -yq python-picamera python-imaging dos2unix python-pyexiv2 libav-tools
sudo apt-get install -yq gpac   # required for MP4Box video converter
sudo apt-get install -yq fonts-freefont-ttf # Required for Jessie Lite Only
if [ -e gdrive ]; then
  echo "-------------------------------------------------------------"
  echo "6 - Install Latest gdrive to /usr/local/bin/gdrive"
  echo ""
  sudo chmod +x gdrive
  sudo cp gdrive /usr/local/bin
  /usr/local/bin/gdrive | grep version
  echo "Done gdrive Install"
else
  echo "Error - Could not find gdrive file in current folder.  Please investigate ..."
  echo "        pi-timolo syncing feature will not be available."
fi

cd $DIR
# Check if pi-timolo-install.sh was launched from pi-timolo folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -e 'pi-timolo-install.sh' ]; then
    echo "$STATUS Cleanup pi-timolo-install.sh"
    rm pi-timolo-install.sh
  fi
fi

if [ -e 'install.sh' ]; then
  echo "$STATUS Delete Old install.sh"
  rm install.sh
fi

if [ -e 'makemovie.sh' ]; then
  echo "$STATUS Delete Old makemovie.sh"
  rm makemovie.sh
fi

if [ -e 'makedailymovie.sh' ]; then
  echo "$STATUS Delete Old makedailymovie.sh"
  rm makedailymovie.sh
fi

echo "Done Dependencies"
echo "-----------------------------------------------"
echo "7 - $STATUS Complete"
echo "-----------------------------------------------"
echo ""
echo "See Readme.md for pi-timolo Program"
echo "Requirements, Configuration and Setting up gdrive security token"
echo
echo "Note:"
echo "1 - Reboot RPI if there are significant Raspbian system updates."
echo "2 - If config.py already exists then old file named config.py.prev"
echo "3 - Check pi-timolo variable settings in config.py. See comments for details."
echo "    cd ~/pi-timolo"
echo "    nano config.py"
echo "    ctrl-x y to save and quit nano editor"
echo "4 - To Run pi-timolo perform the following in SSH or terminal session"
echo ""
echo "    cd ~/pi-timolo"
echo "    ./pi-timolo.py"
echo ""
echo "-------------------------------------------------------------"
echo "See Readme.md or GitHub wiki for Further Details"
echo ""
echo "IMPORTANT"
echo "makemovie.sh and makedailymovie.sh have been deleted"
echo "They are Now Replaced by makevideo.sh"
echo "For makevideo.sh usage see GitHub wiki"
echo "at https://github.com/pageauc/pi-timolo/wiki/Utilities"
echo $TIMOLO_DIR "Good Luck Claude ..."
echo "Bye"

