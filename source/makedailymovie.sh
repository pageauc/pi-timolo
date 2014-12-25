#!/bin/sh

# makedailymovie.sh - written by Claude Pageau based on script by zengargoyle
# This script will move files from /home/pi/pi-timolo/timelapse to /home/pi/pi-timolo/dailymoves
# It will then use mencoder to create a move and move it to /home/pi/pi-timolo/mnt
# make sure you create the required folders and create the fstab entry to mount
# the remote share onto /home/pi/pi-timolo/mnt.  This folder MUST be empty before the share will mount.
# verify the share point is mounted before running this script.
# Note this script does not delete files in /home/pi/pi-timolo/dailymovies folder.  
# This line can be added to the bottom of the script otherwise if something goes wrong
# the files will be deleted event if the process fails since there is no error checking
# in the script.  I leave it to you to add this if required.
#
# Mounting a network share to /home/pi/pi-timolo/mnt folder
# it still might be updating.  This avoids a rpi-timelapse.py crash
# Note change the IP and sharename path below to suit your network
# You can mount the network share by adding
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
# //192.168.1.154/sharename/Media/Images /home/pi/pi-timolo/mnt cifs username=root,password=openelec,uid=pi,gid=pi, 0 0
#
# Add a crontab entry to the root crontab per the below.  
# make sure makedailymovie.sh is executable eg sudo chmod +x makedailymovie.sh
#
# sudo crontab -e
#
# Add similar crontab entry as line below (excluding the #). 
# This would execute makedailymovie.sh at 10pm every day
#
# 01 20 * * * /home/pi/pi-timolo/makedailymovie.sh

sudo rm /home/pi/pi-timolo/dailymovie/*jpg
files_to_check=/home/pi/pi-timolo/motion/*jpg
command_to_run='cp -u'
the_destination=/home/pi/pi-timolo/dailymovie

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
cd /home/pi/pi-timolo

moviename=dailymovie_$(date '+%Y%m%d').avi

ls  -t -r $the_destination/*jpg > dailymovie.txt
/usr/bin/mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 -o $moviename -mf type=jpeg:fps=5  mf://@dailymovie.txt

mv $moviename /home/pi/pi-timolo/mnt/
