#!/bin/bash
ver="0.1"
echo "$0 ver $ver written by Claude Pageau"

if [ ! -z "$1" ] ; then
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
fi

if [ -f /usr/bin/rclone ]; then
    echo "rclone installed to /usr/bin/rclone"
    echo "-------------------------------------------------------------------------------"
    echo "To configure one rclone remote service on RPI.

    1 Open SSH login session to RPI and execute command below

      rclone config

      Follow rclone prompts. For more Details see  https://rclone.org/
      You will be required to have a login account on the remote service
    2 When prompted specify a remote name to idenify remote resource.
      eg gdmedia
    3 On RPI, mouse highlight rclone url link (do not hit enter)
      then in logged web browser url bar right click paste and go .
    4 On computer web browser security page, Confirm access.
    5 Copy web browser access security token and paste
      into RPI SSH session rclone prompt. Enter to accept
    6 To test remote service access. Execute the following where
      gdmedia is the name you gave your remote service

      rclone ls gdmedia:/

    Example sync From RPI folder
                   To remote service name and folder

    rclone /home/pi/pi-timolo/media/motion gdmedia:media/motion

    Good Luck Claude ..
    "
    exit 0
else
    echo "-------------------------------------------------------------------------------
rclone Allows syncing files from/to many remote storage services
    
rclone Not Installed. Specify a parameter per example below

    ./rclone-install.sh install
    
Follow installation instructions after install is complete.
Note Instructions were tested with google drive."
    exit 1
fi
