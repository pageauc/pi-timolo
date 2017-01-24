#!/bin/bash

# convid.sh - written by Claude Pageau
#
# This script will convert h264 files to mp4 using MP4Box
# The converted h264 can be deleted or renamed per del_h264 setting
#
# gpac is installed by default by latest pi-timolo-install.sh script
# To manually install MP4Box execute the following command
# sudo apt-get install gpac
#
#
# convid.sh  can join multiple mp4 videos into one bigger datetime named
# Output file and optionally delete source files.  This is handy
# to preserver archives when pi-timolo.py is set to recycle filenames
#
# To Automate convid.sh, Add a crontab entry to crontab per the below.
# make sure convid.sh is executable eg sudo chmod +x convid.sh
#
# cd ~/pi-timolo
# sudo crontab -e
#
# Add similar crontab entry as line below (excluding the #).
# This would execute convid.sh join once a day at 10pm
#
# 0 22 * * * su pi -c "/home/pi/pi-timolo/convid.sh join > /dev/null"

ver="4.00"
echo "================================================"
echo "$0 version $ver  written by Claude Pageau"

# Get current folder of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

if [ -e convid.conf ] ; then
   source $DIR/convid.conf
else
   echo "INFO  - Attempting to download convid.conf from GitHub"
   echo "INFO  - Please Wait ...."
   wget https://raw.github.com/pageauc/pi-timolo/master/source/convid.conf
   if [ -e convid.conf ] ; then
      source $DIR/convid.conf
   else
      echo "ERROR  - $DIR/convid.conf File Not Found."
      echo "ERROR  - Could Not Import $0 variables"
      echo "ERROR  - Please Investigate or Download file from GitHub Repo"
      echo "ERROR  - https://github.com/pageauc/pi-timolo"
      exit 1
    fi
fi

#---------------------------------------------
function convert ()  # Convert param single h264 file to MP4
{
    fileparam=$1

    if [ ! -e $fileparam ]; then
        echo "ERROR  - Could Not Find File" $fileparam
        echo "         Please Investigate"
    else
        echo "STATUS - Now Converting $fileparam"
        MP4filename=$(echo $fileparam | cut -f 1 -d '.')
        $command_to_run $fileparam $MP4filename.mp4
        if [ $? -ne 0 ] ; then
            echo "ERROR   -  Problem running $command_to_run"
            echo "           Check if command exists"
            echo "To install MP4Box"
            echo "sudo apt-get -y install gpac"
            exit 1
        else
           # sync mp4 file dates from corresponding h264 file
           /bin/touch -r $fileparam $MP4filename.mp4
           if [ "$del_h264" = true ]; then
                echo "STATUS - Deleting" $fileparam
                rm $fileparam
            else
                echo "STATUS - Rename" $fileparam
                echo "STATUS -   To  " $fileparam".done"
                rm -f $fileparam.done
                mv $fileparam $fileparam.done
            fi
        fi
        echo "STATUS - Successfully Converted" $fileparam
        echo "================================================"
    fi
}

#---------------------------------------------
function convertall ()
{
    echo "Start Batch Convert of All h264 to mp4"
    echo "================================================"
    if ls $source_h264 1> /dev/null 2>&1; then
        echo "WARN  - The most recent file may still be Recording so"
        echo "WARN  - Wait 15 seconds Before Processing."
        sleep 15   # Wait in case video is in progress

        # Convert all h264 files to mp4 and optionally delete h264
        if ls $source_h264 1> /dev/null 2>&1; then
            echo "STATUS- Found $source_h264 Files"
            ls -t $source_h264 |
            (
              while read next_h264_file
              do
                 if [ -e $next_h264_file ] ; then
                     convert $next_h264_file
                 else
                     echo "WARN  - File Not Found" $next_h264_file
                 fi
              done
            )
        else
            echo "WARN  - No" $source_h264 "Files Found to Process."
        fi
    else
        echo "STATUS - No" $source_h264 "Files Found to Process."
    fi
}

#---------------------------------------------
function joinvideo ()
{
    echo "Batch Join MP4 Videos Using MP4Box"
    echo "================================================"
    if ls $source_mp4/*mp4 1> /dev/null 2>&1 ; then
        total_mp4=$(ls $source_mp4 | grep mp4 -wc)
        if [ $total_mp4 -le 2 ] ; then
            echo "ERROR  - You Must Have at Least Two mp4 Files to Join"
            exit 1
        fi
    else
        echo "WARN  - No $source_mp4 Files Found to Process."
        exit 0
    fi

    ls -t $source_mp4/*mp4 |
    (
      # the first line will be the most recent file
      read the_first_mp4
      # Create a file name based on the date of current file
      # This keeps video file name date time more in line with original record date time
      date=$(stat $the_first_mp4 | grep Modify | cut -f 2 -d ' ')
      year=$(echo $date | cut -f 1 -d '-')
      month=$(echo $date | cut -f 2 -d '-')
      day=$(echo $date | cut -f 3 -d '-')
      time=$(stat $the_first_mp4 | grep Modify | cut -f 3 -d ' ' | cut -f 1 -d '.')
      H=$(echo $time | cut -f 1 -d ':')
      M=$(echo $time | cut -f 2 -d ':')
      S=$(echo $time | cut -f 3 -d ':')
      videoname=$video_prefix"_"$year$month$day"_"$H$M$S".mp4"
      total_mp4=$(ls $source_mp4/*mp4 | grep mp4 -wc)
      echo "STATUS - Input Files" $source_mp4"/*mp4"
      echo "STATUS - Output File" $dest_mp4/$videoname
      echo "STATUS - max_joins="$max_joins "per Output Video File"
      echo "==============================================="
      echo $the_first_mp4 "May Still be Recording"
      echo "STATUS - Wait 15 seconds Before Processing."
      sleep 15   # Wait in case video is in progress
      echo "==============================================="
      echo "STATUS - Start Processing Video Joins"
      echo "STATUS - Initialize Join with" $the_first_mp4
      cp $the_first_mp4 $DIR/$videoname
      cp $DIR/$videoname $DIR/tmp_$videoname
      rm $the_first_mp4
      cur_joins=2
      loop_cnt=2
      # Process the rest of the files
      while read the_next_mp4
      do
        if [ $loop_cnt -ge $total_mp4 ]; then
            echo "STATUS - Total  " $loop_cnt "of" $total_mp4
            echo "STATUS - Current" $cur_joins "of" $max_joins
            echo "STATUS - Next File " $the_next_mp4
            echo "STATUS - Joining To" $DIR/$videoname
            echo "==============================================="
            /usr/bin/MP4Box -add $the_next_mp4 -cat $DIR/$videoname -new $DIR/tmp_$videoname
            echo "==============================================="
            echo "STATUS - Moving" $DIR/$videoname
            echo "STATUS -   To  " $dest_mp4/$videoname
            rm $the_next_mp4
            rm $DIR/$videoname
            mv $DIR/tmp_$videoname $dest_mp4/$videoname
            if [ -e $dest_mp4/$videoname ] ; then
                echo "STATUS - Success ...."
                echo "STATUS - Video Saved To" $dest_mp4/$videoname
            else
                echo "ERROR  - Problem Moving" $DIR/tmp_$videoname
                echo "ERROR  - Please Investigate Problem"
            fi
            echo "==============================================="
        elif [ $cur_joins -ge $max_joins ] ; then
            # Move current Ouput video and Prepare next Output Video
            /bin/touch -r $the_next_mp4 $DIR/$videoname
            echo "STATUS - Moving" $DIR/$videoname
            echo "           To  " $dest_mp4/$videoname
            mv $DIR/$videoname $dest_mp4/$videoname
            date=$(stat $the_next_mp4 | grep Modify | cut -f 2 -d ' ')
            year=$(echo $date | cut -f 1 -d '-')
            month=$(echo $date | cut -f 2 -d '-')
            day=$(echo $date | cut -f 3 -d '-')
            time=$(stat $the_next_mp4 | grep Modify | cut -f 3 -d ' ' | cut -f 1 -d '.')
            H=$(echo $time | cut -f 1 -d ':')
            M=$(echo $time | cut -f 2 -d ':')
            S=$(echo $time | cut -f 3 -d ':')
            videoname=$video_prefix"_"$year$month$day"_"$H$M$S".mp4"
            echo "STATUS - Next Output Video is" $DIR/$videoname
            echo "STATUS - Initialize Join with" $the_next_mp4
            cp $the_next_mp4 $DIR/$videoname
            cp $DIR/$videoname $DIR/tmp_$videoname
            rm $the_next_mp4
            # Process loop and join counters
            loop_cnt=$[$loop_cnt +1]
            cur_joins=2
        else
            # Join Source mp4's to Output mp4
            cur_joins=$[$cur_joins +1]
            loop_cnt=$[$loop_cnt +1]
            echo "STATUS - Total  " $loop_cnt "of" $total_mp4
            echo "STATUS - Current" $cur_joins "of" $max_joins
            echo "STATUS - Next File " $the_next_mp4
            echo "STATUS - Joining To" $DIR/$videoname
            echo "==============================================="
            /usr/bin/MP4Box -add $the_next_mp4 -cat $DIR/$videoname -new $DIR/tmp_$videoname
            echo "==============================================="
            rm $DIR/$videoname
            mv $DIR/tmp_$videoname $DIR/$videoname
            rm $the_next_mp4
        fi
      done
    )
}

# ------------------ Start Main Script ------------------
if [ -z $1 ] ;  then

   # Display convid.sh Variable Settings
   echo ""
   echo "         H264 Conversion Variable Settings"
   echo "         ---------------------------------"
   echo "source_h264="$source_h264
   echo "del_h264="$del_h264
   echo ""
   echo "           MP4 Join Variable Settings"
   echo "           --------------------------"
   echo "max_joins="$max_joins
   echo "source_mp4="$source_mp4
   echo "dest_mp4="$dest_mp4
   echo "video_prefix="$video_prefix
   echo "command_to_run="$command_to_run
   echo ""
   echo "================================================"
   echo "This utility can"
   echo "1) convert - h264 files to mp4 format"
   echo "   Individually or for all files in specified folder per source_h264 variable"
   echo "   To remove original h264 set variable del_h264=true (default)"
   echo ""
   echo "2) join - specified number of mp4 videos into larger datetime stamped video files"
   echo "   per variable  max_joins=" $max_joins
   echo "   IMPORTANT - Original mp4's Will be Deleted After the Join"
   echo ""
   echo "           $0  Syntax"
   echo ""
   echo "You Must Specify a Valid Parameter per"
   echo ""
   echo "filepath - convert h264 file per filepath  NOTE - Original filename will be preserved"
   echo "all      - converts all h264 files in folder per variable source_h264"
   echo "join     - Joins all mp4 files into a dated mp4 per specified max_joins variable"
   echo ""
   echo "Examples"
   echo "           ./convid motion/mo-cam1-1234.h264"
   echo "           ./convid convert"
   echo "           ./convid join"
   echo ""
   echo "use nano convid.sh to customize the variable settings near the top of this file"
   echo "For More Details See pi-timolo Wiki Here https://github.com/pageauc/pi-timolo/wiki"

elif [ "$1" = "join" ] ; then
    joinvideo
elif [ "$1" = "convert" ] ; then
    convertall  
elif [ -e $1 ] ; then
    convert $1
else
   echo "STATUS - $1 File Not Found"
fi
echo ""
echo "$0 Done"
