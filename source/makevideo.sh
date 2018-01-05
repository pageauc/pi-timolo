#!/bin/bash
ver="5.00"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # get cur dir of this script
progName=$(basename -- "$0")
cd $DIR
echo "INFO  : $progName $ver  written by Claude Pageau"

# Note - makevideo.sh variables are in video.conf
# To install/update avconv execute the following command in RPI terminal session
#
# sudo apt-get install libav-tools
#
# For more details see GitHub Wiki here
# https://github.com/pageauc/pi-timolo/wiki/Utilities

# get current working folder that this script was launched from

if [ -f video.conf ] ; then
   source $DIR/video.conf
else
   echo "INFO  : Attempting to download video.conf from GitHub"
   echo "INFO  : Please Wait ...."
   wget https://raw.github.com/pageauc/pi-timolo/master/source/video.conf

   if [ -f video.conf ] ; then
      source $DIR/video.conf
   else
      echo "ERROR : $DIR/video.conf File Not Found."
      echo "        Could Not Import $progName variables"
      echo "        Please Investigate or Download file from GitHub Repo"
      echo "        https://github.com/pageauc/pi-timolo"
      exit 1
   fi
fi

# ------------- Start Script ------------------

#  Script variables
tl_folder_working="$DIR/makevideo_tmp"
tl_error_log_file="$DIR/makevideo_error.log"
tl_source_files=$DIR/$tl_folder_source/*$tl_files_ext  # Files wildcard that we are looking for

# Output videoname with prefix and date and time (minute only).
# Video can be specified as avi or mp4
tl_videoname=$tl_video_prefix$(date '+%Y%m%d-%H%M').mp4

clear
echo "$progName $ver  written by Claude Pageau
============ TIMELAPSE VIDEO SETTINGS ====================================
tl_videoname             : $tl_videoname
tl_files_ext             : $tl_files_ext
tl_files_sort            : $tl_files_sort
tl_folder_source         : $tl_folder_source
tl_folder_destination    : $tl_folder_destination
tl_archive_source_files  : $tl_archive_source_files
tl_archive_dest_folder   : $tl_archive_dest_folder
tl_delete_source_files   : $tl_delete_source_files
tl_share_copy_on         : $tl_share_copy_on
tl_share_destination     : $tl_share_destination
==========================================================================
Working ..."

# Check if source folder exists
if [ ! -d $tl_folder_source ] ; then
    echo "ERROR : Source Folder" $tl_folder_source "Does Not Exist"
    echo "        Check $0 Variable folder_source and Try Again"
    echo "ERROR : Source Folder $tl_folder_source Does Not Exist." >> $tl_error_log_file
    exit 1
fi

# Check if source files exist
if ! ls $tl_source_files 1> /dev/null 2>&1 ; then
    echo "ERROR : No Source Files Found in $tl_source_files"
    echo "        Please Investigate and Try Again"
    exit 1
fi

# Create destination folder if it does not exist
if [ ! -d $tl_folder_destination ] ; then
    mkdir $tl_folder_destination
    if [ "$?" -ne 0 ]; then
        echo "ERROR : Problem Creating Destination Folder" $tl_folder_destination
        echo "        If destination is a remote folder or mount then check network, destination IP address, permissions, Etc"
        echo "ERROR : mkdir Failed - $tl_folder_destination Could NOT be Created." >> $tl_error_log_file
        exit 1
    fi
fi

# Create Archive subfolder if archiving enabled One Folder per day
if [ "$tl_archive_source_files" = true ] ; then    # Check if archiving enabled
    if [ ! -d $tl_archive_dest_folder ] ; then  # Check if archive folder exists
        echo "ERROR : Archive Folder" $tl_archive_dest_folder "Does Not Exist"
        echo "        Check $0 Variable tl_archive_dest_folder and Try Again"
        echo "ERROR : Archive Folder $tl_archive_dest_folder Does Not Exist." >> $tl_error_log_file
        exit 1
    fi
    # create date/time stamped subfolder
    subfolderName=$(date '+%Y-%m-%d')  # Dated subfolder name Year/Month/Day  One per day
    if [ ! -d $tl_archive_dest_folder/$subfolderName ] ; then
        echo "INFO  : Create subfolder $tl_archive_dest_folder/$subfolderName"
        mkdir -p $tl_archive_dest_folder/$subfolderName
        if [ ! -d $tl_archive_dest_folder/$subfolderName ] ; then
            echo "ERROR : subfolder create Failed $tl_archive_dest_folder/$subfolderName"
            echo "ERROR : subfolder create Failed $tl_archive_dest_folder/$subfolderName" >> $tl_error_log_file
            exit 1
        fi
    fi
fi

# Remove old working folder if it exists
if [ -d $tl_folder_working ] ; then
    echo "WARN  : Removing previous working folder $tl_folder_working"
    rm -R $tl_folder_working
fi

# Create a new temporary working folder to store soft links
# that are numbered sequentially in case source number has gaps
echo "INFO  : Creating Temporary Working Folder $tl_folder_working"
mkdir $tl_folder_working
if [ ! -d $tl_folder_working ] ; then
    echo "ERROR : Problem Creating Temporary Working Folder $tl_folder_working"
    echo "ERROR : mkdir Failed - $tl_folder_working Could NOT be Created." >> $tl_error_log_file
    exit 1
fi

cd $tl_folder_working    # change to working folder
# Create numbered soft links in working folder that point to image files in source folder
echo "INFO  : Creating Image File Soft Links"
echo "        From  $tl_folder_source"
echo "        To    $tl_folder_working"
a=0
ls $tl_files_sort $tl_source_files |
(
  # the first line will be the most recent file so ignore it
  # since it might still be in progress
  read the_most_recent_file
  # Skip this file in listing
  # create sym links in working folder for the rest of the files
  while read not_the_most_recent_file
  do
    new=$(printf "%05d.$tl_files_ext" ${a}) #05 pad to length of 4 max 99999 images
    ln -s ${not_the_most_recent_file} ${new}
    let a=a+1
  done
)
cd $DIR      # Return back to launch folder

echo "=========================================================================="
echo "Making Video ... "$tl_videoname
echo "=========================================================================="
/usr/bin/avconv -y -f image2 -r $tl_fps -i $tl_folder_working/%5d.$tl_files_ext -aspect $tl_a_ratio -s $tl_vid_size $tl_folder_destination/$tl_videoname
if [ $? -ne 0 ] ; then
  echo "ERROR : avconv Encoding Failed for" $tl_folder_destination/$tl_videoname
  echo "        Review avconv output for Error Messages and Correct Problem"
  echo "ERROR : avconv Encoding Failed for" $tl_folder_destination/$tl_videoname >> $tl_error_log_file
  exit 1
else
  echo "=========================================================================="
  echo "INFO  : Video Saved to" $tl_folder_destination/$tl_videoname

  # Process archive, delete or do nothing for encoded source image files
  if [ "$tl_archive_source_files" = true ] ; then    # Check if archiving enabled
    echo "INFO  : Archive Enabled per tl_archive_source_files="$tl_archive_source_files
    echo "INFO  : Archive Files from $tl_folder_source to $tl_archive_dest_folder/$subfolderName"
    echo "INFO  : This will Take Some Time.  Wait ...."
    ls $tl_folder_working |     # get directory listing of working folder symlinks
    (
      while read linkFile
      do
        imageFilePath=$( readlink -f $tl_folder_working/$linkFile )  # read symlink for full path to image file
        imageFilename=$(basename $imageFilePath)
        # echo "INFO  - Move $imageFilePath to $tl_archive_dest_folder"
        cp -p  $imageFilePath $tl_archive_dest_folder/$subfolderName # copy image file and preserve timestamp
        if [ -e $tl_archive_dest_folder/$subfolderName/$imageFilename ] ; then
            rm -f $imageFilePath   # Remove original image file without prompt
            if [ -e $imageFilePath ] ; then
                echo "ERROR : Delete Failed $imageFilePath.  Please Investigate ..."
                echo "ERROR : Delete Failed $imageFilePath.  Please Investigate ..." >> $tl_error_log_file
            fi
        else
            echo "ERROR : Copy Failed $imageFilePath to $tl_archive_dest_folder/$subfolderName"
            echo "ERROR : Copy Failed $imageFilePath to $tl_archive_dest_folder/"$subfolderName >> $tl_error_log_file
        fi
      done
    )
  elif [ "$tl_delete_source_files" = true ] ; then   # Check if delete source files is enabled
    echo "WARN  : Variable tl_delete_source_files : $tl_delete_source_files"
    echo "WARN  : Start Deleting Encoded Source Files in $tl_folder_source"
    ls $tl_folder_working |    # get directory listing of working folder symlinks
    (
      while read linkFile
      do
        imageFile=$(readlink -f $tl_folder_working/$linkFile)
        echo "WARN  : Deleting $imageFile"
        rm -f $imageFile
        if [ -e $imageFile ] ; then
            echo "ERROR : Delete Failed for $imageFile"
            echo "ERROR : Delete Failed for $imageFile" >> $tl_error_log_file
        fi
      done
    )
  fi

  echo "INFO  : Deleting Working Folder" $tl_folder_working
  rm -R $tl_folder_working
  if [ $? -ne 0 ] ; then
    echo "ERROR : Could not Delete Working Folder $tl_folder_working"
    echo "        Check for permissions or other possible problems"
    echo "ERROR : Could not Delete Working Folder" $tl_folder_working >> $tl_error_log_file
    exit 1
  fi
fi

# Check if video file is to be copied to a network share
if [ "$tl_share_copy_on" = true ] ; then
  echo "INFO  : Copy Video File"
  echo "        From: $tl_folder_destination/$tl_videoname"
  echo "        To  : $tl_share_destination"

  if grep -qs "$tl_share_destination" /proc/mounts; then
    echo "INFO  : $tl_share_destination is Mounted."
  else
    echo "ERROR : Cannot Copy File to Share Folder"
    echo "        Failed to Copy" $tl_folder_destination/$tl_videoname "to" $tl_share_destination "Because It is NOT Mounted"
    echo "        Please Investigate Mount Problem and Try Again"
    echo "        Once Resolved You Will Need to Manually Transfer Previous Video Files"
    echo "ERROR : Failed to Copy" $tl_folder_destination/$tl_videoname "to" $tl_share_destination "Because It is NOT Mounted" >> $tl_error_log_file
    exit 1
  fi

  cp -p $tl_folder_destination/$tl_videoname $tl_share_destination
  if [ $? -ne 0 ]; then
    echo "ERROR : Copy Failed $tl_folder_destination/$tl_videoname to" $tl_share_destination/$tl_videoname
    echo "        If destination is a remote folder or mount then check network, destination IP address, permissions, Etc"
    echo "ERROR : Copy Failed from" $tl_folder_destination/$tl_videoname "to" $tl_share_destination/$tl_videoname >> $tl_error_log_file
    exit 1
  else
    if [ -e $tl_share_destination/$tl_videoname ] ; then
      echo "INFO  : Successfully Moved Video"
      echo "        From $tl_folder_destination/$tl_videoname"
      echo "        To   $tl_share_destination/$tl_videoname"
      echo "WARN  : Deleting Local Video File $tl_folder_destination/$tl_videoname"
      rm -f $tl_folder_destination/$tl_videoname
      if [ -e $tl_folder_destination/$tl_videoname ] ; then
        echo "ERROR : Could Not Delete" $tl_folder_destination/$tl_videoname "After Copy To" $tl_share_destination/$tl_videoname
        echo "        Please Investigate"
        echo "ERROR : Could Not Delete" $tl_folder_destination/$tl_videoname "After Copy To" $tl_share_destination/$tl_videoname >> $tl_error_log_file
        exit 1
      fi
    else
      echo "ERROR : Problem copying $tl_folder_destination/$tl_videoname to $tl_share_destination/$tl_videoname"
      echo "        If destination is a remote folder or mount then check network, destination IP address, permissions, Etc"
      echo "ERROR : Copy Failed from" $tl_folder_destination/$tl_videoname "to" $tl_share_destination/$tl_videoname >> $tl_error_log_file
      exit 1
    fi
  fi
fi
echo "INFO  : Processing Completed Successfully ..."
echo "=========================================================================="
echo "$progName Done"
#------------------ End do_timelapse_video Script ------------------------

