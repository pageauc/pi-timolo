#!/bin/sh
# writtem by Claude Pageau 
# Script to run pi-timolo.py in background available here
# wget https://raw.github.com/pageauc/pi-timolo/master/source/timolo.sh
# launch from command line or via entry in /etc/rc.local file
# You may have to change sleep delay if it does not run properly in rc.local
# make sure to make this script executable
# chmod +x timolo.sh
# NOTE : This script can be used as a generic launcher by changing
#        the parameters below
# This script avoids launching the pi-timolo.py script more than once
# since the pi camera hardware cannot be run more than once sumultaneously.
progpath=/home/pi/pi-timolo
progname=pi-timolo.py
proglog=verbose.log

if [ -z "$(ps -ef | grep $progname | grep -v grep)" ]
then
   echo "Start $progpath/$progname   Waiting 10 seconds"
   # delay for boot to complete if running from /etc/rc.local
   sleep 10
   echo "Starting $progpath/$progname in background"
   # If you want to redirect output then comment out below
   # comment command below for no redirection of console output
   $progpath/$progname &  
   # then uncomment line below for logging 
   # python -u $progpath/$progname  > $progpath/$proglog &
   echo "$progpath/$progname started per process PID below"
   ps -ef | grep $progname | grep -v grep
   echo
   echo "If not running then Check setup and permissions"
else
  echo "$progpath/$progname Already Running"
  ps -ef | grep $progname | grep -v grep
  echo
  echo "To end task kill PID above eg sudo kill 1234"
fi
echo "Done"
exit
