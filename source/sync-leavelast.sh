#!/bin/bash
# written 7-May-2015 by Claude Pageau email: pageauc@gmail.com
# This script was written to work with pi-timolo and gdrivefs
# For details See https://github.com/pageauc/pi-timolo
# This script can be modified to suit other similar needs.
# Modify the variables in the script to suit your needs. eg source, destination Etc 
# This script will copy files from a local RPI SD card
# folder to a remote mount excluding the most recent file since
# it might still be updating. This avoids a pi-timolo.py crash with camera.
# It checks if destination is mounted and also Looks for a sync lock file
# that is created by pi-timolo.py ver 2.51 
# It Kills the copy process if it has been running. > 600 seconds (10 min)
# Suggest you run this script from crontab every minute or so.  
# Add appropriate line to crontab using command sudo crontab -e
# example crontab entry below without # comment char
# */1 * * * * /home/pi/pi-timolo/sync-leavelast.sh >/dev/nul

files=*jpg
source=dogcam
destination=gdrivefs/dogcam
mount_dir=/mnt/gdfs
command_to_run='cp -upv'
sync_file=pi-timolo.sync

# Get current folder that this script is located in
current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo " "
echo "                 $0 version 1.0" 
echo "-------------------------------------------------------------------"
echo "Synchronize files From $current_dir/$source"
echo "                   To  $current_dir/$destination"     
echo "-------------------------------------------------------------------"
if grep -qs $mount_dir /proc/mounts
then
  echo "$mount_dir is Mounted"
  if [ -z "$(pgrep cp)" ]
  then
    # Check for sync file indicating pi-motion.py saved new files
    if [ -e $current_dir/$sync_file ]
    then
      echo "Start Sync Please wait ...." 
      ls -t $current_dir/$source/$files |
      # pipes a source dir listing sorted by time
      (
        # the first line will be the most recent file
        read the_most_recent_file
        # do nothing with the most recent file: $the_most_recent_file
        while read not_the_most_recent_file
        do
          $command_to_run $not_the_most_recent_file $current_dir/$destination
          if [ $? -ne 0 ]
          then
            echo "ERROR - $command_to_run Processing failed."
            echo "Possible Cause - No Internet Connection." 
            echo "Please Investigate ... Exit $0"
            exit
          fi            
        done
      )
      # If successful then remove sync file
      echo "Sync Complete for Destination - $current_dir/$destination"
      rm -f $current_dir/$sync_file 
      echo "Deleted Sync File $current_dir/$sync_file"
      echo "Successful Completion ... Exit $0"
    else
      echo "Sync File Not Found - $current_dir/$sync_file"
      echo "         For Source - $current_dir/$source/$files"
      echo "No Files to Process ... Exit $0"
    fi    
  else
    # $command_to_run is already running so check how long and kill if past time limit
    if [ -z "$(sudo ps axh -O etimes | grep cp | grep -v grep | sed 's/^ *//'| awk '{if ($2 >= 600) print $1}')" ]
    then
      RUNTIME=$(sudo ps axh -O etimes | grep cp | grep -v grep | sed 's/^ *//' | awk '{if ($2 > 0) print $2}')
      echo "$command_to_run .. Has Run for $RUNTIME seconds. Will kill when greater than 600 seconds 10 min."
    else
      SYNC_PID=$(pgrep cp)
      echo "$command_to_run .. Has Run longer than 10 minutes so Kill PID $SYNC_PID"
      KILLPID=$(ps axh -O etimes | grep cp | grep -v grep | awk '{if ($2 >= 600) print $1}')
      echo "$command_to_run .. Killing $KILLPID"
      sudo kill $KILLPID
      echo "Killed $command_to_run PID=$KILLPID .... Exit $0" 
    fi  
  fi
else
  echo "Destination $mount_dir is NOT Mounted."
  echo "Please mount before using this script ... Exit $0"
fi