#!/bin/bash
echo "$0 ver 1.0  written by Claude Pageau"
if pidof -o %PPID -x "rclone-sync.sh"; then
    echo "WARN  - rclone sync already running. Only one allowed."
    exit 1
fi

localSyncDir="/home/pi/pi-timolo/media/recent/motion"
remoteSyncDir="media/recent/motion"
rcloneName="gdmedia"

/usr/bin/rclone sync -v $remoteSyncDir $rcloneName:$remoteSyncDir