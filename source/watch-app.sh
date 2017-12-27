#!/bin/bash
ver="9.79"
progName=$(basename -- "$0")
echo "$progName $ver  written by Claude Pageau"

# ----------------- User Customize Variables Below  --------------

watch_config_on=false    # true=Remotely Manage Files from Remote Storage  false=off
watch_app_on=false       # true=Monitor watch_app_fname and attempt restart false=off
watch_reboot_on=false    # true= Reboot RPI If watch_app_fname Down false=0ff

watch_app_fname="pi-timolo.py"  # Filename of Program to Monitor for Run Status

rclone_name="gdmedia"           # Name you gave remote storage service

sync_dir="mycam-config-sync"      # Name of folder to manage when watch_config_on=true

# List of files to monitor for updates
sync_files=("config.py" "pi-timolo.py" "convid.conf" "makevideo.conf" "watch-app-err.log")

# -------------- End User Variable Edits -------------------------

# Display Users Settings
fList=""
for fname in "${sync_files[@]}" ; do
    fList=$fList' '$fname
done
echo "--------------- SETTINGS -----------------

watch_config_on  : $watch_config_on       # manage config true=on false=off
watch_app_on     : $watch_app_on       # restart true=on false=off
watch_reboot_on  : $watch_reboot_on       # reboot true=on false=off
watch_app_fname  : $watch_app_fname

rclone_name      : $rclone_name  # Name you gave remote storage service

sync_dir         : $sync_dir   # Will be created if does not exist
sync_files       :$fList

------------------------------------------"

progDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # folder location of this script
cd $progDir

# ------------------------------------------------------
function do_watch_restart ()
{
    if [ ! -z "$( pgrep -f $watch_app_fname )" ]; then
        progPID=$( pgrep -f $watch_app_fname )
        echo "do_watch_restart - Stop $watch_app_fname PID $progPID"
        sudo kill $progPID
        sleep 1
    fi
    echo "do_watch_restart - Start $watch_app_fname"
   ./$watch_app_fname  >/dev/null 2>&1 &
    sleep 1
    if [ -z "$(pgrep -f $watch_app_fname)" ] ; then
        # pi-timolo did not start
        echo "do_watch_restart - Restart Failed $watch_app_fname"
    else
        progPID=$( pgrep -f $watch_app_fname )
        echo "do_watch_restart - Restart OK $watch_app_fname PID $progPID"
    fi
}

# ------------------------------------------------------
function do_remote_config ()
{
    if [ ! -d $sync_dir ] ; then  # If local sync dir does not exist then create one
        echo "do_remote_config - Create New Dir $sync_dir"
        mkdir $sync_dir
        for fname in "${sync_files[@]}" ; do
            if [ -f $fname ] ; then
                echo "do_remote_config - Copy $fname to $sync_dir"
                cp $fname $sync_dir/$fname.orig
                cp $fname $sync_dir/$fname.done
            else
                echo "do_remote_config - $fname File Not Found"
            fi
        done
        echo "do_remote_config - rclone sync -v $sync_dir $rclone_name:$sync_dir"
        /usr/bin/rclone sync -v $sync_dir $rclone_name:$sync_dir  # sync to remote storage drive
        if [ ! $? -eq 0 ]; then
            /usr/bin/rclone sync -v --log-file watch-app-err.log $sync_dir $rclone_name:$sync_dir
            echo "EPROR - do_remote_config - Problem with rclone.  Check rclone_name $rclone_name"
        fi
    else
        echo "do_remote_config - rclone sync -v $rclone_name:$sync_dir $sync_dir"
        /usr/bin/rclone sync -v $rclone_name:$sync_dir $sync_dir  # sync remote with local sync dir
        if [ ! $? -eq 0 ]; then
            echo "do_remote_config - rclone sync -v $sync_dir $rclone_name:$sync_dir"
            /usr/bin/rclone sync $sync_dir $rclone_name:$sync_dir  # sync to remote storage drive
            /usr/bin/rclone sync -v $rclone_name:$sync_dir $sync_dir  # sync remote with local sync dir
            if [ ! $? -eq 0 ]; then
                /usr/bin/rclone sync -v --log-file watch-app-err.log $rclone_name:$sync_dir $sync_dir
                echo "do_remote_config - Problem with rclone. Check rclone_name $rclone_name"
            fi
        fi
        found_update=false
        for fname in "${sync_files[@]}" ; do     # check if new config files are present
            if [ -f $sync_dir/$fname ] ; then
                found_update=true
                echo "do_remote_config - Found Update for File $fname"
                cp $fname $sync_dir/$fname.prev  # save copy with .prev extension
                echo "do_remote_config - Copy $sync_dir/$fname to $fname"
                cp $sync_dir/$fname $fname       # update working file
            fi
        done
        if [ -f "watch-app-err.log" ]; then
            cp watch-app-err.log $sync_dir
        fi
        if $found_update; then
            do_watch_restart
            if [ -z "$(pgrep -f $watch_app_fname)" ] ; then  # changes Failed so restore prev files
                for fname in "${sync_files[@]}" ; do
                    if [ -f $sync_dir/$fname ] ; then
                        echo "do_remote_config - Undo Update Copy $fname to $sync_dir/$fname.err"
                        cp $fname $sync_dir/$fname.bad
                        cp $sync_dir/$fname.prev $fname
                        rm $sync_dir/$fname
                    fi
                done
                do_watch_restart
                echo "rclone sync -v $sync_dir $rclone_name:$sync_dir"
                /usr/bin/rclone sync -v $sync_dir $rclone_name:$sync_dir
            else
                # pi-timolo Started OK so restore prev config.py
                for fname in "${sync_files[@]}" ; do
                    if [ -f $sync_dir/$fname ] ; then
                        echo "do_remote_config - Done Update Copy $fname to $sync_dir/$fname.done"
                        cp $fname $sync_dir/$fname.done
                        rm $sync_dir/$fname
                    fi
                done
                echo "do_remote_sync - Confirm Update"
                echo "rclone sync -v $sync_dir $rclone_name:$sync_dir"
                /usr/bin/rclone sync -v $sync_dir $rclone_name:$sync_dir
                do_watch_restart
            fi
        else
            echo "do_remote_config - No File Changes Found in $sync_dir"
        fi
    fi
}

# ------------------------------------------------------
function do_watch_app()
{
    if [ -z "$( pgrep -f $watch_app_fname )" ]; then
        do_watch_restart
    else
        progPID=$( pgrep -f $watch_app_fname )
        echo "$watch_app_fname is Running PID $progPID"
    fi
}

# ------------------------------------------------------
function do_watch_reboot ()
{
    if [ -z "$(pgrep -f $watch_app_fname)" ] ; then
        if $watch_reboot_on ; then
            echo "do_watch_reboot - $watch_app_fname is NOT Running so reboot"
            echo "do_watch_reboot - Reboot in 15 seconds Waiting ...."
            echo "                     ctrl-c to Abort Reboot."
            sleep 10
            echo "do_watch_reboot - Rebooting in 5 seconds"
            sleep 5
            sudo reboot
        fi
    else
        APP_PID=$(pgrep -f $watch_app_fname)
        echo "do_watch_reboot - $watch_app_fname is Running PID $APP_PID"
    fi
}

# ------------------------------------------------------
# Main script processing
if pidof -o %PPID -x "$progName"; then
    echo "WARN  - $progName Already Running. Only One Allowed."
else
    if $watch_app_on ; then # Restart app if not running
        do_watch_app
    else
        echo "WARN  - Watch App is Off per watch_app_on=$watch_app_on"
    fi

    if $watch_config_on ; then  # Check if remote configuration feature is on
        if [ -f /usr/bin/rclone ]; then
            echo "List Remote Names"
            echo "-----------------"
            /usr/bin/rclone listremotes
            echo "-----------------"
            do_remote_config
        else
            echo "ERROR - /usr/bin/rclone File Not Found. Please Investigate."
        fi
    else
        echo "WARN  - Remote Configuration is Off per watch_config_on=$watch_config_on"
    fi

    if $watch_reboot_on ; then # check if watch app feature is on
        do_watch_reboot
    else
       echo "WARN  - Watch Reboot is Off per watch_reboot_on=$watch_reboot_on"
    fi
    
    if [ -f "watch-app-new.sh" ] ; then
        echo "------------------------------------------
WARN  - Found Newer Version of watch-app.sh per watch-app-new.sh
        To Implement New Version
        1  nano watch-app-new.sh
        2  Edit settings to transfer any customization from existing watch-app.sh
        3  cp watch-app.sh watch-app-old.sh
           or
           rm watch-app.sh           
        4  mv watch-app-new.sh watch-app.sh
        5  Test changes"
    fi
fi
echo "------------------------------------------
$progName Done ..."
exit

