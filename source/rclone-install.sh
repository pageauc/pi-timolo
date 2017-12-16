#!/bin/bash
ver="9.5"
echo "$0 ver $ver written by Claude Pageau"

if [ ! -f /usr/bin/rclone -o ! -z "$1" ]; then
    echo "-------------------------------------------------------------------------------"
    echo "Download https://downloads.rclone.org/rclone-v1.38-linux-arm.zip"
    wget wget -O rclone.zip -q --show-progress https://downloads.rclone.org/rclone-v1.38-linux-arm.zip
    echo "unzip rclone.zip to folder rclone-v1.38-linux-arm"
    unzip -o rclone.zip
    echo "Install files and man pages"
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
    wget -O rclone-sync.sh https://raw.github.com/pageauc/pi-timolo/master/source/rclone-sync.sh
    chmod +x rclone-sync.sh
fi
echo "rclone installed at /usr/bin/rclone"
echo "-------------------------------------------------------------------------------"
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

  rclone ls gdmedia:/

Example sync command make source identical to destination

rclone sync -v /home/pi/pi-timolo/media/motion gdmedia:media/motion

To upgrade

  ./rclone-install.sh upgrade

Note: Instructions were tested with google drive.

Bye
"


