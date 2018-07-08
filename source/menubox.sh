#!/bin/bash

ver="10.10"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

pyconfigfile="./config.py"
filename_conf="./pi-timolo.conf"
filename_temp="./pi-timolo.conf.temp"
filename_utils_conf="/home/pi/pi-timolo/utils.conf"
filename_utils_temp="$filename_utils_conf_temp"

#------------------------------------------------------------------------------
function do_anykey ()
{
   echo ""
   echo "#######################################"
   echo "#           Review Output             #"
   echo "#######################################"
 read -p "Press Enter to Return to Previous Menu"
}

#------------------------------------------------------------------------------
function init_status ()
{
  if [ -z "$( pgrep -f pi-timolo.py )" ]; then
    PTMLO_1="START"
    PTMLO_2="pi-timolo.py in background"
  else
     pi_timolo_pid=$( pgrep -f pi-timolo.py )
     PTMLO_1="STOP"
     PTMLO_2="pi-timolo.py - PID is $pi_timolo_pid"
  fi

  if [ -z "$( pgrep -f $DIR/webserver.py )" ]; then
     WEB_1="START"
     WEB_2="webserver.py in background"
  else
     webserver_pid=$( pgrep -f $DIR/webserver.py )
     myip=$(ifconfig | grep 'inet ' | grep -v 127.0.0 | cut -d " " -f 12 | cut -d ":" -f 2 )
     myport=$( grep "web_server_port" config.py | cut -d "=" -f 2 | cut -d "#" -f 1 | awk '{$1=$1};1' )
     WEB_1="STOP"
     WEB_2="webserver.py - PID is $webserver_pid http://$myip:$myport"
  fi
}

#------------------------------------------------------------------------------
function do_pi_timolo ()
{
  if [ -z "$( pgrep -f pi-timolo.py )" ]; then
     ./pi-timolo.py >/dev/null 2>&1 &
     if [ -z "$( pgrep -f pi-timolo.py )" ]; then
         whiptail --msgbox "Failed to Start pi-timolo.py   Please Investigate Problem " 20 70
     fi
  else
     pi_timolo_pid=$( pgrep -f pi-timolo.py )
     sudo kill $pi_timolo_pid
      if [ ! -z "$( pgrep -f pi-timolo.py )" ]; then
          whiptail --msgbox "Failed to Stop pi-timolo.py   Please Investigate Problem" 20 70
      fi
  fi
  do_main_menu
}

#------------------------------------------------------------------------------
function do_webserver ()
{
  if [ -z "$( pgrep -f $DIR/webserver.py )" ]; then
     $DIR/webserver.py >/dev/null 2>&1 &
     if [ -z "$( pgrep -f $DIR/webserver.py )" ]; then
        whiptail --msgbox "Failed to Start webserver.py   Please Investigate Problem." 20 70
     else
       myip=$(ifconfig | grep 'inet ' | grep -v 127.0.0 | cut -d " " -f 12 | cut -d ":" -f 2 )
       myport=$( grep "web_server_port" config.py | cut -d "=" -f 2 | cut -d "#" -f 1 | awk '{$1=$1};1' )
       whiptail --msgbox --title "Webserver Access" "Access pi-timolo web server from another network computer web browser using url http://$myip:$myport" 15 50
     fi
  else
     webserver_pid=$( pgrep -f $DIR/webserver.py )
     sudo kill $webserver_pid
     if [ ! -z "$( pgrep -f $DIR/webserver.py )" ]; then
        whiptail --msgbox "Failed to Stop webserver.py   Please Investigate Problem." 20 70
     fi
  fi
  do_main_menu
}

#------------------------------------------------------------------------------
function do_makevideo ()
{
  if [ -e makevideo.sh ] ; then
     ./makevideo.sh
     do_anykey
     do_makevideo_menu
  else
     whiptail --msgbox "ERROR - makevideo.sh File Not Found. Please Investigate." 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_makevideo_config ()
{
  if [ -f $DIR/video.conf ] ; then
     /bin/nano $DIR/video.conf
  else
     whiptail --msgbox "ERROR - $DIR/video.conf File Not Found. Please Investigate." 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_makevideo_menu ()
{
  SELECTION=$(whiptail --title "makevideo.sh Menu" --menu "Arrow/Enter to Run or Tab Key" 20 67 7 --cancel-button Back --ok-button Select \
  "a RUN" "makevideo.sh - motion or timelapse jpg's to mp4 video" \
  "b EDIT" "nano video.conf  makevideo.sh & config.sh Settings" \
  "c VIEW" "video.conf file  makevideo.sh & config.sh Settings" \
  "q BACK" "To Main Menu"  3>&1 1>&2 2>&3)

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SELECTION" in
      a\ *) do_makevideo
            do_makevideo_menu ;;
      b\ *) do_makevideo_config
            do_makevideo_menu ;;
      c\ *) clear
            more $DIR/video.conf
            do_anykey
            do_makevideo_menu ;;
      q\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 10 65 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 10 65 1
  fi
}

#------------------------------------------------------------------------------
function do_join_video ()
{
  if [ -e convid.sh ] ; then
     ./convid.sh join
     do_anykey
     do_convid_menu
  else
     whiptail --msgbox "ERROR - convid.sh file Not Found. Please Investigate." 20 65 1
  fi
}

#------------------------------------------------------------------------------
function do_convert_video ()
{
  if [ -e convid.sh ] ; then
     ./convid.sh convert
     do_anykey
     do_convid_menu
  else
     whiptail --msgbox "ERROR - convid.sh file Not Found. Please Investigate." 20 65 1
  fi
}

#------------------------------------------------------------------------------
function do_convid_config ()
{
    if [ -f $DIR/video.conf ] ; then
        /bin/nano $DIR/video.conf
    else
        whiptail --msgbox "ERROR - $DIR/video.conf File Not Found. Please Investigate." 20 65 1
    fi
}

#------------------------------------------------------------------------------
function do_convid_menu ()
{

  VID_SEL=$( whiptail --title "convid.sh Menu" --menu "Arrow/Enter to Run or Tab Key" 0 0 0 --cancel-button Back --ok-button Select \
  "a JOIN" "JOIN multiple motion MP4 videos into larger videos" \
  "b CONVERT" "motion h264 files to MP4 videos" \
  "c EDIT" "nano video.conf  makevideo.sh & config.sh Settings" \
  "d VIEW" "video.conf  makevideo.sh & config.sh Settings" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$VID_SEL" in
      a\ *) do_join_video ;;
      b\ *) do_convert_video ;;
      c\ *) do_convid_config
            do_convid_menu ;;
      d\ *) clear
            cat $DIR/video.conf
            do_anykey
            do_convid_menu ;;
      q\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function Filebrowser()
{
# first parameter is Menu Title
# second parameter is optional dir path to starting folder
# otherwise current folder is selected

    if [ -z $2 ] ; then
        dir_list=$(ls -lhp  | awk -F ' ' ' { print $9 " " $5 } ')
    else
        cd "$2"
        dir_list=$(ls -lhp  | awk -F ' ' ' { print $9 " " $5 } ')
    fi

    curdir=$(pwd)
    if [ "$curdir" == "/" ] ; then  # Check if you are at root folder
        selection=$(whiptail --title "$1" \
                              --menu "PgUp/PgDn/Arrow Enter Selects File/Folder\nor Tab Key\n$curdir" 0 0 0 \
                              --cancel-button Cancel \
                              --ok-button Select $dir_list 3>&1 1>&2 2>&3)
    else   # Not Root Dir so show ../ BACK Selection in Menu
        selection=$(whiptail --title "$1" \
                              --menu "PgUp/PgDn/Arrow Enter Selects File/Folder\nor Tab Key\n$curdir" 0 0 0 \
                              --cancel-button Cancel \
                              --ok-button Select ../ BACK $dir_list 3>&1 1>&2 2>&3)
    fi

    RET=$?
    if [ $RET -eq 1 ]; then  # Check if User Selected Cancel
       return 1
    elif [ $RET -eq 0 ]; then
       if [[ -d "$selection" ]]; then  # Check if Directory Selected
          Filebrowser "$1" "$selection"
       elif [[ -f "$selection" ]]; then  # Check if File Selected
          if [[ $selection == *$filext ]]; then   # Check if selected File has .jpg extension
            if (whiptail --title "Confirm Selection" --yesno "DirPath : $curdir\nFileName: $selection" 0 0 \
                         --yes-button "Confirm" \
                         --no-button "Retry"); then
                filename="$selection"
                filepath="$curdir"    # Return full filepath  and filename as selection variables
            else
                Filebrowser "$1" "$curdir"
            fi
          else   # Not jpg so Inform User and restart
             whiptail --title "ERROR: File Must have .jpg Extension" \
                      --msgbox "$selection\nYou Must Select a jpg Image File" 0 0
             Filebrowser "$1" "$curdir"
          fi
       else
          # Could not detect a file or folder so Try Again
          whiptail --title "ERROR: Selection Error" \
                   --msgbox "Error Changing to Path $selection" 0 0
          Filebrowser "$1" "$curdir"
       fi
    fi
}

#------------------------------------------------------------------------------
function do_nano_edit ()
{
    menutitle="Select File to Edit"
    startdir="/home/pi/pi-timolo"
    filext='sh'

    Filebrowser "$menutitle" "$startdir"

    exitstatus=$?
    if [ $exitstatus -eq 0 ]; then
        if [ "$selection" == "" ]; then
            echo "User Pressed Esc with No File Selection"
        else
            nano $filepath/$filename
        fi
    else
        echo "User Pressed Cancel. with No File Selected"
    fi
}

#------------------------------------------------------------------------------
function do_plugins_edit ()
{
    menutitle="Select File to Edit"
    startdir="/home/pi/pi-timolo/plugins"
    filext='py'

    Filebrowser "$menutitle" "$startdir"

    exitstatus=$?
    if [ $exitstatus -eq 0 ]; then
        if [ "$selection" == "" ]; then
            echo "User Pressed Esc with No File Selection"
        else
            nano $filepath/$filename
        fi
    else
        echo "User Pressed Cancel. with No File Selected"
    fi
    cd $DIR
}

#------------------------------------------------------------------------------
function do_sync_run ()
{
    menutitle="Select rclone sync Script to Run"
    startdir="/home/pi/pi-timolo"
    filext='sh'

    Filebrowser "$menutitle" "$startdir"

    exitstatus=$?
    if [ $exitstatus -eq 0 ]; then
        if [ "$selection" == "" ]; then
            echo "User Pressed Esc with No File Selection"
        else
            if [ ! -x "$filepath/$filename" ]; then
                chmod +x $filepath/$filename
            fi
            $filepath/$filename
            do_anykey
            clear
        fi
    else
        echo "User Pressed Cancel. with No File Selected"
    fi
    cd $DIR
}

#------------------------------------------------------------------------------
function do_sync_menu ()
{
  SET_SEL=$( whiptail --title "Rclone Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a EDIT" "Select rclone- sh File to Edit with nano" \
  "b RUN" "Run Selected Rclone sh Script" \
  "c CONFIG" "Run rclone config See GitHub Wiki for Details" \
  "d LIST" "Names of Configured Remote Storage Services" \
  "e HELP" "Rclone Man Pages" \
  "f ABOUT" "Rclone Remote Storage Sync" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_nano_edit
            do_sync_menu ;;
      b\ *) do_sync_run
            do_sync_menu ;;
      c\ *) clear
            rclone config
            do_anykey
            clear
            do_sync_menu ;;
      d\ *) clear
            echo "Avail Remote Names"
            /usr/bin/rclone -v listremotes
            do_anykey
            clear
            do_sync_menu ;;
      e\ *) man rclone
            do_sync_menu ;;
      f\ *) do_sync_about
            do_sync_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

function do_sync_about
{
  whiptail --title "About Sync" --msgbox "\
Rclone is the default pi-timolo remote storage sync utility.
You Must Configure a Remote Storage Service before using.
gdrive is no longer installed but will remain if already installed.

For More Details See Wiki per link below
https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-rclone

Select EDIT menu to change rclone-sync.sh script variables.
ctrl-x y to save changes and exit nano otherwise respond n.

Select CONFIG menu to run rclone config menu.
You will need details about Remote Storage Service.

Select RUN menu to Test rclone-sync.sh changes.
or manually Run the command below from a console session.

    ./rclone-sync.sh

If you want to Run Rclone install separately for another project.
See my GitHub Project https://github.com/pageauc/rclone4pi

                           -----
\
" 0 0 0

}

#--------------------------------------------------------------------
function do_edit_save ()
{
  if (whiptail --title "Save $var=$newvalue" --yesno "$comment\n $var=$newvalue   was $value" 8 65 --yes-button "Save" --no-button "Cancel" ) then
    value=$newvalue

    rm $filename_conf  # Initialize new conf file
    while read configfile ;  do
      if echo "${configfile}" | grep --quiet "${var}" ; then
         echo "$var=$value         #$comment" >> $filename_conf
      else
         echo "$configfile" >> $filename_conf
      fi
    done < $pyconfigfile
    cp $filename_conf $pyconfigfile
  fi
  rm $filename_temp
  rm $filename_conf
  do_settings_menu
}

#------------------------------------------------------------------------------
function do_nano_main ()
{
  cp $pyconfigfile $filename_conf
  nano $filename_conf
  if (whiptail --title "Save Nano Edits" --yesno "Save nano changes to $filename_conf\n or cancel all changes" 8 65 --yes-button "Save" --no-button "Cancel" ) then
    cp $filename_conf $pyconfigfile
  fi
}

#------------------------------------------------------------------------------
function do_settings_menu ()
{
  SET_SEL=$( whiptail --title "Settings Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a EDIT" "nano config.py for pi-timolo & webserver" \
  "b VIEW" "config.py for pi-timolo & webserver" \
  "c EDIT" "nano video.conf  makevideo.sh & config.sh Settings" \
  "d VIEW" "video.conf  makevideo.sh & config.sh Settings" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    clear
    rm -f $filename_temp
    rm -f $filename_conf
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_nano_main
            do_settings_menu ;;
      b\ *) more -d config.py
            do_anykey
            do_settings_menu ;;
      c\ *) do_makevideo_config
            do_settings_menu ;;
      d\ *) clear
            cat $DIR/video.conf
            do_anykey
            do_settings_menu ;;
      q\ *) clear
            rm -f $filename_temp
            rm -f $filename_conf
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_watch_menu ()
{
  SET_SEL=$( whiptail --title "watch-app.sh Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a EDIT" "Edit watch-app.sh using nano" \
  "b RUN" "Test Run watch-app.sh" \
  "c CRON" "Edit crontab" \
  "d ABOUT" "About watch-app.sh Remote Configure" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    clear
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) nano watch-app.sh
            do_watch_menu ;;
      b\ *) ./watch-app.sh
            do_anykey
            do_watch_menu ;;
      c\ *) sudo crontab -e
            do_watch_menu ;;
      d\ *) do_watch_about
            do_watch_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_watch_about ()
{
  whiptail --title "About watch-app.sh" --msgbox "\
watch-app.sh allows monitoring of pi-timolo-py and restarting
if application is down or optionally rebooting. It will also
allow changing specified configuration and program files
from a remote storage drive and getting feedback on the
results on the remote machine.

for more details see GitHub Wiki

\
" 0 0 0

}

#------------------------------------------------------------------------------
function do_plugins_menu ()
{
  SET_SEL=$( whiptail --title "Edit Plugins Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a config" "nano config.py - plugin vars override" \
  "b SELECT" "plugin File to nano Edit" \
  "c secfast" "nano plugins/secfast.py" \
  "d secstill" "nano plugins/secstill.py" \
  "e secvid" "nano plugins/secvid.py" \
  "f secQTL" "nano plugins/secQTL.py" \
  "g TLlong" "nano plugins/TLlong.py" \
  "h TLshort" "nano plugins/TLshort.py" \
  "i shopcam" "nano plugins/shopcam.py" \
  "j dashcam" "nano plugins/dashcam.py" \
  "k slowmo" "nano plugins/slowmo.py" \
  "l strmvid" "nano plugins/strmvid.py" \
  "m UPGRADE" "Missing plugins From GitHub" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) rm -f $filename_temp
            rm -f $filename_conf
            do_nano_main
            do_plugins_menu ;;
      b\ *) do_plugins_edit
            do_plugins_menu ;;
      c\ *) nano plugins/secfast.py
            do_plugins_menu ;;
      d\ *) nano plugins/secstill.py
            do_plugins_menu ;;
      e\ *) nano plugins/secvid.py
            do_plugins_menu ;;
      f\ *) nano plugins/secQTL.py
            do_plugins_menu ;;
      g\ *) nano plugins/TLlong.py
            do_plugins_menu;;
      h\ *) nano plugins/TLshort.py
            do_plugins_menu ;;
      i\ *) nano plugins/shopcam.py
            do_plugins_menu ;;
      j\ *) nano plugins/dashcam.py
            do_plugins_menu ;;
      k\ *) nano plugins/slowmo.py
            do_plugins_menu ;;
      l\ *) nano plugins/strmvid.py
            do_plugins_menu ;;
      m\ *) clear
            curl -L https://raw.github.com/pageauc/pi-timolo/master/source/plugins-install.sh | bash
            do_anykey
            do_plugins_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_upgrade()
{
  if (whiptail --title "GitHub Upgrade pi-timolo" --yesno "Upgrade pi-timolo files from GitHub. Config files will not be changed" 8 65 --yes-button "upgrade" --no-button "Cancel" ) then
    curl -L https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh | bash
    do_anykey
    ./menubox.sh
  fi
}

#------------------------------------------------------------------------------
function do_about()
{
  whiptail --title "About menubox.sh" --msgbox " \
   pi-timolo - Pi-Timelapse, Motion, Lowlight
        written by Claude Pageau

 Manage pi-timolo operation, configuration
 and utilities using this whiptail menu system.

 for Detailed Instructions on how to use
 the pi-timolo program and utilities See GitHub Wiki

     https://github.com/pageauc/pi-timolo/wiki

\
" 35 70 35

}

#------------------------------------------------------------------------------
function do_main_menu ()
{
  cd $DIR
  init_status
  temp="$(/opt/vc/bin/vcgencmd measure_temp)"
  SELECTION=$(whiptail --title "pi-timolo Main Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --cancel-button Quit --ok-button Select \
  "a $PTMLO_1" "$PTMLO_2" \
  "b $WEB_1" "$WEB_2" \
  "c SETTINGS" "Change Program Configuration Files" \
  "d PLUGINS" "Edit Plugin Files" \
  "e CREATE" "MP4 Timelapse Video from jpg Images" \
  "f CONVERT" "Video from h264 to MP4 or Join multiple MP4 Videos" \
  "g RCLONE" "Manage File Transfers to Remote Storage" \
  "h REMOTE" "Manage pi-timolo using watch-app.sh" \
  "i UPGRADE" "Program Files from GitHub.com" \
  "j STATUS" "CPU $temp   Select to Refresh" \
  "k HELP" "View Readme.md" \
  "l ABOUT" "menubox.sh" \
  "q QUIT" "Exit This Menu Program"  3>&1 1>&2 2>&3)

  RET=$?
  if [ $RET -eq 1 ]; then
    exit 0
  elif [ $RET -eq 0 ]; then
    case "$SELECTION" in
      a\ *) do_pi_timolo ;;
      b\ *) do_webserver ;;
      c\ *) do_settings_menu ;;
      d\ *) do_plugins_menu ;;
      e\ *) do_makevideo_menu ;;
      f\ *) do_convid_menu ;;
      g\ *) do_sync_menu ;;
      h\ *) do_watch_menu ;;
      i\ *) clear
            do_upgrade ;;
      j\ *) clear
            do_main_menu ;;
      k\ *) pandoc -f markdown -t plain  Readme.md | more
            do_anykey
            do_main_menu ;;
      l\ *) do_about
            do_main_menu ;;
      q\ *) clear
            exit ;;
         *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
#                                Main Script
#------------------------------------------------------------------------------

do_main_menu
