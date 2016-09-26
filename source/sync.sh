#!/bin/bash
echo "$0 version 1.5 by Claude Pageau"
# --------------------------------------------------------------------
# Requires /usr/local/bin/gdrive executable compiled from github source for arm
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
# --------------------------------------------------------------------
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # folder location of this script

# -------------------  User Variables ------------------
SYNC_DIR=motion          # folder location of files to sync
FILES_TO_SYNC='*jpg'     # Set the type of files to sync * for all
CHECK_FOR_SYNC_FILE=true # true if sync file required otherwise set to false
SYNC_FILE_PATH=$DIR/pi-timolo.sync  # name of pi-timolo sync lock filename
FORCE_REBOOT=false       # true to reboot if pi-timolo not running otherwise set to false
# ------------------------------------------------------

function do_gdrive_sync()
{
  cd $DIR
  date
  echo "Start synchronization ....."
  START=$(date +%s)
  echo "sudo /usr/local/bin/gdrive push -no-prompt -ignore-conflict $SYNC_DIR/*jpg"
  sudo /usr/local/bin/gdrive push -no-prompt -ignore-conflict $SYNC_DIR/$FILES_TO_SYNC
  # Check if gdrive sync was successfully
  if [ $? -ne 0 ] ;  then
    echo "ERROR - gdrive Processing failed."
    echo "  Possible Cause - No internet connection or some other reason."
  else
    # If successful then display processing time and remove sync file
    date
    echo "SUCCESS - $0 Processing completed successfully"
    END=$(date +%s)
    DIFF=$((END - START))
    echo "Processing took $DIFF seconds"
    echo "  Deleting lock file $SYNC_FILE"
    rm -f $SYNC_FILE
  fi
}

# check if gdrive is already running to avoid multiple instances
if [ -z "$(pgrep gdrive)" ] ; then
  if [ $CHECK_FOR_SYNC_FILE ; then
    if [ -e $SYNC_FILE_PATH ] ; then
      # Run gdrive for files in folder specified by variable $SYNC_DIR
      echo "---------------------- PROCESSING ---------------------------------"
      echo "Found sync lock file $DIR/$SYNC_FILE"
      echo "Starting gdrive Push From $DIR/$SYNC_DIR"
      echo "                      To  google drive subfolder $SYNC_DIR"
      echo "-------------------------------------------------------------------"
      do_gdrive_sync
    else
      echo "Sync lock File Not Found at $SYNC_FILE"
      echo "  No files to process in $SYNC_DIR"
      echo ""
    fi
  else
    do_gdrive_sync
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

if $FORCE_REBOOT ; then  # check if reboot required
  echo "Check pi-timolo.py Run Status ..."
  if [ -z "$(pgrep pi-timolo)" ] ; then
    echo "pi-timolo.py is NOT running so reboot"
    sudo reboot
  else
    echo "  pi-timolo.py is Running"
  fi
  echo "Done ..."
fi
exit
