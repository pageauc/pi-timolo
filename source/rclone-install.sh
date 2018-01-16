#!/bin/bash
ver="10.1"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # get cur dir of this script
progName=$(basename -- "$0")
cd $DIR
echo "INFO  : $progName $ver  written by Claude Pageau"
echo "-------------------------------------------------------------------------------"
if [ -f /usr/bin/rclone ]; then
    echo "INFO  : Rclone Reinstall/Upgrade"
    /usr/bin/rclone -V
else
    echo "INFO  : Rclone New Install"
fi

echo "INFO  : Download https://downloads.rclone.org/rclone-current-linux-arm.zip"
wget wget -O rclone.zip -q --show-progress https://downloads.rclone.org/rclone-current-linux-arm.zip
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
wget -O rclone-test.sh https://raw.github.com/pageauc/pi-timolo/master/source/rclone-samples/rclone-master.sh
chmod +x rclone-test.sh

if [ -f /usr/bin/rclone ]; then
  echo "INFO  : rclone is installed at /usr/bin/rclone"
  rclone -V
  echo "                       INSTRUCTIONS
1 You will be required to have a login account on the remote service
  Open putty SSH login session to RPI and execute command below

  rclone config

  Follow rclone prompts. For more Details See
  https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-rclone
2 At name> prompt specify a reference name  eg gdmedia
3 At storage> prompt Enter a remote storage number from List
4 Select Auto Config, At Link: prompt, left click
  and highlight rclone url link (do not hit enter)
5 on computer web browser url bar right click paste and go.
6 On computer web browser security page, Confirm access.
7 Copy web browser access security token and paste
  into RPI SSH session rclone prompt. Enter to accept
8 To test remote service access. Execute the following where
  gdmedia is the name you gave your remote service

  rclone listremotes
  rclone ls gdmedia:/

Example sync command will make remote destination identical to local source.

rclone sync -v /home/pi/pi-timolo/media/motion gdmedia:media/motion

Note: Instructions were tested with google drive.
"
else
  echo "ERROR : Problem Installing rclone.  Please Investigate"
fi
echo "Bye..."



