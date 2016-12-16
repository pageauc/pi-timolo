#!/bin/bash
echo "$0 version 1.95 by Claude Pageau"
echo "--------------------------------------"
# --------------------------------------------------------------------
# Requires /usr/local/bin/gdrive executable compiled from github source for arm
# Note gdrive is included with pi-timolo on github at https://github.com/pageauc/pi-timolo
# for gdrive details see https://github.com/odeke-em/drive/releases
# To manually install gdrive binary perform the following.
# cd ~
# wget -O gdrive -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/gdrive_armv6
# chmod +x gdrive
# sudo cp gdrive /usr/local/bin/
# rm gdrive
# cd ~
# gdrive version
# Follow instructions for initializing gdrive for pi-timolo see pi-timolo wiki
# gdrive init
#
# This script will perform the following
# Runs gdrive only if it is not already running
# Looks for pi-timolo.sync file created by pi-timolo.py indicating there are new files to sync
# if CHECK_FOR_SYNC_FILE=true
# Kills gdrive process if it has been running too long. default is > 4000 seconds or 67 minutes
# Suggest you run this script from a crontab every 5 minutes or so.
# Add appropriate line to crontab using command sudo crontab -e
# example crontab entry below without # comment char
# */5 * * * * /home/pi/pi-timolo/sync.sh >/dev/nul
# --------------------------------------------------------------------
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # folder location of this script

# -------------------  User Variables ------------------
SYNC_DIR=motion          # relative to this script folder - location of files to sync
FILES_TO_SYNC='*jpg'     # Set the type of files to sync * for all
CHECK_FOR_SYNC_FILE=true # true if sync file required otherwise set to false
SYNC_FILE_PATH=$DIR/pi-timolo.sync  # name of pi-timolo sync lock filename
FORCE_REBOOT=false       # true to reboot if pi-timolo not running otherwise set to false
# ------------------------------------------------------

# Change directory to match google drive root (required for crontab operation
cd $DIR
function do_gdrive_sync()
{
    # Check if Local SYNC_DIR folder exists
    if [ ! -d "$DIR/$SYNC_DIR" ] ; then
        echo "ERROR   - Local Folder $DIR/$SYNC_DIR Does Not Exist"
        echo "          Please Check SYNC_DIR variable and/or Local Folder PATH"
        exit 1
    fi

    # Check for matching files to sync in folder
    ls -1 $DIR/$SYNC_DIR/$FILES_TO_SYNC > /dev/null 2>&1
    if [ ! "$?" = "0" ] ; then
        echo "ERROR   - No Matching $FILES_TO_SYNC Files Found in $DIR/$SYNC_DIR"
        exit 1
    fi

    # Check if a matching remote folder exists
    # and if Not then create one
    echo "STATUS  - Check if Remote Folder /$SYNC_DIR Exists"
    echo "------------------------------------------"
    /usr/local/bin/gdrive file-id $SYNC_DIR
    if [ ! $? -eq 0 ] ; then
        echo "------------------------------------------"
        echo "STATUS  - Creating Remote Folder /$SYNC_DIR"
        echo "------------------------------------------"
        /usr/local/bin/gdrive new --folder $SYNC_DIR
        /usr/local/bin/gdrive file-id $SYNC_DIR
        if [ $? -eq 0 ] ; then
            echo "------------------------------------------"
            echo "STATUS  - Successfully Created Remote Folder /$SYNC_DIR"
        else
            echo "------------------------------------------"
            echo "ERROR   - Problem Creating Remote Folder $SYNC_DIR"
            echo "          Please Investigate Problem"
            exit 1
        fi
    fi
    echo "------------------------------------------"
    echo "STATUS  - Start gdrive Sync ...."
    echo "STATUS  - Local Source Folder - $DIR/$SYNC_DIR"
    echo "STATUS  - Remote Destn Folder - /$SYNC_DIR"
    echo "STATUS  - Files $FILES_TO_SYNC"
    echo "STATUS  - Running"
    echo "STATUS  - sudo /usr/local/bin/gdrive push -no-prompt -ignore-conflict $SYNC_DIR/$FILES_TO_SYNC"
    echo "------------------------------------------"
    date
    START=$(date +%s)
    sudo /usr/local/bin/gdrive push -no-prompt -ignore-conflict $SYNC_DIR/$FILES_TO_SYNC
    if [ $? -ne 0 ] ;  then
        # Check if gdrive sync was successfully
        date
        echo "------------------------------------------"
        echo "ERROR   - gdrive Sync Failed."
        echo "          Possible Cause - See gdrive Error Message Above"
        echo "          Please Investigate Problem and Try Again"
    else
        # If successful then display processing time and remove sync file
        date
        END=$(date +%s)
        DIFF=$((END - START))
        echo "------------------------------------------"
        echo "STATUS  - $0 Completed Successfully"
        echo "STATUS  - Processing Took $DIFF seconds"
        if [ -e $SYNC_FILE_PATH ] ; then
            echo "STATUS  - Deleting Sync Lock File $SYNC_FILE_PATH"
            rm -f $SYNC_FILE_PATH
        fi
    fi
}

# check if gdrive is already running to avoid multiple instances
if [ -z "$(pgrep -f gdrive)" ] ; then
    if [ $CHECK_FOR_SYNC_FILE ] ; then
        echo "STATUS  - CHECK_FOR_SYNC_FILE=true (script variable)"
        if [ -e $SYNC_FILE_PATH ] ; then
            # Run gdrive for files in folder specified by variable $SYNC_DIR
            echo "STATUS  - Found File $SYNC_FILE_PATH"
            do_gdrive_sync
        else
            echo "STATUS  - File Not Found $SYNC_FILE_PATH"
            echo "STATUS  - Sync Not Required."
        fi
    else
        echo "STATUS  - CHECK_FOR_SYNC_FILE=false (script variable)"
        echo "WARNING - No Sync Lock File $SYNC_FILE_PATH Required"
        do_gdrive_sync
    fi
else
    # gdrive is already running so check how long and kill if past time limit
    sudo kill $GDRIVEPID
    if [ -z "$(sudo ps axh -O etimes | grep gdrive | grep -v grep | sed 's/^ *//'| awk '{if ($2 >= 4000) print $1}')" ]
    then
        RUNTIME=$(sudo ps axh -O etimes | grep gdrive | grep -v grep | sed 's/^ *//' | awk '{if ($2 > 0) print $2}' | head -1)
        echo "STATUS  - Another sync.sh has run for "$RUNTIME" seconds."
        echo "          Will kill if greater than 4000 seconds."
    else
        GDRIVEPID=$(pgrep gdrive)
        echo "WARNING - gdrive has run longer than 4000 seconds so kill PID $GDRIVEPID"
        echo "          Killing $GDRIVEPID"
    fi
fi

if $FORCE_REBOOT ; then  # check if reboot required
    echo "STATUS  - Check pi-timolo.py Run Status ..."
    if [ -z "$(pgrep -f pi-timolo.py)" ] ; then
        echo "STATUS  - pi-timolo.py is NOT Running so reboot"
        echo "STATUS  - ctrl-c to Abort Reboot."
        echo "STATUS  - Reboot in 15 seconds Waiting ...."
        sleep 10
        echo "WARNING - Rebooting in 5 seconds"
        sleep 5
        sudo reboot
    else
        APPPID=$(pgrep -f pi-timolo.py)
        echo "STATUS  - pi-timolo.py is Running PID $APPPID"
    fi
fi
echo ""
echo "Done ..."
exit
