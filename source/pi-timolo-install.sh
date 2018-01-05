#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="9.90"
progName=$(basename -- "$0")
TIMOLO_DIR='pi-timolo'  # Default folder install location

cd ~
is_upgrade=false
if [ -d "$TIMOLO_DIR" ] ; then
  STATUS="Upgrade"
  echo "INFO  : Upgrade pi-timolo files"
  is_upgrade=true
else
  echo "INFO  : New pi-timolo Install"
  STATUS="New Install"
  mkdir -p $TIMOLO_DIR
  mkdir -p $TIMOLO_DIR/media
  echo "INFO  : $TIMOLO_DIR Folder Created"
fi

cd $TIMOLO_DIR
INSTALL_PATH=$( pwd )

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "
-------------------------------------------------------------
INFO  : $progName $ver  written by Claude Pageau
        $STATUS from https://github.com/pageauc/pi-timolo
-------------------------------------------------------------
"

# check if this is an upgrade and bypass update of configuration files
if $is_upgrade ; then
  timoloFiles=("menubox.sh" "pi-timolo.py" "pi-timolo.sh"  \
"sync.sh" "webserver.py" "webserver.sh" \
"convid.sh" "makevideo.sh" "mvleavelast.sh" "rclone-sync.sh" \
"rclone-recent.sh" "rclone-motion.sh" "rclone-cleanup.sh" "remote-run.sh")

if [ -f "sync.sh" ] ; then
    cp sync.sh sync.sh.old
fi

else   # New Install
  timoloFiles=("config.py" "menubox.sh" "pi-timolo.py" "pi-timolo.sh" \
"sync.sh" "webserver.py" "webserver.sh" "watch-app.sh" \
"convid.sh" "makevideo.sh" "video.conf" "mvleavelast.sh" \
"rclone-recent.sh" "rclone-motion.sh" "rclone-videos.sh" "rclone-cleanup.sh" "remote-run.sh")
fi

for fname in "${timoloFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo/master/source/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname https://raw.github.com/pageauc/pi-timolo/master/source/$fname
        fi
    fi
done

wget -O config.py.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/config.py
if [ $? -ne 0 ] ;  then
    wget -O config.py.new https://raw.github.com/pageauc/pi-timolo/master/source/config.py
    wget -O watch-app-new.sh https://raw.github.com/pageauc/pi-timolo/master/source/watch-app.sh
    wget -O video.conf.new https://raw.github.com/pageauc/pi-timolo/master/source/video.conf
    wget -O Readme.md -q https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O media/webserver.txt https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
    wget -O rclone-sync-new.sh https://raw.github.com/pageauc/pi-timolo/master/source/rclone-sync.sh
    wget -O rclone-videos-new.sh https://raw.github.com/pageauc/pi-timolo/master/source/rclone-videos.sh
    # wget -O gdrive https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
else
    wget -O watch-app-new.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/watch-app.sh
    wget -O video.conf.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/video.conf
    wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O media/webserver.txt -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
    wget -O rclone-sync-new.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/rclone-sync.sh
    wget -O rclone-videos-new.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/rclone-videos.sh
    # wget -O gdrive -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
fi

# Install rclone with latest version
wget -O rclone.zip -q --show-progress https://downloads.rclone.org/rclone-current-linux-arm.zip
echo "INFO  : unzip rclone.zip to folder rclone-tmp"
unzip -o -j -d rclone-tmp rclone.zip
echo "INFO  : Install files and man pages"
cd rclone-tmp
sudo cp rclone /usr/bin/
sudo chown root:root /usr/bin/rclone
sudo chmod 755 /usr/bin/rclone
sudo mkdir -p /usr/local/share/man/man1
sudo cp rclone.1 /usr/local/share/man/man1/
sudo mandb
cd ..
echo "INFO  : Deleting rclone.zip and Folder rclone-tmp"
rm rclone.zip
rm -r rclone-tmp

echo "INFO  : $STATUS Install of plugins Wait ..."
PLUGINS_DIR='plugins'  # Default folder install location
pluginFiles=("__init__.py" "dashcam.py" "secfast.py" "secQTL.py" "secstill.py" \
"secvid.py" "strmvid.py" "shopcam.py" "slowmo.py" "TLlong.py" "TLshort.py")

# Install plugins
mkdir -p $PLUGINS_DIR
cd $PLUGINS_DIR
for fname in "${pluginFiles[@]}" ; do
  if [ -f $fname ]; then     # check if local file exists.
    echo "INFO  : $fname Skip Download Since Local Copy Found"
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
echo "INFO  : $STATUS Done plugins as Required."
echo "-------------------------------------------------------------"
echo "INFO  : $STATUS Make Required Files Executable"
chmod +x *py
chmod -x config*py
chmod +x *sh
echo "-------------------------------------------------------------"

# check if system was updated today
# NOW="$( date +%d-%m-%y )"
# LAST="$( date -r /var/lib/dpkg/info +%d-%m-%y )"
# if [ "$NOW" == "$LAST" ] ; then
#  echo "Raspbian System is Up To Date"
# else
#  echo "Performing Raspbian System Update"
#  echo "  This Will Take Some Time ...."
#  sudo apt-get -y update
#  echo "Done Rasbian Update"
#  echo "Performing Raspbian System Upgrade"
#  echo "  This Will Take Some Time ...."
#  sudo apt-get -y upgrade
#  echo "Done Raspbian Upgrade"
# fi

echo "INFO  : $STATUS Installing pi-timolo Dependencies Wait ..."
sudo apt-get install -yq python-picamera python3-picamera python-imaging dos2unix python-pyexiv2 libav-tools
sudo apt-get install -yq python-scipy  # New Dependency for enhanced motion detection
sudo apt-get install -yq gpac   # required for MP4Box video converter
sudo apt-get install -yq fonts-freefont-ttf # Required for Jessie Lite Only
sudo apt-get install -yq python-opencv
dos2unix *sh
dos2unix *py
echo "INFO  : $STATUS Done Dependencies Install"

# Check if pi-timolo-install.sh was launched from pi-timolo folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -f 'pi-timolo-install.sh' ]; then
    echo "INFO  : $STATUS Cleanup pi-timolo-install.sh"
    rm pi-timolo-install.sh
  fi
fi

# cleanup old files from previous versions of install
sync_files=("gdrive" "install.sh" "makemovie.sh" "makedailymovie.sh" \
"convid.conf" "convid.conf.orig" "convid.conf.prev" "convid.conf.1" "convid.conf.new" \
"makevideo.conf" "makevideo.conf.orig" "makevideo.conf.prev" "makevideo.conf.1" \
"makevideo.conf.new" "sync.sh")

for fname in "${sync_files[@]}" ; do
    if [ -f $fname ] ; then
        echo "INFO  : Delete $fname"
        rm $fname
    fi
done

if [ -f /usr/bin/rclone ]; then
  echo "INFO  : $STATUS rclone is installed at /usr/bin/rclone"
  rclone -V
else
  echo "ERROR : $STATUS Problem Installing rclone.  Please Investigate"
fi

echo "
-----------------------------------------------
INFO  : $STATUS Complete
-----------------------------------------------
Minimal Instructions:
1 - It is suggested you run sudo apt-get update and sudo apt-get upgrade
    Reboot RPI if there are significant Raspbian system updates.
2 - If config.py already exists then latest file is config.py.new
3 - To Test Run pi-timolo execute the following commands in RPI SSH
    or terminal session. Default is Motion Track On and TimeLapse On

    cd ~/pi-timolo
    ./pi-timolo.py

4 - To manage pi-timolo, Run menubox.sh Execute commands below

    cd ~/pi-timolo
    ./menubox.sh

For Detailed Instructions See Wiki https://github.com/pageauc/pi-timolo/wiki

Good Luck Claude ...
Bye"

