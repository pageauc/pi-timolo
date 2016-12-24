#!/bin/bash
echo "$0 version 2.00 by Claude Pageau"
echo "------------------------------------------"

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
# example crontab entry below without # comment char to run every 5 minutes
# */5 * * * * /home/pi/pi-timolo/sync.sh >/dev/nul
# --------------------------------------------------------------------

PROG_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # folder location of this script
cd $PROG_DIR
echo "START   - Processing"
echo "STATUS  - Current pi-timolo working dir is $PROG_DIR"

# ---------------  Local to Remote File Sync Settings --------------
SYNC_ON=true                 # true - Do Remote Sync  false - Non
SYNC_DIR='motion'            # relative to this script folder - location of files to sync
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

# -------------------- Watch App Settings --------------------------
WATCH_APP_ON=false           # false - off  true - Check if app is running and restart or reboot
WATCH_APP='pi-timolo.py'     # App filename to monitor for Run Status
FORCE_REBOOT=false           # false - Restart pi-timolo.py if not running    true - Reboot if not running (Use with Caution)  

# ------------------------------------------------------
function restart_pi_timolo ()
{
    echo "------------------------------------------"
    echo "START   - restart_pi_timolo"
    echo "INFO    - Starting pi-timolo"     
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
        exit 1
    fi

    # Check for matching files to sync in folder
    ls -1 $PROG_DIR/$SYNC_DIR/$FILES_TO_SYNC > /dev/null 2>&1
    if [ ! "$?" = "0" ] ; then
        echo "ERROR   - No Matching $FILES_TO_SYNC Files Found in $PROG_DIR/$SYNC_DIR"
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
        if [ $CHECK_FOR_SYNC_FILE ] ; then
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
        echo "STATUS - mkdir $REMOTE_CONFIG_DIR  (local)" 
        mkdir $PROG_DIR/$REMOTE_CONFIG_DIR 
        cp $PROG_DIR/$LOCAL_CONFIG_FILE $PROG_DIR/$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE.orig
    fi

    echo "GDRIVE  - Check Remote File Exists - /$REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE"     
    /usr/local/bin/gdrive pull -no-prompt -ignore-conflict $REMOTE_CONFIG_DIR/$REMOTE_CONFIG_FILE
    
    # Check if gdrive exited successfully
    if [ $? -ne 0 ] ; then
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

if $WATCH_APP_ON ; then # check if watch app feature is on
    watch_app  
fi
echo "------------------------------------------"
echo ""
echo "Done ..."
exit
