#!/bin/bash
# version 1.4
# sync.sh written by Claude Pageau.  Requires /usr/local/bin/gdrive executable compiled from github source for arm
# Note gdrive is included with pi-timolo on github at https://github.com/pageauc/pi-timolo
# for gdrive details see https://github.com/odeke-em/drive
# To manually install gdrive binary perform the following.
# cd /tmp
# wget https://github.com/odeke-em/drive/releases/download/v0.2.2-arm-binary/drive-arm-binary
# chmod +x drive-arm-binary
# sudo cp drive-arm-binary /usr/local/bin/gdrive
# cd ~
# gdrive version
# Follow instructions for initializing gdrive for pi-timolo
# gdrive init
#
# This script will perform the following
# Runs gdrive only if it is not already running
# Looks for pi-timolo.sync file created by pi-timolo.py indicating there are new files to sync
# Kills gdrive process if it has been running too long. default is > 600 seconds or 10 minutes
# Suggest you run this script from a crontab every 5 minutes or so.
# Add appropriate line to crontab using command sudo crontab -e
# example crontab entry below without # comment char
# */5 * * * * /home/pi/sync.sh >/dev/nul

# pi-timolo subfolder where motion files are located
SYNC_DIR=motion

echo "$0 version 1.4" 
# Get current folder where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# name of pi-timolo sync file
SYNC_FILE=pi-timolo.sync
# check if gdrive is already running to avoid multiple instances
if [ -z "$(pgrep gdrive)" ]
  then
    # Check for sync file indicating pi-timolo.py has new saved image files
    if [ -e $DIR/$SYNC_FILE ]
    then
      # Run gdrive for files in folder specified by variable $SYNC_DIR
      echo "---------------------- PROCESSING ---------------------------------"
      echo "Found sync lock file $DIR/$SYNC_FILE"
      echo "Starting gdrive Push From $DIR/$SYNC_DIR"
      echo "                      To  google drive subfolder $SYNC_DIR"
      echo "-------------------------------------------------------------------"
      cd $DIR
      date
      echo "Start synchronization ....."
      START=$(date +%s)
      echo "sudo /usr/local/bin/gdrive push -no-prompt -ignore-conflict $SYNC_DIR/*jpg"
      sudo /usr/local/bin/gdrive push -no-prompt -ignore-conflict $SYNC_DIR/*jpg
      # Check if gdrive sync was successfully
      if [ $? -ne 0 ]
      then
        echo "ERROR - gdrive Processing failed."
        echo "  Possible Cause - No internet connection or some other reason."
      else
        # If successful then display processing time and remove sync file
        date
        echo "SUCCESS - $0 Processing completed successfully"
        END=$(date +%s)
        DIFF=$((END - START))
        echo "Processing took $DIFF seconds"
        echo "  Deleting lock file $DIR/$SYNC_FILE"
        rm -f $DIR/$SYNC_FILE
      fi
    else
      echo "Sync lock File Not Found $DIR/$SYNC_FILE"
      echo "  No files to process in $DIR/$SYNC_DIR"
    fi
    cd $DIR
else
  # gdrive is already running so check how long and kill if past time limit
  if [ -z "$(sudo ps axh -O etimes | grep gdrive | grep -v grep | sed 's/^ *//'| awk '{if ($2 >= 4000) print $1}')" ]
  then
    RUNTIME=$(sudo ps axh -O etimes | grep gdrive | grep -v grep | sed 's/^ *//' | awk '{if ($2 > 0) print $2}' | head -1)
    echo "Another sync.sh has run for "$RUNTIME" seconds."
    echo "  Will kill if greater than 4000 seconds."
  else
    GDRIVEPID=$(pgrep gdrive)
    echo "gdrive has run longer than 4000 seconds so kill PID $GDRIVEPID"
    echo "  Killing $GDRIVEPID"
    sudo kill $GDRIVEPID
  fi
fi

# Check if pi-timolo is running and if not then reboot
echo "Check pi-timolo.py Run Status ..."
if [ -z "$(pgrep pi-timolo)" ]
  then
    echo "pi-timolo.py is NOT running so reboot"
    sudo reboot
  else
    echo "  pi-timolo.py is Running"
fi
echo "Done ..."
exit
