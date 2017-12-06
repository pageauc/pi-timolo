#!/bin/bash

ver="9.00"

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
   echo "######################################"
   echo "#          Review Output             #"
   echo "######################################"
   read -p "  Press Enter to Return to Main Menu"
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
     WEB_1="STOP"
     WEB_2="webserver.py - PID is $webserver_pid"
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
  if [ -e $DIR/makevideo.conf ] ; then
     /bin/nano $DIR/makevideo.conf
  else
     whiptail --msgbox "ERROR - $DIR/makevideo.conf File Not Found. Please Investigate." 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_makevideo_menu ()
{
  SELECTION=$(whiptail --title "makevideo.sh Menu" --menu "Arrow/Enter to Run or Tab Key" 20 67 7 --cancel-button Back --ok-button Select \
  "a RUN" "makevideo.sh - motion or timelapse jpg's to mp4 video" \
  "b EDIT" "nano makevideo.conf video settings" \
  "c VIEW" "makevideo.conf file" \
  "q BACK" "to Main Menu"  3>&1 1>&2 2>&3)

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SELECTION" in
      a\ *) do_makevideo ;;
      b\ *) do_makevideo_config
            do_makevideo_menu ;;
      c\ *) clear
            cat $DIR/makevideo.conf
            do_anykey
            do_makevideo_menu ;;
      q\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognized option" 10 65 1 ;;
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
function do_video_config ()
{
    if [ -e $DIR/convid.conf ] ; then
        /bin/nano $DIR/convid.conf
    else
        whiptail --msgbox "ERROR - $DIR/convid.conf File Not Found. Please Investigate." 20 65 1
    fi
}

#------------------------------------------------------------------------------
function do_convid_menu ()
{

  VID_SEL=$( whiptail --title "convid.sh Menu" --menu "Arrow/Enter to Run or Tab Key" 0 0 0 --cancel-button Back --ok-button Select \
  "a JOIN" "JOIN multiple motion MP4 videos into larger videos" \
  "b CONVERT" "motion h264 files to MP4 videos" \
  "c EDIT" "nano convid.conf settings" \
  "d VIEW" "convid.conf settings." \
  "q BACK" "to Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$VID_SEL" in
      a\ *) do_join_video ;;
      b\ *) do_convert_video ;;
      c\ *) do_video_config
            do_convid_menu ;;
      d\ *) clear
            cat $DIR/convid.conf
            do_anykey
            do_convid_menu ;;
      q\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi

}

#------------------------------------------------------------------------------
function do_sync ()
{
  whiptail --msgbox "Insert gdrive sync Code Here" 20 60 1

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
  "c EDIT" "nano makevideo.conf" \
  "d VIEW" "makevideo.conf" \
  "e EDIT" "nano convid.conf" \
  "f VIEW" "convid.conf" \
  "q BACK" "to Main Menu" 3>&1 1>&2 2>&3 )

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
      c\ *) do_makevideo_config ;;
      d\ *) clear
            cat $DIR/makevideo.conf
            do_anykey
            do_settings_menu ;;
      e\ *) do_video_config
            do_settings_menu;;
      f\ *) clear
            cat $DIR/convid.conf
            do_anykey
            do_settings_menu ;;
      q\ *) clear
            rm -f $filename_temp
            rm -f $filename_conf
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi

}

#------------------------------------------------------------------------------
function do_plugins_menu ()
{
  SET_SEL=$( whiptail --title "Edit Plugins Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a secfast" "nano plugins/secfast.py" \
  "b secstill" "nano plugins/secstill.py" \
  "c secvid" "nano plugins/secvid.py" \
  "d secQTL" "nano plugins/secQTL.py" \
  "e TLlong" "nano plugins/TLlong.py" \
  "f TLshort" "nano plugins/TLshort.py" \
  "g shopcam" "nano plugins/shopcam.py" \
  "h dashcam" "nano plugins/dashcam.py" \
  "i slowmo" "nano plugins/slowmo.py" \
  "q BACK" "to Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then

    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) nano plugins/secfast.py
            do_plugins_menu ;;
      b\ *) nano plugins/secstill.py
            do_plugins_menu ;;
      c\ *) nano plugins/secvid.py
            do_plugins_menu ;;
      d\ *) nano plugins/secQTL.py
            do_plugins_menu ;;
      e\ *) nano plugins/TLlong.py
            do_plugins_menu;;
      f\ *) nano plugins/TLshort.py
            do_plugins_menu ;;
      g\ *) nano plugins/shopcam.py
            do_plugins_menu ;;
      h\ *) nano plugins/dashcam.py
            do_plugins_menu ;;
      i\ *) nano plugins/slowmo.py
            do_plugins_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi

}

#------------------------------------------------------------------------------
function do_upgrade()
{
  if (whiptail --title "GitHub Upgrade pi-timolo" --yesno "Upgrade pi-timolo files from GitHub. Config files will not be changed" 8 65 --yes-button "upgrade" --no-button "Cancel" ) then
    curl -L https://raw.github.com/pageauc/pi-timolo/master/source/pi-timolo-install.sh | bash
    do_anykey
  fi
}

#------------------------------------------------------------------------------
function do_about()
{
  whiptail --title "About" --msgbox " \
   pi-timolo - Pi-Timelapse, Motion, Lowlight
          written by Claude Pageau

   Manage pi-timolo operation, config and utilities
    This script can run via interactive menu or

                menubox syntax
         if no parameter then run menu

menu      - Runs an interactive menu
upgrade   - Perform Upgrade keep previous config files
timolo    - Toggle Start/Stop pi-timolo.py background
webserver - Toggle Start/Stop webserver.py background
join      - join multiple mp4 videos into larger videos
convert   - convert h264 files to MP4 format
timelapse - Make video from source folder jpg images
sync      - perform gdrive sync
settings  - Edit various program settings
about     - About this program
help      - Display help

\
" 35 70 35
}

#------------------------------------------------------------------------------
function do_main_menu ()
{
  init_status
  SELECTION=$(whiptail --title "pi-timolo Main Menu" --menu "Arrow/Enter Selects or Tab Key" 20 70 10 --cancel-button Quit --ok-button Select \
  "a $PTMLO_1" "$PTMLO_2" \
  "b $WEB_1" "$WEB_2" \
  "c SETTINGS" "Change Program Configuration Files" \
  "d PLUGINS" "Edit Plugin Files" \
  "e CREATE" "MP4 Timelapse Video from jpg Images" \
  "f CONVERT" "Video from h264 to MP4 or Join multiple MP4 Videos" \
  "g SYNC" "Configure gdrive sync to google drive" \
  "h UPGRADE" "Program Files from GitHub.com" \
  "i ABOUT" "Information About this Program" \
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
      g\ *) do_sync ;;
      h\ *) do_upgrade ;;
      i\ *) do_about ;;
      q\ *) clear
            exit 0 ;;
         *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
#                                Main Script
#------------------------------------------------------------------------------
if [ $# -eq 0 ] ; then
    while true; do
       do_main_menu
    done
else
    # convert to upper case
    parm=$(echo $1 | awk '{print toupper($0)}')

    case "$parm" in
        HELP)
            do_about
            ;;
        ABOUT)
            do_about
            ;;
        MENU)
            do_main_menu
            ;;
        UPGRADE)
            do_upgrade
            ;;
        TIMOLO)
            do_pi_timolo
            ;;
        WEBSERVER)
            do_webserver
            ;;
        SYNC)
            do_sync
            ;;
        TIMELAPSE)
            do_makevideo
            ;;
        JOIN)
            do_join_video
            ;;
        CONVERT)
            do_convert_video
            ;;
        SETTINGS)
            do_settings_menu
            ;;
    esac
fi