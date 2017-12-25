#!/bin/bash
progName=$(basename -- "$0")
echo "$progName ver 9.61  written by Claude Pageau"

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
    if [ -f /usr/bin/rclone ]; then
        echo "rclone is installed at /usr/bin/rclone"
        rclone -V
        echo "/usr/bin/rclone cleanup -v $rcloneName:"
        echo "One Moment Please ..."
        /usr/bin/rclone cleanup -v $rcloneName:
        echo "Done Cleanup of $rcloneName:"
    else
        echo "WARN  - /usr/bin/rclone Not Installed."
    fi
fi
echo "$progName Bye ..."

