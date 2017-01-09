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
ver="0.8"

echo "$0 version $ver by Claude Pageau"
echo "Batch Convert h264 to MP4 using MP4Box"
echo "------------------------------------------"

# Get current folder of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# Variable Settings
del_h264=true     # delete=true rename=false
source_files=/home/pi/pi-timolo/motion/*h264

command_to_run='/usr/bin/MP4Box -add '

# looking for files matching $source_files
# ls -t sorts files by last modification time, most recent to oldest
# IMPORTANT  - The latest file will not be processed since it may be being written to

function convert ()  #Convert h264 file to MP4
{
     file=$1
     if [ -z "$( pgrep -f MP4Box )" ]; then   # Does file exist
        if [ ! -e $file ]; then
            echo "ERROR  - Could Not Find File $file"
            echo "         Please Investigate"
        else
            echo "START  - Converting $file"
            MP4filename=$(echo $file | cut -f 1 -d '.')
            $command_to_run $file $MP4filename.mp4
            if [ $? -ne 0 ] ; then
                echo "------------------------------------------"
                echo "ERROR   -  Problem running $command_to_run"
                echo "           Check if command exists"
                echo "To install MP4Box"
                echo "sudo apt-get -y install gpac"
                exit 1
            else
                /bin/touch -r $file $MP4filename.mp4
                if [ "$del_h264" = true ]; then
                    echo "STATUS - Deleting $not_the_most_recent_file"
                    rm $file
                else
                    echo "STATUS - Rename $file $file.done"
                    rm -f $file.done
                    mv $file $file.done
                fi
            fi
            echo "DONE   - Processing of $file"
            echo "================================================"
        fi
    else
        echo "MP4Box is Already Running ..."
    fi
}

#Check if there are files to process
if ls $source_files 1> /dev/null 2>&1; then
    echo "STATUS- Found $source_files Files"
else
    echo "WARN  - No $source_files Files Found to Process."
    exit
fi

ls -t $source_files |
(
  # the first line will be the most recent file
  read the_most_recent_file
  echo $the_most_recent_file "May Still be Recording"
  echo "Wait 15 seconds Before Processing."
  sleep 15   # Wait in case video is in progress
  convert $the_most_recent_file
  # Process the rest of the files
  while read not_the_most_recent_file
  do
     convert $not_the_most_recent_file
  done
)

echo "$0 Done"
