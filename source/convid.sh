#!/bin/bash

# convid.sh - written by Claude Pageau
# This script will convert h264 files to mp4 using MP4Box
# install MP4Box per the following
# sudo apt-get install gpac
#
# The converted h264 can be deleted or renamed per del_h264 setting
#
# To Automate Add a crontab entry to crontab per the below.  
# make sure convid.sh is executable eg sudo chmod +x convid.sh
#
# crontab -e
#
# Add similar crontab entry as line below (excluding the #). 
# This would execute convid.sh every minute
#
# */1 * * * * /home/pi/pi-timolo/convid.sh > /dev/null
ver="0.7"

echo "$0 version $ver by Claude Pageau"
echo "Batch Convert h264 to MP4 using MP4Box"
echo "------------------------------------------"
cd /home/pi/pi-timolo   # change directory

# --------- Variable Settings ---------------
del_h264=true   # delete=true rename=false
source_files=/home/pi/pi-timolo/motion/*h264

command_to_run='/usr/bin/MP4Box -add '
# looking for files matching $source_files
# ls -t sorts files by last modification time, most recent to oldest
# IMPORTANT  - The latest file will not be processed since it may be being written to
ls -t $source_files |
(

  # the first line will be the most recent file

  read the_most_recent_file
  # do nothing with the most recent file: $the_most_recent_file

  # the rest of the lines will not be the most recent file

  # do something with the rest of the files
  while read not_the_most_recent_file
  do
    if [ -z "$( pgrep -f MP4Box )" ]; then   # Does file exist
        if [ ! -e $not_the_most_recent_file ]; then
            echo "ERROR  - Could Not Find File $not_the_most_recent_file"
            echo "         Please Investigate"
        else
            echo "START  - Converting $not_the_most_recent_file" 
            MP4filename=$(echo $not_the_most_recent_file | cut -f 1 -d '.')
            $command_to_run $not_the_most_recent_file $MP4filename.mp4
            if [ $? -ne 0 ] ; then
                echo "------------------------------------------"
                echo "ERROR   -  Problem running $command_to_run"
                echo "           Check if command exists"
                echo "To install MP4Box"
                echo "sudo apt-get -y install gpac"
                exit 1
            else
                touch -r $not_the_most_recent_file $MP4filename.mp4                
                if [ "$del_h264" = true ]; then                  
                    echo "STATUS - Deleting $not_the_most_recent_file"
                    rm $not_the_most_recent_file    
                else
                    echo "STATUS - Rename $not_the_most_recent_file $not_the_most_recent_file.done"
                    rm -f $not_the_most_recent_file.done
                    mv $not_the_most_recent_file $not_the_most_recent_file.done
                fi                    
            fi
            echo "DONE   - Processing of $not_the_most_recent_file"
            echo "================================================"
        fi
    else
        echo "MP4Box is Already Running ..."
    fi
  done
)
echo "$0 Done"
