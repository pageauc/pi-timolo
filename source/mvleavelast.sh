#!/bin/sh

# movefiles.sh - written by Claude Pageau based on script by zengargoyle
# This script will move files from the local SD card images
# folder to a remote network share mount excluding the most recent file since
# it still might be updating.  This avoids a rpi-timelapse.py crash
# Note xbmc in the example below is a folder mounted on a remote
# disk drive share.  You can mount the external share by adding
# the appropriate entry to the /etc/fstab
# example
#
# sudo nano /etc/fstab
#
# Add a similar line below to the fstab.  
# This example mounts an external Hard Drive share
# on a RPI running openelec xbmc.  
# Change the IP address, share name and paths appropriately (exclude the #)
#
# //192.168.1.154/sharename/Media/Images /home/pi/rpi-timelapse/xbmc cifs username=root,password=openelec,uid=pi,gid=pi, 0 0
#
# Add a crontab entry to the root crontab per the below.  
# make sure movefiles.sh is executable eg sudo chmod +x movefiles.sh
#
# sudo crontab -e
#
# Add similar crontab entry as line below (excluding the #). 
# This would execute movefiles.sh every 15 minutes
#
# */15 * * * * /home/pi/rpi-timelapse/movefiles.sh

files_to_check=/home/pi/pi-timolo/media/timelapse/*jpg
command_to_run='mv -f '
the_destination=/home/pi/pi-timolo/mnt

# looking for files matching $files_to_check
# ls -t sorts files by last modification time, most recent to oldest

ls -t $files_to_check |
(

  # the first line will be the most recent file

  read the_most_recent_file
  # do nothing with the most recent file: $the_most_recent_file


  # the rest of the lines will not be the most recent file

  # do something with the rest of the files
  while read not_the_most_recent_file
  do
    $command_to_run $not_the_most_recent_file $the_destination
  done
)
