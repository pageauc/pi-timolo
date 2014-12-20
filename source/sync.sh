#!/bin/bash
# sync.sh written by Claude Pageau.  requires /home/pi/grive executable compiled from github source 
# for details see http://www.pihomeserver.fr/en/2013/08/15/raspberry-pi-home-server-synchroniser-le-raspberry-pi-avec-votre-google-drive/
# Runs grive only if it is not already running
# Looks for sync.lock file created by pimotion.py to start the sync
# Kills grive process if it has been running too long. > 300 seconds
# Suggest you run this script from crontab every minute or so.  Add approriate line to crontab using command sudo crontab -e
# example crontab entry below without # comment char
# */1 * * * * /home/pi/sync.sh >/dev/nul

echo ---------------------------- $0 ---------------------------------
# Get current folder that this script is located in
SYNCFILE=pimotion.sync
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Current Directory=$DIR"
# check if grive is already running to avoid multiple instances
if [ -z "$(pgrep grive)" ]
  then
    # Check for any grive .trash files and remove to recover space
    if [ -e $DIR/motion/.trash/* ]
    then
      echo "grive .. Remove trash from '$DIR'/motion/.trash"
      rm -R $DIR/motion/.trash/*
    fi
    # Check for sync file indicating pimotion.py saved new files
    if [ -e $DIR/$SYNCFILE ]
    then
      # Run grive in the against the motion folder
      echo "grive .. Found $SYNCFILE files to synchronize"
      echo "Change Directory to $DIR/motion"
      cd $DIR/motion
      echo "grive .. Running $DIR/grive -p $DIR/motion"
      $DIR/grive -p $DIR/motion
      # Check if grive exited successully
      if [ $? -ne 0 ]
      then
        echo "grive .. processing failed"
      else
        # If successful then remove sync file
        echo "grive .. processing complete"
        echo "grive .. remove $DIR/$SYNCFILE file"
        rm -f $DIR/$SYNCFILE
      fi
    else
      echo "grive .. No files to process in $DIR/motion"
    fi
    cd $DIR
else
  # grive is already running so check how long and kill if past time limit
  if [ -z "$(sudo ps axh -O etimes | grep grive | grep -v grep | sed 's/^ *//'| awk '{if ($2 >= 300) print $1}')" ]
  then
    GRIVETIME=$(sudo ps axh -O etimes | grep grive | grep -v grep | sed 's/^ *//' | awk '{if ($2 > 0) print $2}')
    echo "grive .. Has run for $GRIVETIME seconds. Will kill when greater than 300 seconds."
  else
    GRIVEPID=$(pgrep grive)
    echo "grive .. Has run longer than 5 minutes so kill pid $GRIVEPID"
    KILLPID=$(ps axh -O etimes | grep grive | grep -v grep | awk '{if ($2 >= 300) print $1}')
    echo "grive .. killing $KILLPID"
    sudo kill $KILLPID
  fi
fi
exit
