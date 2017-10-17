#!/bin/bash
echo "=================================================================="
echo "$0 version 4.20 by Claude Pageau"

# --------------------------------------------------------------------
# Requires /usr/local/bin/gdrive executable compiled from github source for arm
# Note gdrive is included with pi-timolo on github at https://github.com/pageauc/pi-timolo
# for gdrive details see https://github.com/odeke-em/drive/releases
# To manually install gdrive binary perform the following.
# cd ~
# wget -O gdrive -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/drive_armv6
# chmod +x gdrive
# sudo cp gdrive /usr/local/bin/
# rm gdrive
# cd ~
# gdrive version
# Follow instructions for initializing gdrive for pi-timolo see pi-timolo wiki
# gdrive init
#
# Edit the sync.sh variables to enable and customize features
# For more details see my github wiki pages here
# https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-pi-timolo-gdrive-sync
# https://github.com/pageauc/pi-timolo/wiki/sync.sh---Automate-gdrive-Uploads-and-More
# https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-config.py-Remote-Configuration
# Add appropriate line to crontab using command sudo crontab -e
# example crontab entry below without # comment char to run every 5 minutes
# */5 * * * * /home/pi/pi-timolo/sync.sh >/dev/nul
# --------------------------------------------------------------------

PROG_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # folder location of this script
cd $PROG_DIR

# ---------------  Local to Remote File Sync Settings --------------
SYNC_ON=true                 # true - Do Remote Sync  false - Non
SYNC_DIR='media/motion'            # relative to this script folder - location of files to sync
FILES_TO_SYNC='*jpg'         # Set the type of files to sync * for all
CHECK_FOR_SYNC_FILE=true     # true if sync file below is required otherwise set to false always sync
SYNC_FILE_PATH=$PROG_DIR/pi-timolo.sync  # name of pi-timolo sync lock filename

# ------------------ Remote Sync Config Settings -------------------
# Remote configuration will copy a new configuration file from remote google drive
# to local pi-timolo config.py file and restart pi-timolo.
REMOTE_CONFIG_ON=false                 # true - Check for remote config file and install, false - Ignore Checking
REMOTE_CONFIG_DIR='sync_config_cam1'   # Remote Config Folder on google drive (Will be Created if Does Not Exist)
REMOTE_CONFIG_FILE='config.py'         # Name of new pi-timolo config file on google drive
LOCAL_CONFIG_FILE='config.py'          # pi-timolo configuration variables file (default)

# ------------------ Remote Sync Wipe Settings -------------------
# Remote Wipe will erase all Files in the syc folder ater syncing
# as long as a file wipe.me is located in the remote google drive
REMOTE_WIPE_ON=false                   # true - Check for wipe.me file and wipe sync folder, false - Ignore Checking
REMOTE_WIPE_DIR='sync_config_cam1'     # Remote Wipe Folder on google drive (Will be Created if Does Not Exist)
REMOTE_WIPE_FILE='wipe.me'             # Name of the wipe file on google drive
REMOTE_WIPE_SAFE=true                  # true - only synced files get deleted but this is slow, false- all jpg files get deleted

# -------------------- Watch App Settings --------------------------
WATCH_APP_ON=false           # false - off  true - Check if app is running and restart or reboot
WATCH_APP='pi-timolo.py'     # App filename to monitor for Run Status
FORCE_REBOOT=false           # false - Restart pi-timolo.py if not running    true - Reboot if not running (Use with Caution)

echo "==================== Variable Settings ==========================="
echo "SYNC_ON             =" $SYNC_ON
echo "SYNC_DIR            =" $SYNC_DIR
echo "FILES_TO_SYNC       =" $FILES_TO_SYNC
echo "CHECK_FOR_SYNC_FILE =" $CHECK_FOR_SYNC_FILE
echo "SYNC_FILE_PATH      =" $SYNC_FILE_PATH
echo ""
echo "REMOTE_CONFIG_ON    =" $REMOTE_CONFIG_ON
echo "REMOTE_CONFIG_DIR   =" $REMOTE_CONFIG_DIR
echo "REMOTE_CONFIG_FILE  =" $REMOTE_CONFIG_FILE
echo "LOCAL_CONFIG_FILE   =" $LOCAL_CONFIG_FILE
echo ""
echo "REMOTE_WIPE_ON    =" $REMOTE_WIPE_ON
echo "REMOTE_WIPE_DIR   =" $REMOTE_WIPE_DIR
echo "REMOTE_WIPE_FILE  =" $REMOTE_WIPE_FILE
echo "REMOTE_WIPE_SAFE  =" $REMOTE_WIPE_SAFE
echo ""
echo "WATCH_APP_ON        =" $WATCH_APP_ON
echo "WATCH_APP           =" $WATCH_APP
echo "FORCE_REBOOT        =" $FORCE_REBOOT
echo "=================================================================="
echo "STATUS  - Current pi-timolo working dir is $PROG_DIR"
echo "START   - Processing"

# ------------------------------------------------------
function restart_pi_timolo ()
{
    echo "------------------------------------------"
    echo "START   - restart_pi_timolo"
    echo "INFO    - Starting pi-timolo"
    $PROG_DIR/pi-timolo.sh stop
    sleep 5
    $PROG_DIR/pi-timolo.sh start
    sleep 5
    if [ -z "$(pgrep -f pi-timolo.py)" ] ; then
        # pi-timolo did not start
        echo "WARN    - Failed to Restart pi-timolo"
    else
        echo "INFO    - Successfully restarted pi-timolo"
    fi
}

# ------------------------------------------------------
function do_gdrive_sync ()
{
    # function to perform a gdrive sync between RPI local folder (exit if not found) and
    # a matching google drive folder. (Create remote folder if required)
    # Check if Local SYNC_DIR folder exists
    if [ ! -d "$PROG_DIR/$SYNC_DIR" ] ; then
        echo "ERROR   - Local Folder $PROG_DIR/$SYNC_DIR Does Not Exist"
        echo "          Please Check SYNC_DIR variable and/or Local Folder PATH"
        return 1
    fi

    # Check for matching files to sync in folder
    ls -1 $PROG_DIR/$SYNC_DIR/$FILES_TO_SYNC > /dev/null 2>&1
    if [ ! "$?" = "0" ] ; then
        echo "WARNING - No Matching $FILES_TO_SYNC Files Found in $PROG_DIR/$SYNC_DIR"
        return 1
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
            return 1
        fi
    fi
    echo "------------------------------------------"
    echo "STATUS  - Start gdrive Sync ...."
    echo "STATUS  - Local Source Folder - $PROG_DIR/$SYNC_DIR"
    echo "STATUS  - Remote Destn Folder - /$SYNC_DIR"
    echo "STATUS  - Files $FILES_TO_SYNC"
    echo "STATUS  - Running  This May Take Some Time ....."
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

# ------------------------------------------------------
function start_sync ()
{
    # function to check and perform gdrive sync push of local files to
    # remote google drive folder

    echo "------------------------------------------"
    echo "START   - start_sync - Local Files with Remote Folder"
    # check if gdrive is already running to avoid multiple instances
    if [ -z "$(pgrep -f gdrive)" ] ; then
        if [ "$CHECK_FOR_SYNC_FILE" = true ] ; then
            echo "STATUS  - Script Variable CHECK_FOR_SYNC_FILE=true"
            if [ -e $SYNC_FILE_PATH ] ; then
                # Run gdrive for files in folder specified by variable $SYNC_DIR
                echo "STATUS  - Found File $SYNC_FILE_PATH"
                do_gdrive_sync
            else
                echo "STATUS  - File Not Found $SYNC_FILE_PATH"
                echo "STATUS  - No Files to Sync at this Time."
            fi
        else
            echo "STATUS  - Script Variable CHECK_FOR_SYNC_FILE=false"
            echo "WARNING - No Sync Lock File $SYNC_FILE_PATH Required"
            do_gdrive_sync
        fi
    else
        # gdrive is already running so check how long and kill if past time limit
        GDRIVEPID=$(pgrep gdrive)
        if [ -z "$(sudo ps axh -O etimes | grep gdrive | grep -v grep | sed 's/^ *//'| awk '{if ($2 >= 4000) print $1}')" ] ; then
            RUNTIME=$(sudo ps axh -O etimes | grep gdrive | grep -v grep | sed 's/^ *//' | awk '{if ($2 > 0) print $2}' | head -1)
            echo "STATUS  - Another sync.sh has run for "$RUNTIME" seconds."
            echo "STATUS  - Will kill if greater than 4000 seconds."
            echo "STATUS  - gdrive PID is $GDRIVEPID"
        else
            echo "WARNING - gdrive has run longer than 4000 seconds so kill PID $GDRIVEPID"
            echo "          Killing $GDRIVEPID in 5 seconds"
            sleep 5
            sudo kill $GDRIVEPID
        fi
    fi
}

# ------------------------------------------------------
function do_config_sync ()
{
    # function to perform update of the local pi-timolo config.py file
    # with a specified remote google drive pi-timolo config.py file
    # and restart pi-timolo and verify successful otherwise restore orig config.py

    echo "------------------------------------------"
    echo "START   - do_config_sync - Remote Configuration Checks"
    echo "INFO    - Look for new pi-timolo $LOCAL_CONFIG_FILE file on google drive"
    echo "          at $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE (remote)"

    # check if folder exists locally and if not create one
    if [ ! -d $PROG_DIR/$REMOTE_CONFIG_DIR ] ; then
        echo "STATUS  - Creating Remote Folder /$REMOTE_CONFIG_DIR"
        echo "------------------------------------------"
        /usr/local/bin/gdrive new --folder $REMOTE_CONFIG_DIR
        /usr/local/bin/gdrive file-id $REMOTE_CONFIG_DIR
        if [ $? -ne 0 ] ; then
            echo "------------------------------------------"
            echo "ERROR   -  Could Not Create Remote $REMOTE_CONFIG_DIR"
            echo "          1 Lost Internet Connection"
            echo "          2 Some Other Reason."
        else
            echo "STATUS - mkdir $REMOTE_CONFIG_DIR  (local)"
            mkdir $PROG_DIR/$REMOTE_CONFIG_DIR
            cp $PROG_DIR/$LOCAL_CONFIG_FILE $PROG_DIR/$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE.orig
            echo "GDRIVE  - Sync push Local /$REMOTE_CONFIG_DIR Files to Local to $REMOTE_CONFIG_DIR"
            echo "GDRIVE  - Sync push Local /
            Files to Local to $REMOTE_CONFIG_DIR"
            /usr/local/bin/gdrive push -no-prompt -ignore-conflict $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE.orig
       fi
    fi

    echo "GDRIVE  - Check Remote File Exists - /$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE"
    /usr/local/bin/gdrive pull -no-prompt -ignore-conflict $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE
    if [ $? -ne 0 ] ; then   # Check if gdrive exited successfully
        echo "------------------------------------------"
        echo "WARN    - Remote Configuration Check Failed"
        echo "          See gdrive message above for Details."
        echo "          Possible Cause"
        echo "          1 Remote File Not Found /$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE"
        echo "            So No New Configuration to Install"
        echo "          2 Lost Internet Connection"
        echo "          3 Some Other Reason."
    else
        # Download successful start update of pi-timolo config.py
        if [ -e $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE ] ; then
            echo "STATUS  - Successfully Downloaded $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE  (remote)"
            echo "          to $PROG_DIR/$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE  (local)"
            echo "BACKUP  - $PROG_DIR/$LOCAL_CONFIG_FILE $PROG_DIR/$LOCAL_CONFIG_FILE.prev  (local)"
            cp $PROG_DIR/$LOCAL_CONFIG_FILE $PROG_DIR/$LOCAL_CONFIG_FILE.prev
            cp $PROG_DIR/$LOCAL_CONFIG_FILE $PROG_DIR/$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE.prev

            echo "COPY    - $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE $PROG_DIR/$LOCAL_CONFIG_FILE (local)"
            cp $PROG_DIR/$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE $PROG_DIR/$LOCAL_CONFIG_FILE
            chown pi:pi $PROG_DIR/$LOCAL_CONFIG_FILE
            echo "RENAME  - $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE $REMOTE_CONFIG_FILE.done  (remote)"
            /usr/local/bin/gdrive rename -force $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE $REMOTE_CONFIG_FILE.done
            echo "DELETE  - $PROG_DIR/$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE  (local)"
            rm $PROG_DIR/$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE
            echo "SUCCESS - $PROG_DIR/$LOCAL_CONFIG_FILE updated successfully."
            echo "------------------------------------------"
            echo "GDRIVE  - Sync push Local /$LOCAL_CONFIG_DIR Files to Local to $REMOTE_CONFIG_DIR"
            /usr/local/bin/gdrive push -no-prompt -ignore-conflict $REMOTE_CONFIG_DIR
            echo "TRASH   - Empty gdrive trash  (local)"
            /usr/local/bin/gdrive emptytrash -no-prompt
            echo "------------------------------------------"
            echo "WARN    - Sync Complete Restarting pi-timolo"
            restart_pi_timolo
            if [ -z "$(pgrep -f pi-timolo.py)" ] ; then
                # pi-timolo did not start so restore prev config.py
                cp $PROG_DIR/$LOCAL_CONFIG_FILE.prev $PROG_DIR/$LOCAL_CONFIG_FILE
                echo "WARN    - Stopping pi-timolo.py"
                $PROG_DIR/pi-timolo.sh stop
                restart_pi_timolo
            fi
        else
            echo "GDRIVE  - $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE Not Found (local)"
            echo "STATUS  - $PROG_DIR/$LOCAL_CONFIG_FILE Configuration Not Updated."
        fi
    fi
}
# ------------------------------------------------------
function do_wipe_sync ()
{
    # function to wipe local copy of synced files
    # remote files will not be effected
    # regular wipes speed up the sync process

    echo "------------------------------------------"
    echo "START   - do_wipe_sync - Remote Wipe Checks"
    echo "INFO    - Look for new wipe file on google drive"
    echo "          at $REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE (remote)"

    # check if folder exists locally and if not create one
    if [ ! -d $PROG_DIR/$REMOTE_WIPE_DIR ] ; then
        echo "STATUS  - Creating Remote Folder /$REMOTE_WIPE_DIR"
        echo "------------------------------------------"
        /usr/local/bin/gdrive new --folder $REMOTE_WIPE_DIR
        /usr/local/bin/gdrive file-id $REMOTE_WIPE_DIR
        if [ $? -ne 0 ] ; then
            echo "------------------------------------------"
            echo "ERROR   -  Could Not Create Remote $REMOTE_WIPE_DIR"
            echo "          1 Lost Internet Connection"
            echo "          2 Some Other Reason."
        else
            echo "STATUS - mkdir $REMOTE_WIPE_DIR  (local)"
            mkdir $PROG_DIR/$REMOTE_WIPE_DIR
       fi
    fi

    echo "GDRIVE  - Check Remote Wipe File Exists - /$REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE"
    /usr/local/bin/gdrive pull -no-prompt -ignore-conflict $REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE
    if [ $? -ne 0 ] ; then   # Check if gdrive exited successfully
        echo "------------------------------------------"
        echo "WARN    - Remote Wipe Check Failed"
        echo "          See gdrive message above for Details."
        echo "          Possible Cause"
        echo "          1 Remote File Not Found /$REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE"
        echo "          2 Lost Internet Connection"
        echo "          3 Some Other Reason."
    else
        # Download successful start update of pi-timolo config.py
        if [ -e $REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE ] ; then
            echo "STATUS  - Successfully Downloaded $REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE  (remote)"
            echo "          to $PROG_DIR/$REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE  (local)"
            /usr/local/bin/gdrive rename -force $REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE $REMOTE_WIPE_FILE.done
            echo "DELETE  - $SYNC_DIR  (local)"
            if $REMOTE_WIPE_SAFE ; then
                /usr/local/bin/gdrive list -match-mime jpg $SYNC_DIR | cut -c2- | xargs -n 10 echo rm -f | sh
            else
                rm $SYNC_DIR/*jpg
            fi
            echo "SUCCESS - $SYNC_DIR  is now empty"
            echo "------------------------------------------"
            echo "GDRIVE  - Sync push Local /$REMOTE_WIPE_DIR Files to Local to $REMOTE_WIPE_DIR"
            /usr/local/bin/gdrive push -no-prompt -ignore-conflict $REMOTE_WIPE_DIR
            echo "TRASH   - Empty gdrive trash  (local)"
            /usr/local/bin/gdrive emptytrash -no-prompt
        else
            echo "GDRIVE  - $REMOTE_WIPE_DIR/$REMOTE_WIPE_FILE Not Found (local)"
        fi
    fi
}
# ------------------------------------------------------
function watch_app ()
{
    echo "------------------------------------------"
    echo "START   - watch_app - Check $WATCH_APP Run Status ..."
    if [ -z "$(pgrep -f $WATCH_APP)" ] ; then
        if $FORCE_REBOOT ; then
            echo "STATUS  - $WATCH_APP is NOT Running so reboot"
            echo "WARNING - Reboot in 15 seconds Waiting ...."
            echo "          ctrl-c to Abort Reboot."
            sleep 10
            echo "WARNING - Rebooting in 5 seconds"
            sleep 5
            sudo reboot
        else
            restart_pi_timolo
        fi
    else
        APP_PID=$(pgrep -f $WATCH_APP)
        echo "STATUS  - $WATCH_APP is Running PID is $APP_PID"
    fi
}

# ------------------------------------------------------
# Main script processing

if $SYNC_ON ; then # Check and Sync Files From Local To Remote Folder.
    start_sync
fi

if $REMOTE_CONFIG_ON ; then  # Check if remote configuration feature is on
    do_config_sync
fi

if $REMOTE_WIPE_ON ; then  # Check if remote wipe feature is on
    do_wipe_sync
fi

if $WATCH_APP_ON ; then # check if watch app feature is on
    watch_app
fi
echo "------------------------------------------"
echo ""
echo "Done ..."
exit

