#!/bin/bash

# avconv_makemovie.sh version 2.8 - written by Claude Pageau.
# To install/update avconv execute the following command in RPI terminal session
#
# sudo apt-get install libav-tools
#
# Mounting a network share to /home/pi/pi-timolo/mnt folder
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

#            ------------- Start Script ------------------
# get current working folder that this script was launched from
ver="2.9"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# User Settings for source and destination folders
# Note destination folder will be created if it does not exist
folder_source=$DIR/timelapse     # location of source jpg images for video
folder_destination=$DIR  # destination movies folder (will be created if it does not exist)
folder_working=$DIR/avconv_makemovie_tmp
error_log_file=$DIR/makemovie_error.log

# Output video path with a unique daily name by date and time.
# Video can be specified as avi or mp4
moviename=makemovie_$(date '+%Y%m%d-%H%M').mp4

# avconv encoding variables for output video
fps=10               # Output video frames per second
vid_size='1280x720'  # Output video size width x height
a_ratio=16:9         # Output video aspect ratio

clear
echo $0 " version $ver Working ..."
echo "====================== SETTINGS =========================================="
echo "Movie Name  =" $moviename
echo "Source      =" $folder_source
echo "Destination =" $folder_destination
echo "Working     =" $folder_working
echo "=========================================================================="

# Remove old working folder if it exists
if [ -d $folder_working ]; then
  echo "Removing previous working folder " $folder_working 
  sudo rm -R $folder_working
fi

# Create a new working folder
echo "Creating Temporary Working Folder " $folder_working
mkdir $folder_working
cd $folder_working    # change to working folder
# Create numbered soft links pointing to image files in source folder
echo "Creating soft links for " $folder_source " files in  "$folder_working
a=0
ls $folder_source/*.jpg |
(
  # the first line will be the most recent file so ignore it
  # since it might still be in progress
  read the_most_recent_file
     # Skip this file in listing
  # do something with the rest of the files
  while read not_the_most_recent_file
  do
    new=$(printf "%05d.jpg" ${a}) #05 pad to length of 4 max 99999 images
    ln -s ${not_the_most_recent_file} ${new}
    let a=a+1  
  done
)
cd $DIR      # Return back to launch folder

echo "=========================================================================="
echo "Making Movie ... "$moviename "from images in " $folder_source
echo "=========================================================================="
sudo /usr/bin/avconv -y -f image2 -r $fps -i $folder_working/%5d.jpg -aspect $a_ratio -s $vid_size $folder_destination/$moviename
if [ $? -ne 0 ]; then
  echo "========================== ERROR ========================================="
  echo "avconv Encoding Failed for " $folder_destination/$moviename " Please Investigate Problem"
  echo "Review avconv output for error messages and correct problem"
  echo "ERROR - avconv Encoding Failed for " $folder_destination/$moviename >> $error_log_file  
  exit 1
else
  echo "Processing Completed Successfully ..."
  echo "Deleting Working Folder " $folder_working
  sudo rm -R $folder_working
  if [ $? -ne 0 ]; then 
    echo "ERROR - Could not Delete Working Folder " $folder_working " Please Investigate ..."
    echo "Check for permissions or other possible problems" 
    echo "============================ ERROR +======================================"           
    exit 1
  else 
    echo "=========================== SUCCESS ======================================"
    echo "STATUS- Video Saved to $folder_destination/$moviename"     
  fi    
fi    
#               ------------------ End Script ----------------------------