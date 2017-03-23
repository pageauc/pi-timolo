#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="4.4"
TIMOLO_DIR='pi-timolo'  # Default folder install location

cd ~
if [ -d "$TIMOLO_DIR" ] ; then
  STATUS="Upgrade"
  echo "Upgrade pi-timolo files"
else  
  echo "New pi-timolo Install"
  STATUS="New Install"
  mkdir -p $TIMOLO_DIR
  mkdir -p $TIMOLO_DIR/media
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
wget -O media/webserver.txt https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
if [ $? -ne 0 ] ;  then
  wget -O config.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py
  wget -O menubox.sh https://raw.github.com/pageauc/pi-timolo/master/source/menubox.sh  
  wget -O pi-timolo.py https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py
  wget -O pi-timolo.sh https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.sh  
  wget -O pi-timolo-install.sh https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh
  wget -O Readme.md https://raw.github.com/pageauc/pi-timolo/master/Readme.md
  wget -O sync.sh https://raw.github.com/pageauc/pi-timolo/master/source/sync.sh
  wget -O webserver.py https://raw.github.com/pageauc/pi-timolo/master/source/webserver.py
  wget -O webserver.sh https://raw.github.com/pageauc/pi-timolo/master/source/webserver.sh  
  wget -O convid.sh https://raw.github.com/pageauc/pi-timolo/master/source/convid.sh 
  wget https://raw.github.com/pageauc/pi-timolo/master/source/convid.conf 
  wget -O makevideo.sh https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.sh
  wget https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.conf 
  wget -O mvleavelast.sh https://raw.github.com/pageauc/pi-timolo/master/source/mvleavelast.sh
  wget -O myip.sh https://raw.github.com/pageauc/pi-timolo/master/source/myip.sh
  wget -O gdrive https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
else
  wget -O menubox.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/menubox.sh
  wget -O pi-timolo.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.py
  wget -O pi-timolo.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo.sh
  wget -O pi-timolo-install.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh  
  wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/Readme.md
  wget -O sync.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/sync.sh
  wget -O webserver.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.py
  wget -O webserver.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.sh 
  wget -O convid.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/convid.sh
  wget -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/convid.conf
  wget -O makevideo.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.sh
  wget -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.conf
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
sudo apt-get install -yq python-scipy  # New Dependency for enhanced motion detection
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
echo "Note:"
echo "1 - Reboot RPI if there are significant Raspbian system updates."
echo "2 - If config.py already exists then old file named config.py.prev"
echo "3 - Check pi-timolo variable settings in config.py per comments"
echo "    cd ~/pi-timolo"
echo "    nano config.py"
echo "    ctrl-x y to save and quit nano editor"
echo "4 - To Run pi-timolo perform the following in SSH or terminal session"
echo "    cd ~/pi-timolo"
echo "    ./pi-timolo.py"
echo "-------------------------------------------------------------"
echo "              IMPORTANT UPGRADE INFORMATION"
echo "1 - makemovie.sh and makedailymovie.sh have been deleted"
echo "    They are Now Replaced by makevideo.sh and convid.sh"
echo "2 - If this is an upgrade then config.py will be replaced."
echo "    If config.py.prev has webserver variables then you can"
echo "    cp config.py.prev config.py   to restore previous settings"
echo "    otherwise edit the existing config.py to restore prev settings"
echo "3 - A new menubox.sh has been added to make admin easier"
echo "4 - Variable settings are now stored in .conf files or config.py"
echo "    This allows upgrading without loosing settings"
echo "5 - motion, timelapse, video folder are now in media folder"
echo "6 - Existing config files will Not be overwritten.  New files will be"
echo "    .1, .2 etc or config.py new file will be config_new.py"
echo "------------------------------------------------------------------"
echo "For further details See Readme.md or GitHub wiki"
echo "here https://github.com/pageauc/pi-timolo/wiki"

if ! grep -q "web_server_root" config.py ; then
   cp config_new.py config.py
   echo ""   
   echo "IMPORTANT:  Your config.py has been Upgraded"
   echo "and Replaced with config_new.py"
   echo "Your previous settings are in config.py.prev"
fi
echo "====================================================="
if [ ! -e /usr/bin/mc ]; then
   echo "Do you want to install mc (Midnight Commander)"
   echo "Interactive Console File Manager"
   echo "Can utilize mouse/function keys in SSH sessions"
   echo ""
   read -p "Install Midnight Commander (y/n)?" choice
   case "$choice" in 
     y|Y ) echo "yes"
       sudo apt-get install mc
       echo "type mc to start";;
     n|N ) echo "no";;
     * ) echo "invalid";;
   esac
fi
echo $TIMOLO_DIR "Good Luck Claude ..."
echo "Bye"

