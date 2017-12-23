#!/bin/bash
echo "$0 ver 9.6  written by Claude Pageau"

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
if pidof -o %PPID -x "$0"; then
    echo "WARN  - $0 Already Running. Only One Allowed."
    exit 1
else
    echo "cd $syncRoot"
    cd "$syncRoot"
    echo "/usr/bin/rclone sync -v $localSyncDir $rcloneName:$remoteSyncDir"
    echo "One Moment Please ..."
    /usr/bin/rclone sync -v $localSyncDir $rcloneName:$remoteSyncDir
fi
echo "$0 Bye ..."