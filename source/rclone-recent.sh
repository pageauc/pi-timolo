#!/bin/bash
progName=$(basename -- "$0")
echo "$progName ver 9.61  written by Claude Pageau"

# Customize rclone sync variables Below
# ---------------------------------------
rcloneName="gdmedia"
syncRoot="/home/pi/pi-timolo"
localSyncDir="media/recent/motion"
remoteSyncDir="mycam/recent"
# ---------------------------------------

# Display Users Settings
echo "
---------- SETTINGS -------------
rcloneName   : $rcloneName
syncRoot     : $syncRoot
localSyncDir : $localSyncDir
remoteSyncDir: $remoteSyncDir
---------------------------------"
if pidof -o %PPID -x "$progName"; then
    echo "WARN  - $progName Already Running. Only One Allowed."
else
    if [ -f /usr/bin/rclone ]; then
        echo "rclone is installed at /usr/bin/rclone"
        rclone -V
        echo "cd $syncRoot"
        cd "$syncRoot"
        echo "/usr/bin/rclone sync -v $localSyncDir $rcloneName:$remoteSyncDir"
        echo "One Moment Please ..."
        /usr/bin/rclone sync -v $localSyncDir $rcloneName:$remoteSyncDir
    else 
        echo "WARN  - /usr/bin/rclone Not Installed."
    fi    
fi
echo "$progName Bye ..."