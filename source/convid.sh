#!/bin/bash
ver="5.00"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # get cur dir of this script
progName=$(basename -- "$0")
cd $DIR
echo "================================================"
echo "INFO  : $progName $ver  written by Claude Pageau"

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

# Get current folder of this script
if [ -f video.conf ] ; then
   source $DIR/video.conf
else
   echo "INFO  : Attempting to download convid.conf from GitHub"
   echo "INFO  : Please Wait ...."
   wget video.conf https://raw.github.com/pageauc/pi-timolo/master/source/video.conf
   if [ -e video.conf ] ; then
      source $DIR/video.conf
   else
      echo "ERROR : $DIR/video.conf File Not Found."
      echo "        Could Not Import $progName variables"
      echo "        Please Investigate or Download file from GitHub Repo"
      echo "        https://github.com/pageauc/pi-timolo"
      exit 1
    fi
fi

#---------------------------------------------
function convert ()  # Convert param single h264 file to MP4
{
    h264_fpath=$1

    if [ ! -e $h264_fpath ]; then
        echo "ERROR : Could Not Find File" $h264_fpath
        echo "        Please Investigate"
    else
        mkdir -p $mp4_work  # create if does not exist
        mkdir -p $mp4_dest  # create a destination dir if it does not exist
        h264_fname=$(basename "${h264_fpath}")  # get filename from h264_fpath
        base_fname=$(echo $h264_fname | cut -f 1 -d '.')
        mp4_fname=$base_fname.mp4
        echo "INFO  : Copy $h264_fpath $mp4_work/$h264_fname"
        cp -p $h264_fpath $mp4_work/$h264_fname
        if [ $? -ne 0 ] ; then
            echo "ERROR : Failed cp -p $h264_fpath $mp4_work/$h264_fname"
        fi
        echo "INFO  : Converting $mp4_work/$h264_fname"
        echo "INFO  : $command_to_run -add $mp4_work/$h264_fname:fps=$mp4_fps -new $mp4_work/$mp4_fname"
        $command_to_run -add $mp4_work/$h264_fname:fps=$mp4_fps -new $mp4_work/$mp4_fname
        if [ $? -ne 0 ] ; then
            echo "ERROR :  Problem running $command_to_run"
            echo "         Check if command exists"
            echo "To install MP4Box"
            echo "sudo apt-get -y install gpac"
            exit 1
        else
            echo "INFO  : Copy $mp4_work/$mp4_fname $mp4_dest$mp4_fname"
            cp -p $mp4_work/$mp4_fname $mp4_dest/$mp4_fname
            if [ $? -ne 0 ] ; then
                echo "ERROR : Failed cp -p $mp4_work/$mp4_fname $mp4_dest/$mp4_fname"
            else
                /bin/touch -r $h264_fpath $mp4_dest/$mp4_fname
                echo "INFO  : Delete $mp4_work/$h264_fname"
                rm -f $mp4_work/$mp4_fname
                if [ $? -ne 0 ] ; then
                    echo "ERROR : Failed rm -f $mp4_work/$mp4_fname"
                fi
                rm -f $mp4_work/$h264_fname
                if [ "$mp4_del_h264" = true ]; then
                    echo "INFO  : Delete $h264_fpath"
                    rm -f $h264_fpath
                else
                    echo "INFO  : Copy $h264_fpath $h264_fpath.done"
                    cp -p $h264_fpath $h264_fpath.done
                    if [ $? -ne 0 ] ; then
                        echo "ERROR : Failed cp -p $h264_fpath $h264_fpath.done"
                    else
                        echo "INFO  : Delete $h264_fpath"
                        rm -f $h264_fpath
                    fi
                fi
            fi
        fi
        echo "INFO  : Saved $mp4_dest/$mp4_fname"
        echo "================================================"
    fi
}

#---------------------------------------------
function convertall ()
{
    echo "Start Batch Convert of All h264 to mp4"
    echo "================================================"
    if ls $mp4_source_h264 1> /dev/null 2>&1; then
        echo "WARN  : The most recent file may still be Recording so"
        echo "        Wait 15 seconds Before Processing."
        sleep 15   # Wait in case video is in progress

        # Convert all h264 files to mp4 and optionally delete h264
        if ls $mp4_source_h264 1> /dev/null 2>&1; then
            echo "INFO  : Found $mp4_source_h264 Files"
            ls -t $mp4_source_h264 |
            (
              while read next_h264_file
              do
                 if [ -e $next_h264_file ] ; then
                     convert $next_h264_file
                 else
                     echo "WARN  : File Not Found" $next_h264_file
                 fi
              done
            )
        else
            echo "WARN  : No" $mp4_source_h264 "Files Found to Process."
        fi
    else
        echo "INFO  : No" $mp4_source_h264 "Files Found to Process."
    fi
}

#---------------------------------------------
function joinvideo ()
{
    echo "Batch Join MP4 Videos Using MP4Box"
    echo "================================================"
    if ls $mp4_source/*mp4 1> /dev/null 2>&1 ; then
        total_mp4=$(ls $mp4_source | grep mp4 -wc)
        if [ $total_mp4 -le 2 ] ; then
            echo "ERROR : You Must Have at Least Two mp4 Files to Join"
            exit 1
        fi
    else
        echo "WARN  : No $mp4_source Files Found to Process."
        exit 0
    fi

    ls -t $mp4_source/*mp4 |
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
      videoname=$mp4_video_prefix"_"$year$month$day"_"$H$M$S".mp4"
      total_mp4=$(ls $mp4_source/*mp4 | grep mp4 -wc)
      echo "INFO  : Input Files $mp4_source/*mp4"
      echo "        Output File $mp4_dest/$videoname"
      echo "        mp4_max_joins=$mp4_max_joins per Output Video File"
      echo "==============================================="
      echo $the_first_mp4 "May Still be Recording"
      echo "INFO  : Wait 15 seconds Before Processing."
      sleep 15   # Wait in case video is in progress
      echo "==============================================="
      echo "INFO  : Start Processing Video Joins"
      echo "INFO  : Initialize Join with" $the_first_mp4
      cp $the_first_mp4 $DIR/$videoname
      cp $DIR/$videoname $DIR/tmp_$videoname
      rm $the_first_mp4
      cur_joins=2
      loop_cnt=2
      # Process the rest of the files
      while read the_next_mp4
      do
        if [ $loop_cnt -ge $total_mp4 ]; then
            echo "INFO  : Total  " $loop_cnt "of" $total_mp4
            echo "        Current" $cur_joins "of" $mp4_max_joins
            echo "        Next File " $the_next_mp4
            echo "        Joining To" $DIR/$videoname
            echo "==============================================="
            /usr/bin/MP4Box -add $the_next_mp4 -cat $DIR/$videoname -new $DIR/tmp_$videoname
            echo "==============================================="
            echo "INFO  : Moving" $DIR/$videoname
            echo "          To  " $mp4_dest/$videoname
            rm $the_next_mp4
            rm $DIR/$videoname
            mv $DIR/tmp_$videoname $mp4_dest/$videoname
            if [ -e $mp4_dest/$videoname ] ; then
                echo "INFO  : Saved $mp4_dest/$videoname"
            else
                echo "ERROR : Problem Moving $DIR/tmp_$videoname"
            fi
            echo "==============================================="
        elif [ $cur_joins -ge $mp4_max_joins ] ; then
            # Move current Ouput video and Prepare next Output Video
            /bin/touch -r $the_next_mp4 $DIR/$videoname
            echo "INFO  : Moving" $DIR/$videoname
            echo "          To  " $mp4_dest/$videoname
            mv $DIR/$videoname $mp4_dest/$videoname
            date=$(stat $the_next_mp4 | grep Modify | cut -f 2 -d ' ')
            year=$(echo $date | cut -f 1 -d '-')
            month=$(echo $date | cut -f 2 -d '-')
            day=$(echo $date | cut -f 3 -d '-')
            time=$(stat $the_next_mp4 | grep Modify | cut -f 3 -d ' ' | cut -f 1 -d '.')
            H=$(echo $time | cut -f 1 -d ':')
            M=$(echo $time | cut -f 2 -d ':')
            S=$(echo $time | cut -f 3 -d ':')
            videoname=$mp4_video_prefix"_"$year$month$day"_"$H$M$S".mp4"
            echo "INFO  : Next Output Video is" $DIR/$videoname
            echo "INFO  : Initialize Join with" $the_next_mp4
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
            echo "INFO  : Total  " $loop_cnt "of" $total_mp4
            echo "        Current" $cur_joins "of" $mp4_max_joins
            echo "        Next File " $the_next_mp4
            echo "        Joining To" $DIR/$videoname
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
   echo "
       H264 Conversion Variable Settings
       ---------------------------------
 mp4_source_h264  : $mp4_source_h264
 mp4_del_h264     : $mp4_del_h264

           MP4 Join Variable Settings
           --------------------------
 mp4_max_joins    : $mp4_max_joins
 mp4_source       : $mp4_source
 mp4_dest         : $mp4_dest
 mp4_video_prefix : $mp4_video_prefix
 command_to_run   : $command_to_run

 ================================================
 This utility can
 1) convert - h264 files to mp4 format
    Individually or for all files in specified folder per source_h264 variable
    To remove original h264 set variable del_h264=true (default)

 2) join - specified number of mp4 videos into larger datetime stamped video files
    per variable  mp4_max_joins= $mp4_max_joins
    IMPORTANT - Original mp4's Will be Deleted After the Join

        $0  Syntax

You Must Specify a Valid Parameter per

filepath - convert h264 file per filepath  NOTE - Original filename will be preserved
all      - converts all h264 files in folder per variable source_h264
join     - Joins all mp4 files into a dated mp4 per specified mp4_max_joins variable

Examples
       ./convid motion/mo-cam1-1234.h264
           ./convid convert
           ./convid join

use nano convid.sh to customize the variable settings near the top of this file
For More Details See pi-timolo Wiki Here https://github.com/pageauc/pi-timolo/wiki
"

elif [ "$1" = "join" ] ; then
    joinvideo
elif [ "$1" = "convert" ] ; then
    convertall
elif [ -f $1 ] ; then
    convert $1
else
   echo "INFO - $1 File Not Found"
fi
echo "$progName Done"
