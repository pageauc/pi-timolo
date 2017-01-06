#!/bin/bash

# avconv_makemovie.sh version 3.0 - written by Claude Pageau.
# To install/update avconv execute the following command in RPI terminal session
#
# sudo apt-get install libav-tools
#
# For Details see GitHub Wiki
# here https://github.com/pageauc/pi-timolo/wiki/Utilities

#            ------------- Start Script ------------------
ver="3.0"
# get current working folder that this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# User Settings for source and destination folders
# Note destination folder will be created if it does not exist
folder_source=$DIR/timelapse     # location of source jpg images for video
folder_destination=$DIR  # destination movies folder (will be created if it does not exist)
folder_working=$DIR/avconv_makemovie_tmp
error_log_file=$DIR/makemovie_error.log

delete_source_files=false     # Use with EXTREME CAUTION since source image files will be DELETED after encoding
                              # If something goes wrong you may end up with no source images and a bad encode.
                              # delete=true  noAction=false (default)   Note no spaces between variable and value

# Output video path with a unique daily name by date and time.
# Video can be specified as avi or mp4
moviename=makemovie_$(date '+%Y%m%d-%H%M').mp4

# avconv encoding variables for output video
fps=10               # Output video frames per second
vid_size='1280x720'  # Output video size width x height
a_ratio=16:9         # Output video aspect ratio

clear
echo "$0 version $ver written by Claude Pageau"
echo "Working ..."
echo "====================== SETTINGS =========================================="
echo "Movie Name    =" $moviename
echo "Source        =" $folder_source
echo "Destination   =" $folder_destination
echo "Working       =" $folder_working
echo "Delete Source =" $delete_source_files
echo "=========================================================================="

if [ ! -e $folder_source/*jpg ] ; then
    echo "ERROR - No Files Found $folder_source/*jpg"
    echo "        Please Investigate and Try Again"
    exit 1
fi

# Remove old working folder if it exists
if [ -d $folder_working ]; then
  echo "WARN  - Removing previous working folder " $folder_working 
  sudo rm -R $folder_working
fi

# Create a new working folder
echo "STATUS- Creating Temporary Working Folder " $folder_working
mkdir $folder_working
cd $folder_working    # change to working folder
# Create numbered soft links pointing to image files in source folder
echo "STATUS- Creating soft links"
echo "        From Source Files $folder_source/*jpg"
echo "         To   Destination $folder_working"
a=0

ls $folder_source/*jpg |
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
  echo "ERROR - avconv Encoding Failed for " $folder_destination/$moviename " Please Investigate Problem"
  echo "ERROR - Review avconv output for error messages and correct problem"
  echo "ERROR - avconv Encoding Failed for " $folder_destination/$moviename >> $error_log_file  
  exit 1
else
  echo "STATUS- Processing Completed Successfully ..."
  echo "STATUS- Deleting Working Folder " $folder_working
  sudo rm -R $folder_working
  if [ $? -ne 0 ]; then 
    echo "ERROR - Could not Delete Working Folder " $folder_working " Please Investigate ..."
    echo "ERROR - Check for permissions or other possible problems" 
    echo "============================ ERROR +======================================"           
    exit 1
  else 
    if [ "$delete_source_files" = true ] ; then
        echo "WARN  - Deleting Source Files $folder_source/*jpg"
        sudo rm $folder_source/*jpg
    fi
    echo "=========================== SUCCESS ======================================"
    echo "STATUS- Video Saved to $folder_destination/$moviename"     
  fi    
fi    
#               ------------------ End Script ----------------------------