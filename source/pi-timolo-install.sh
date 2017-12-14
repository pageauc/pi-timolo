#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="9.5"
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
echo "$STATUS pi-timolo from github repo"
echo ""

if [ -f config.py ]; then
  if [ ! -f config.py.orig ]; then
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

if [ -f /usr/bin/rclone ]; then
  timoloFiles=("menubox.sh" "pi-timolo.py" "pi-timolo.sh" "pi-timolo-install.sh" \
"sync.sh" "webserver.py" "webserver.sh" "rclone-install.sh" \
"convid.sh" "makevideo.sh" "mvleavelast.sh" "myip.sh" "plugins-install.sh" "rclone-sync.sh")
else
  timoloFiles=("config.py" "menubox.sh" "pi-timolo.py" "pi-timolo.sh" \
"pi-timolo-install.sh" "sync.sh" "webserver.py" "webserver.sh" "rclone-install.sh" \
"convid.sh" "convid.conf" "makevideo.sh" "makevideo.conf" "mvleavelast.sh" "myip.sh" "plugins-install.sh" "rclone-sync.sh")
fi

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

wget -O config.py.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py
if [ $? -ne 0 ] ;  then
    wget -O config.py.new https://raw.github.com/pageauc/pi-timolo/master/source/config.py
    wget -O convid.conf.new https://raw.github.com/pageauc/pi-timolo/master/source/convid.conf
    wget -O makevideo.conf.new https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.conf
    wget -O Readme.md -q https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O media/webserver.txt https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
    # wget -O gdrive https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
else
    wget -O convid.conf.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/convid.conf
    wget -O makevideo.conf.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/makevideo.conf
    wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O media/webserver.txt -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
    # wget -O gdrive -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
fi

echo "$STATUS Installing plugins Wait ..."
PLUGINS_DIR='plugins'  # Default folder install location
pluginFiles=("__init__.py" "dashcam.py" "secfast.py" "secQTL.py" "secstill.py" \
"secvid.py" "shopcam.py" "slowmo.py" "TLlong.py" "TLshort.py")
mkdir -p $PLUGINS_DIR
cd $PLUGINS_DIR
INSTALL_PATH=$( pwd )
echo "Plugins Install Path is $INSTALL_PATH"

for fname in "${pluginFiles[@]}" ; do
  if [ -f $fname ]; then     # check if local file exists.
    echo "INFO  - $fname Skip Download Since Local Copy Found"
  else
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR - $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname"
        fi
    fi
  fi
done
cd ..
echo "$STATUS Done plugins Install as Required."

if [ ! -f /usr/bin/rclone ]; then
    echo "$STATUS rclone Download and Setup"
    echo "Download https://downloads.rclone.org/rclone-v1.38-linux-arm.zip"
    wget wget -O rclone.zip -q --show-progress https://downloads.rclone.org/rclone-v1.38-linux-arm.zip
    echo "unzip rclone.zip to folder rclone-v1.38-linux-arm"
    unzip -o rclone.zip
    echo "Installing rclone files and man pages"
    cd rclone-v1.38-linux-arm
    sudo cp rclone /usr/bin/
    sudo chown root:root /usr/bin/rclone
    sudo chmod 755 /usr/bin/rclone
    sudo mkdir -p /usr/local/share/man/man1
    sudo cp rclone.1 /usr/local/share/man/man1/
    sudo mandb
    cd ..
    echo "Deleting rclone.zip and rclone-v1.38-linux-arm folder"
    rm rclone.zip
    rm -r rclone-v1.38-linux-arm
fi

echo "-------------------------------------------------------------"
echo "$STATUS Make Required Files Executable"
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
  echo "Raspbian System is Up To Date"
else
  echo "Performing Raspbian System Update"
  echo "  This Will Take Some Time ...."
  sudo apt-get -y update
  echo "Done Rasbian Update"
  echo "Performing Raspbian System Upgrade"
  echo "  This Will Take Some Time ...."
  sudo apt-get -y upgrade
  echo "Done Raspbian Upgrade"
fi

echo "$STATUS Installing pi-timolo Dependencies Wait ..."
sudo apt-get install -yq python-picamera python3-picamera python-imaging dos2unix python-pyexiv2 libav-tools
sudo apt-get install -yq python-scipy  # New Dependency for enhanced motion detection
sudo apt-get install -yq gpac   # required for MP4Box video converter
sudo apt-get install -yq fonts-freefont-ttf # Required for Jessie Lite Only
sudo apt-get install -yq python-opencv
echo "$STATUS Done Dependencies Install"

# Check if pi-timolo-install.sh was launched from pi-timolo folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -f 'pi-timolo-install.sh' ]; then
    echo "$STATUS Cleanup pi-timolo-install.sh"
    rm pi-timolo-install.sh
  fi
fi

if [ -f gdrive ]; then
   rm gdrive
fi

if [ -f 'install.sh' ]; then
  echo "$STATUS Delete Old install.sh"
  rm install.sh
fi

if [ -f 'makemovie.sh' ]; then
  echo "$STATUS Delete Old makemovie.sh"
  rm makemovie.sh
fi

if [ -f 'makedailymovie.sh' ]; then
  echo "$STATUS Delete Old makedailymovie.sh"
  rm makedailymovie.sh
fi

if [ -f /usr/bin/rclone ]; then
  echo "$STATUS rclone is installed at /usr/bin/rclone"
fi

echo "
-----------------------------------------------
$STATUS pi-timolo Complete
-----------------------------------------------
Minimal Instructions:
1 - Reboot RPI if there are significant Raspbian system updates.
2 - If config.py already exists then old file is config.py.prev
3 - To Test Run pi-timolo execute the following commands in RPI SSH
    or terminal session. Default is Timelapse and Motion Track On

    cd ~/pi-timolo
    ./pi-timolo.py

4 - To manage pi-timolo, Run menubox.sh Execute commands below

    cd ~/pi-timolo
    ./menubox.sh

For Detailed Instructions See Wiki https://github.com/pageauc/pi-timolo/wiki

Good Luck Claude ...
Bye"

