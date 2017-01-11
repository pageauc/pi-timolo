#!/bin/bash
ver="3.2"
# makedailymovie.sh - written by Claude Pageau.
# To install/update avconv execute the following command in RPI terminal session
#
# sudo apt-get install libav-tools
#
# For more details see GitHub Wiki here
# https://github.com/pageauc/pi-timolo/wiki/Utilities

#            ------------- Start Script ------------------
# get current working folder that this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# avconv encoding variables for output video
fps=10               # Output video frames per second
vid_size='1280x720'  # Output video size width x height
a_ratio=16:9         # Output video aspect ratio

# User Settings for source and destination folders
# Note destination folder will be created if it does not exist
video_prefix="TL_"
folder_destination=$DIR/video  # destination folder default $DIR/video (will be created if it does not exist)
folder_source=$DIR/timelapse   # location of source jpg images for video.  default $DIR/timelapse
delete_source_files=false      # default false Use with EXTREME CAUTION since true will DELETE source files after encoding
                               # If something goes wrong you may end up with no source images and a bad encode.
                               # delete=true  noAction=false (default)   Note no spaces between variable and value
share_copy_on=false            # default=false true copies video to the network share via mount location below
share_destination=$DIR/mnt     # A valid network share mount point to copy video to
                               # IMPORTANT - Make sure share is mounted or you will have files copied to the folder
                               #             This will prevent mounting of share until the files in the folder are moved/deleted.

#  Script variables
folder_working=$DIR"/makevideo_tmp"
error_log_file=$DIR"/makevideo_error.log"

# Output videoname with prefix and date and time (minute only).
# Video can be specified as avi or mp4
videoname=$video_prefix$(date '+%Y%m%d-%H%M').mp4

clear
echo "$0 version $ver written by Claude Pageau"
echo "====================== SETTINGS =========================================="
echo "videoname            =" $videoname
echo "folder_source        =" $folder_source
echo "folder_destination   =" $folder_destination
echo "delete_source_files  =" $delete_source_files
echo "share_copy_on        =" $share_copy_on
echo "share_destination    =" $share_destination
echo "=========================================================================="
echo "Working ..."

# Create destination folder if it does note exist
if [ ! -d $folder_source ] ; then
    echo "ERROR - Source Folder" $folder_source "Does Not Exist"
    echo "ERROR - Check $0 Variable folder_source and Try Again"
    echo "ERROR - Source Folder $folder_source Does Not Exist." >> $error_log_file
    exit 1
fi

# Check if source files exist
source_files=$folder_source/*jpg
if [ ! -e $source_files ] ; then
    echo "ERROR - No Source Files Found in" $source_files
    echo "ERROR - Please Investigate and Try Again"
    exit 1
fi

# Create destination folder if it does note exist
if [ ! -d $folder_destination ] ; then
    mkdir $folder_destination
    if [ "$?" -ne 0]; then
        echo "ERROR - Problem Creating Destination Folder" $folder_destination
        echo "ERROR - If destination is a remote folder or mount then check network, destination IP address, permissions, Etc"
        echo "ERROR - mkdir Failed - $folder_destination Could NOT be Created." >> $error_log_file
        exit 1
    fi
fi

# Remove old working folder if it exists
if [ -d $folder_working ] ; then
    echo "WARN  - Removing previous working folder" $folder_working 
    sudo rm -R $folder_working
fi

# Create a new temporary working folder to store soft links 
# that are numbered sequentially in case source number has gaps
echo "STATUS- Creating Temporary Working Folder " $folder_working
mkdir $folder_working
if [ ! -d $folder_working ] ; then
    echo "ERROR - Problem Creating Temporary Working Folder " $folder_working
    echo "ERROR - mkdir Failed - $folder_working Could NOT be Created." >> $error_log_file
    exit 1
fi 

cd $folder_working    # change to working folder
# Create numbered soft links in working folder that point to image files in source folder
echo "STATUS- Creating Image File Soft Links"
echo "STATUS-   From" $folder_source
echo "STATUS-   To  " $folder_working
a=0
ls $folder_source/*.jpg |
(
  # the first line will be the most recent file so ignore it
  # since it might still be in progress
  read the_most_recent_file
  # Skip this file in listing
  # create sym links in working folder for the rest of the files
  while read not_the_most_recent_file
  do
    new=$(printf "%05d.jpg" ${a}) #05 pad to length of 4 max 99999 images
    ln -s ${not_the_most_recent_file} ${new}
    let a=a+1
  done
)
cd $DIR      # Return back to launch folder

echo "=========================================================================="
echo "Making Video ... "$videoname
echo "=========================================================================="
/usr/bin/avconv -y -f image2 -r $fps -i $folder_working/%5d.jpg -aspect $a_ratio -s $vid_size $folder_destination/$videoname
if [ $? -ne 0 ] ; then
  echo "ERROR - avconv Encoding Failed for" $folder_destination/$videoname 
  echo "ERROR - Review avconv output for Error Messages and Correct Problem"
  echo "ERROR - avconv Encoding Failed for" $folder_destination/$videoname >> $error_log_file
  exit 1
else
  echo "=========================================================================="
  echo "STATUS- Video Saved to" $folder_destination/$videoname
  
  if [ "$delete_source_files" = true ] ; then
    echo "WARN  - Variable delete_source_files="$delete_source_files
    echo "WARN  - Deleting Source Files $folder_source/*jpg"
    # Be Careful Not to Crash pi-timolo.py by deleting image file in progress
    ls -t $folder_source/*.jpg |
    (
      # the first line will be the most recent file so ignore it
      # since it might still be in progress
      read the_most_recent_file
      # Skip this file in listing since image may be in progress
      while read not_the_most_recent_file
      do
        sudo rm $not_the_most_recent_file
      done
    )    
  fi
  
  echo "STATUS- Deleting Working Folder" $folder_working
  sudo rm -R $folder_working
  if [ $? -ne 0 ] ; then 
    echo "ERROR - Could not Delete Working Folder" $folder_working
    echo "ERROR - Check for permissions or other possible problems"
    echo "ERROR - Could not Delete Working Folder" $folder_working >> $error_log_file
    exit 1
  fi 
fi

# Check if video file is to be copied to a network share
if [ "$share_copy_on" = true ] ; then
  echo "STATUS- Copy Video File"
  echo "STATUS-   From" $folder_destination/$videoname
  echo "STATUS-   To  " $share_destination

  if grep -qs "$share_destination" /proc/mounts; then
    echo "STATUS- $share_destination is Mounted."
  else
    echo "ERROR - Cannot Copy File to Share Folder"
    echo "ERROR - Failed to Copy" $folder_destination/$videoname "to" $share_destination "Because It is NOT Mounted"
    echo "ERROR - Please Investigate Mount Problem and Try Again"
    echo "ERROR - Once Resolved You Will Need to Manually Transfer Previous Video Files"
    echo "ERROR - Failed to Copy" $folder_destination/$videoname "to" $share_destination "Because It is NOT Mounted" >> $error_log_file
    exit 1
  fi
  
  cp $folder_destination/$videoname $share_destination 
  if [ $? -ne 0 ]; then
    echo "ERROR - Copy Failed $folder_destination/$videoname to" $share_destination/$videoname
    echo "ERROR - If destination is a remote folder or mount then check network, destination IP address, permissions, Etc"
    echo "ERROR - Copy Failed from" $folder_destination/$videoname "to" $share_destination/$videoname >> $error_log_file
    exit 1
  else
    if [ -e $share_destination/$videoname ] ; then
      echo "STATUS- Successfully Moved Video"
      echo "STATUS-   From" $folder_destination/$videoname
      echo "STATUS-   To  " $share_destination/$videoname
      echo "WARN  - Deleting Local Video File" $folder_destination/$videoname
      sudo rm -f $folder_destination/$videoname
      if [ -e $folder_destination/$videoname ] ; then
        echo "ERROR - Could Not Delete" $folder_destination/$videoname "After Copy To" $share_destination/$videoname
        echo "ERROR - Please investigate"
        echo "ERROR - Could Not Delete" $folder_destination/$videoname "After Copy To" $share_destination/$videoname >> $error_log_file
        exit 1
      fi
    else
      echo "ERROR - Problem copying $folder_destination/$videoname to $share_destination/$videoname"
      echo "ERROR - If destination is a remote folder or mount then check network, destination IP address, permissions, Etc"
      echo "ERROR - Copy Failed from" $folder_destination/$videoname "to" $share_destination/$videoname >> $error_log_file
      exit 1
    fi
  fi    
fi
echo "STATUS- Processing Completed Successfully ..."
echo "=========================================================================="
echo "$0 Done"

#               ------------------ End Script ----------------------------