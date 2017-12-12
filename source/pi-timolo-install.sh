#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="9.1"
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

if [ -e convid.conf.1 ]; then
  rm convid.conf.1
  rm makevideo.conf.1
fi

if [ -e convid.conf ]; then
  if [ ! -e convid.conf.orig ]; then
    echo "Backup convid.conf and makevideo.conf to .orig files"
    cp convid.conf convid.conf.orig
    cp makevideo.conf makevideo.conf.orig
  fi
fi

timoloFiles=("config.py" "menubox.sh" "pi-timolo.py" "pi-timolo.sh" \
"pi-timolo-install.sh" "sync.sh" "webserver.py" "webserver.sh" "rclone-install.sh" \
"convid.sh" "convid.conf" "makevideo.sh" "makevideo.conf" "mvleavelast.sh" "myip.sh" "plugins-install.sh")

for fname in "${timoloFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR - $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname https://raw.github.com/pageauc/pi-timolo/master/source/$fname
        fi
    fi
done

echo "Download Backup Files  Please Wait ..."
wget -O config_new.py -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py
if [ $? -ne 0 ] ;  then
    wget -O config_new.py https://raw.github.com/pageauc/pi-timolo/master/source/config.py
    wget -O config.py.default https://raw.github.com/pageauc/pi-timolo/master/source/config.py
    wget -O convid.conf.new https://raw.github.com/pageauc/pi-timolo/master/source/convid.conf
    wget -O Readme.md -q https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O makevideo.conf.new https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.conf
    wget -O gdrive https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
    wget -O media/webserver.txt https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
else
    wget -O config.py.default -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py.default
    wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O convid.conf.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/convid.conf
    wget -O makevideo.conf.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.conf
    wget -O gdrive -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
    wget -O media/webserver.txt -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
fi

echo "-------------------------------------------------------------"
echo "2 - Make Required Files Executable"
echo ""
chmod +x *py
chmod -x config*py
chmod +x *sh
dos2unix *sh
dos2unix *py
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
sudo apt-get install -yq python-picamera python3-picamera python-imaging dos2unix python-pyexiv2 libav-tools
sudo apt-get install -yq python-scipy  # New Dependency for enhanced motion detection
sudo apt-get install -yq gpac   # required for MP4Box video converter
sudo apt-get install -yq fonts-freefont-ttf # Required for Jessie Lite Only
sudo apt-get install -yq python-opencv

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

echo "-------------------------------------------------------------"
echo "7 - Install plugins"
echo ""
./plugins-install.sh

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

echo "Done Dependencies
-----------------------------------------------
7 - $STATUS Complete
-----------------------------------------------
Note:
1 - Reboot RPI if there are significant Raspbian system updates.
2 - If config.py already exists then old file is config.py.prev
3 - Check pi-timolo variable settings in config.py per comments
    cd ~/pi-timolo
    nano config.py
    ctrl-x y to save and quit nano editor
4 - To Run pi-timolo perform the following in SSH or terminal session
    cd ~/pi-timolo
    ./pi-timolo.py
-------------------------------------------------------------"

echo "              IMPORTANT UPGRADE INFORMATION
1 - makemovie.sh and makedailymovie.sh have been deleted
    They are Now Replaced by makevideo.sh and convid.sh
2 - If this is an upgrade then config.py will be replaced.
    and previous will be config.py.prev. If version is 4.30 or greater
    cp config.py.prev config.py to restore previous config.py
    otherwise you will need to edit the new config.py with your previous settings
    that are in the config.prev file.
3 - A new menubox.sh has been added to make admin easier
4 - Variable settings are now stored in .conf files or config.py
    This allows upgrading without loosing settings
5 - motion, timelapse, video folder are now in media folder
6 - Existing config files will Not be overwritten.  New files will be
    .1, .2 etc or config.py new file will be config_new.py
------------------------------------------------------------------
For further details See Readme.md or GitHub wiki
here https://github.com/pageauc/pi-timolo/wiki"

if ! grep -q "web_server_root" config.py ; then
   cp config_new.py config.py
   echo "
   IMPORTANT:  Your config.py has been Upgraded
   and Replaced with config_new.py
   Your previous settings are in config.py.prev"
fi
echo "====================================================="
if [ ! -e /usr/bin/mc ]; then
   echo "
   -----  Optional Install of Midnight Commander -----
   This is an Interactive Console File Manager
   It can utilize mouse/function keys in SSH session
   and makes managing local files on the RPI easier
   Another option is to use filezilla on a windows computer
   To Installing Midnight Commander execute command below.

       sudo apt-get install mc

   type mc to Run Midnight Commander"
fi
echo "Good Luck Claude ..."
echo "Bye"

