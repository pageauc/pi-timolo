#!/bin/bash

# makedailymovie.sh - written by Claude Pageau.
# Skip most recent file logic based on script by zengargoyle
# This script will create a daily movie from jpg files in motion folder
# It will then use mencoder to create avi movie and move it to a mount point
# make sure you create the required mnt folders and create the fstab entry to mount
# the remote share onto /home/pi/pi-timolo/mnt.  This folder MUST be empty before the share will mount.
# Verify the share point is mounted before running this script.
# Note the previous daily movie will be deleted when this script is run so you have 24 hours to
# fix any copy problem to external share mount point folder.
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

# sudo rm /home/pi/pi-timolo/dailymovie/*jpg

# get current working folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
folder_source=$DIR/motion
folder_destination=$DIR/mnt
moviename=$DIR/dailymovie_$(date '+%Y%m%d').avi
movielist=$DIR/dailymovie.txt

clear
echo $0 " Working ..."
echo "=========================================================================="
echo "Movie Name  =" $moviename
echo "Source      =" $folder_source
echo "Destination =" $folder_destination
echo "Image List  =" $movielist
echo "=========================================================================="

cd $DIR

if [ -f $movielist ]; then
   echo "Delete "$movielist
   rm $movielist
fi

if [ -f $DIR/*avi ]; then
   rm $DIR/*avi 
fi

echo "Create jpg Image files List "$movielist
echo "From Folder "$folder_source

# ls -t sorts files by last modification time, most recent to oldest
ls -t $folder_source/*.jpg |
(
  # the first line will be the most recent file so ignore it
  # since it might still be in progress
  read the_most_recent_file
     # Skip this file in listing
  # do something with the rest of the files
  while read not_the_most_recent_file
  do
     echo $not_the_most_recent_file >> $DIR/dailymovie.tmp
  done
)

# reverse the list order so the video runs from oldest to most recent
tac $DIR/dailymovie.tmp > $movielist

if [ -f $DIR/dailymovie.tmp ]; then
   rm $DIR/dailymovie.tmp
fi

echo "Making Daily Movie ... "$moviename
echo "=========================================================================="
/usr/bin/mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1280:720 -o $moviename -mf type=jpeg:fps=5  mf://@$movielist
echo "=========================================================================="
echo "Copy "$moviename" to "$folder_destination
cp $moviename $folder_destination
echo "Processing Complete ..."
