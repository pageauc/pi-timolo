#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="10.7"
progName=$(basename -- "$0")
TIMOLO_DIR='pi-timolo'  # Default folder install location

# Make sure ver below matches latest rclone ver on https://downloads.rclone.org/rclone-current-linux-arm.zip
rclone_cur_ver="rclone v1.41"

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
 "webserver.py" "webserver.sh" \
"convid.sh" "makevideo.sh" "mvleavelast.sh" "remote-run.sh")

else   # New Install
  timoloFiles=("config.py" "menubox.sh" "pi-timolo.py" "pi-timolo.sh" \
"webserver.py" "webserver.sh" "watch-app.sh" \
"convid.sh" "makevideo.sh" "video.conf" "mvleavelast.sh" "remote-run.sh")
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
    wget -O Readme.md https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O media/webserver.txt https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
    wget -O rclone-test.sh https://raw.github.com/pageauc/pi-timolo/master/source/rclone-samples/rclone-master.sh
else
    wget -O watch-app-new.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/watch-app.sh
    wget -O video.conf.new -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/video.conf
    wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/Readme.md
    wget -O media/webserver.txt -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/webserver.txt
    wget -O rclone-test.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/rclone-samples/rclone-master.sh
fi

if [ ! -f video.conf ] ; then
    cp video.conf.new video.conf
fi

if [ ! -f config.py ] ; then
    cp config.py.new config.py
fi
cp config.py config.py.prev   # make copy of previous configuration

if [ ! -f watch-app.sh ] ; then
    cp watch-app-new.sh watch-app.sh
fi

# Install plugins if not already installed.  You must delete a plugin file to force reinstall.
echo "INFO  : $STATUS Check/Install pi-timolo/plugins    Wait ..."
PLUGINS_DIR='plugins'  # Default folder install location
# List of plugin Files to Check
pluginFiles=("__init__.py" "dashcam.py" "secfast.py" "secQTL.py" "secstill.py" \
"secvid.py" "strmvid.py" "shopcam.py" "slowmo.py" "TLlong.py" "TLshort.py")

mkdir -p $PLUGINS_DIR
cd $PLUGINS_DIR
for fname in "${pluginFiles[@]}" ; do
  if [ -f $fname ]; then     # check if local file exists.
    echo "INFO  : $fname plugin Found.  Skip Download ..."
  else
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname"
        fi
    fi
  fi
done
cd ..

# Install rclone samples
echo "INFO  : $STATUS Check/Install pi-timolo/rclone-samples    Wait ..."
RCLONE_DIR='rclone-samples'  # Default folder install location
# List of plugin Files to Check
rcloneFiles=("Readme.md" "rclone-master.sh" "rclone-mo-copy-videos.sh" "rclone-mo-sync.sh" \
"rclone-mo-sync-lockfile.sh" "rclone-mo-sync-recent.sh" "rclone-tl-copy.sh" "rclone-tl-sync-recent.sh" "rclone-cleanup.sh")

mkdir -p $RCLONE_DIR
cd $RCLONE_DIR
for fname in "${rcloneFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/rclone-samples/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo/master/source/rclone-samples/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/pi-timolo/master/source/rclone-samples/$fname"
        fi
    fi
done
cd ..

rclone_install=true
if [ -f /usr/bin/rclone ]; then
    /usr/bin/rclone version
    rclone_ins_ver=$( /usr/bin/rclone version | grep rclone )
    if [ "$rclone_ins_ver" == "$rclone_cur_ver" ]; then
        rclone_install=false
    fi
fi

if "$rclone_install" = true ; then
    # Install rclone with latest version
    echo "INFO  : Install Latest Rclone from https://downloads.rclone.org/rclone-current-linux-arm.zip"
    wget -O rclone.zip -q --show-progress https://downloads.rclone.org/rclone-current-linux-arm.zip
    if [ $? -ne 0 ]; then
        wget -O rclone.zip https://downloads.rclone.org/rclone-current-linux-arm.zip
    fi
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
    echo "INFO  : /usr/bin/rclone Install Complete"
fi

echo "INFO  : $STATUS Install pi-timolo Dependencies Wait ..."

sudo apt-get install -yq python-picamera
sudo apt-get install -yq python3-picamera
sudo apt-get install -yq python-imaging
sudo apt-get install -yq python3-pil
sudo apt-get install -yq dos2unix
sudo apt-get install -yq python-pyexiv2
sudo apt-get install -yq libav-tools  # used for makevideo gpac
sudo apt-get install -yq pandoc # convert markdown to plain text for Readme.md
sudo apt-get install -yq gpac   # required for MP4Box video converter
sudo apt-get install -yq fonts-freefont-ttf # Required for Jessie Lite Only
sudo apt-get install -yq python-opencv
sudo apt-get install -yq python-pip
sudo apt-get install -yq python3-dateutil
sudo apt-get install -yq python-dateutil
if [ $? -ne 0 ] ;  then
    sudo apt-get install -yq python3-pip
    sudo pip install python-dateutil  # used for scheduled date/time feature
    if [ $? -ne 0 ] ;  then
        # Upgrade version of pip on Raspbian Wheezy to add ssl support
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        sudo python get-pip.py
        rm get-pip.py
    fi
fi
sudo pip install python-dateutil
dos2unix -q *
chmod +x *py
chmod -x config*py
chmod +x *sh
chmod +x rclone-samples/*sh

echo "INFO  : $STATUS Done Dependencies Install"

# Check if pi-timolo-install.sh was launched from pi-timolo folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -f 'pi-timolo-install.sh' ]; then
    echo "INFO  : $STATUS Cleanup pi-timolo-install.sh"
    rm pi-timolo-install.sh
  fi
fi

# cleanup old files from previous versions of install
cleanup_files=("get-pip.py" "gdrive" "install.sh" "makemovie.sh" "makedailymovie.sh" \
"convid.conf" "convid.conf.orig" "convid.conf.prev" "convid.conf.1" "convid.conf.new" \
"makevideo.conf" "makevideo.conf.orig" "makevideo.conf.prev" "makevideo.conf.1" \
"makevideo.conf.new" "sync.sh" "pi-timolo-install.sh" "rclone-sync-new.sh" "rclone-videos-new.sh")

for fname in "${cleanup_files[@]}" ; do
    if [ -f $fname ] ; then
        echo "INFO  : Delete $fname"
        rm -f $fname
    fi
done

if [ -f /usr/bin/rclone ]; then
    echo "INFO  : $STATUS rclone is installed at /usr/bin/rclone"
    rclone version
else
    echo "ERROR : $STATUS Problem Installing rclone.  Please Investigate"
fi

echo "
-----------------------------------------------
INFO  : $STATUS Complete ver 10.x
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
    ./menubox.sh"

if $is_upgrade ; then
    echo "
IMPORTANT: pi-timolo.py ver 10.x Adds a Sched StartAt Feature.
           If pi-timolo.py gives error messages on start
           then the latest config.py may not be configured.
           Install per commands below if Required.

    cd ~/pi-timolo
    cp config.py config.py.bak
    cp config.py.new config.py
    nano config.py

Use nano to Restore Custom Settings from config.py.bak then ctrl-x y to Save and Exit
For Details See Wiki at
https://github.com/pageauc/pi-timolo/wiki/How-to-Schedule-Motion,-Timelapse-or-VideoRepeat"
fi

echo "
For Full Instructions See Wiki at https://github.com/pageauc/pi-timolo/wiki

Good Luck Claude ...
Bye"

