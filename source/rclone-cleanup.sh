#!/bin/bash
progName=$(basename -- "$0")
echo "$progName ver 9.6  written by Claude Pageau"

# Customize rclone sync variables Below
# ---------------------------------------
rcloneName="gdmedia"
# ---------------------------------------

# Display Users Settings
echo "
---------- SETTINGS -------------
rcloneName   : $rcloneName
---------------------------------"
if pidof -o %PPID -x "$progName"; then
    echo "WARN  - $progName Already Running. Only One Allowed."
else
    echo "/usr/bin/rclone cleanup -v $rcloneName:"
    echo "One Moment Please ..."
    /usr/bin/rclone cleanup -v $rcloneName:
    echo "Done Cleanup of $rcloneName:"
fi
echo "$progName Bye ..."
