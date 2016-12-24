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

progpath="/home/pi/pi-timolo"
progname="pi-timolo.py"
proglog="verbose.log"
progsleep=10

echo "$0 ver 1.1 written by Claude Pageau"
echo "-----------------------------------------------"
cd $progpath

# Check if progname exists
if [ ! -e $progname ] ; then
  echo "ERROR  - Could Not Find $progname"
  exit 1
fi

if [ -z "$( pgrep -f $progname )" ]; then
  if [ "$1" = "start" ]; then
    echo "START   - Start $progpath/$progname in Background"
    # delay for boot to complete if running from /etc/rc.local
    echo "STATUS  - Waiting $progsleep seconds ...."
    sleep $progsleep

    # comment line below for no redirection of console output
    $progpath/$progname  >/dev/null 2>&1 &
    # NOTE set verbose = True in config.py then
    # then uncomment line below for logging 
    # echo "Start $progpath/$progname with log to $progpath/$proglog"
    # python -u $progpath/$progname  > $progpath/$proglog &
  fi
else
  if [ "$1" = "stop" ]; then
    echo "STATUS  - Stopping $progname ...."
    progPID=$( pgrep -f $progname )
    sudo kill $progPID
  fi
fi

if [ -z "$( pgrep -f $progname )" ]; then
    echo "STATUS  - $progname is Not Running ..."
    echo "INFO    - To Start $progname execute command below"
    echo "INFO    - $0 start"
  else
    progPID=$(pgrep -f $progname)
    echo "STATUS  - $progname is Running ..."
    echo "STATUS  - PID is $progPID"
    echo "INFO    - To Stop $progname execute command below"
    echo "INFO    - $0 stop"
fi

