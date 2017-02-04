#!/bin/bash

ver="4.10"

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
    PTMLO_1="Start pi-timolo"
    PTMLO_2="Start pi-timolo.py in background"
  else
     pi_timolo_pid=$( pgrep -f pi-timolo.py )
     PTMLO_1="Stop pi-timolo"
     PTMLO_2="Stop pi-timolo.py - PID is $pi_timolo_pid"     
  fi

  if [ -z "$( pgrep -f webserver.py )" ]; then
     WEB_1="Start webserver"
     WEB_2="Start webserver.py in background"    
  else
     webserver_pid=$( pgrep -f webserver.py )    
     WEB_1="Stop webserver"
     WEB_2="Stop webserver.py - PID is $webserver_pid"    
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
  if [ -z "$( pgrep -f webserver.py )" ]; then
     ./webserver.py >/dev/null 2>&1 & 
     if [ -z "$( pgrep -f webserver.py )" ]; then 
        whiptail --msgbox "Failed to Start webserver.py   Please Investigate Problem." 20 70
     else
       myip=$(ifconfig | grep 'inet ' | grep -v 127.0.0 | cut -d " " -f 12 | cut -d ":" -f 2 )
       myport=$( grep "web_server_port" config.py | cut -d "=" -f 2 | cut -d "#" -f 1 | awk '{$1=$1};1' )
       whiptail --msgbox --title "Webserver Access" "Access pi-timolo web server from another network computer web browser using url http://$myip:$myport" 15 50
     fi 
  else  
     webserver_pid=$( pgrep -f webserver.py )   
     sudo kill $webserver_pid
     if [ ! -z "$( pgrep -f webserver.py )" ]; then 
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
  "a Run" "makevideo.sh - motion or timelapse jpg's to mp4 video" \
  "b Edit" "nano makevideo.conf video settings" \
  "c View" "makevideo.conf file" \
  "d Back" "Back to Main Menu"  3>&1 1>&2 2>&3)

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
      d\ *) do_main_menu ;;
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
  "a " "Join multiple motion mp4 videos into larger videos" \
  "b " "Convert motion h264 files to mp4 videos" \
  "c " "Edit nano convid.conf settings" \
  "d " "View convid.conf settings." \
  "e " "Back to Main Menu" 3>&1 1>&2 2>&3 )
  
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
      e\ *) do_main_menu ;;
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

#--------------------------------------------------------------------
function do_edit_variable ()
{
  choice=$(cat $filename_temp | grep $SELECTION)

  var=$(echo $choice | cut -d= -f1)
  value=$(echo $choice | cut -d= -f2)
  comment=$( cat $filename_conf | grep $var | cut -d# -f2 )

  echo "${value}" | grep --quiet "True"
  # Exit status 0 means anotherstring was found
  # Exit status 1 means anotherstring was not found
  if [ $? = 0 ] ; then
     newvalue=" False"
     do_edit_save       
  else
     echo "${value}" | grep --quiet "False"
     if [ $? = 0 ] ; then
        newvalue=" True"
        do_edit_save            
     elif  [ $? = 1 ] ; then       
        newvalue=$(whiptail --title "Edit $var (Enter Saves or Tab)" \
                               --inputbox "$comment\n $var=$value" 10 65 "$value" \
                               --ok-button "Save" 3>&1 1>&2 2>&3)
        exitstatus=$?
        if [ ! "$newvalue" = "" ] ; then   # Variable was changed                             
           if [ $exitstatus -eq 1 ] ; then  # Check if Save selected otherwise it was cancelled
              do_edit_save                    
           elif [ $exitstatus -eq 0 ] ; then
             echo "do_edit_variable - Cancel was pressed"
             if echo "${value}" | grep --quiet "${newvalue}" ; then
                do_settings_menu
             else
                do_edit_save
             fi
           fi
        fi
     fi
  fi
  do_settings_menu 
}

#--------------------------------------------------------------------
function do_edit_menu ()
{
  clear
  echo "Copy $filename_conf from $pyconfigfile  Please Wait ...."
  cp $pyconfigfile $filename_conf
  echo "Initialize $filename_temp  Please Wait ...."  
  cat $filename_conf | grep = | cut -f1 -d# | tr -s [:space:] >$filename_temp
  echo "Initializing Settings Menu Please Wait ...."    
  menu_options=()
  while read -r number text; do
    menu_options+=( ${number//\"} "${text//\"}" )
  done < $filename_temp
  
  SELECTION=$( whiptail --title "pi-timolo Settings Menu" \
                       --menu "Arrow/Enter Selects or Tab" 0 0 0 "${menu_options[@]}" --ok-button "Edit" 3>&1 1>&2 2>&3 )  
  RET=$?  
  if [ $RET -eq 1 ] ; then
    do_settings_menu
  elif [ $RET -eq 0 ]; then
    cp $pyconfigfile $filename_conf
    cat $filename_conf | grep = | cut -f1 -d# | tr -s [:space:] >$filename_temp  
    do_edit_variable
  fi
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
  "a " "Menu Edit config.py for pi-timolo & webserver" \
  "b " "Edit nano config.py for pi-timolo & webserver" \
  "c " "View config.py for pi-timolo & webserver" \
  "d " "Edit nano makevideo.conf file" \
  "e " "View makevideo.conf file" \
  "f " "Edit nano convid.conf file" \
  "g " "View convid.conf file" \
  "h " "Back to Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_edit_menu ;;
      b\ *) do_nano_main
            do_settings_menu ;;
      c\ *) more -d config.py
            do_anykey
            do_settings_menu ;;
      d\ *) do_makevideo_config ;;
      e\ *) clear
            cat $DIR/makevideo.conf
            do_anykey
            do_settings_menu ;;
      f\ *) do_video_config 
            do_settings_menu;;
      g\ *) clear
            cat $DIR/convid.conf
            do_anykey
            do_settings_menu ;;
      h\ *) do_main_menu ;;
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
  SELECTION=$(whiptail --title "Main Menu" --menu "Arrow/Enter Selects or Tab Key" 20 70 10 --cancel-button Quit --ok-button Select \
  "a $PTMLO_1" "$PTMLO_2" \
  "b $WEB_1" "$WEB_2" \
  "c Create Video" "Make timelapse mp4 video from jpg images" \
  "d Convert Video" "Convert h264 or Join multiple motion mp4 videos" \
  "e Sync" "Configure gdrive sync to google drive" \
  "f Settings" "Change pi-timolo and webserver settings" \
  "g Upgrade" "Upgrade program files from GitHub.com" "h About" "Information about this program" \
  "q Quit" "Exit This Program"  3>&1 1>&2 2>&3)

  RET=$?
  if [ $RET -eq 1 ]; then
    exit 0
  elif [ $RET -eq 0 ]; then
    case "$SELECTION" in
      a\ *) do_pi_timolo ;;
      b\ *) do_webserver ;;
      c\ *) do_makevideo_menu ;;
      d\ *) do_convid_menu ;;
      e\ *) do_sync ;;
      f\ *) do_settings_menu ;; 
      g\ *) do_upgrade ;;           
      h\ *) do_about ;;
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