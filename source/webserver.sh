#!/bin/bash
# This script will run the webserver.py as a background task
# You will then be able close the terminal session.  To auto start
# Add the following command to the /etc/rc.local
# /home/pi/webserver/webserver.sh start

progpath="/home/pi/pi-timolo"
progname="webserver.py"

echo "$0 ver 1.1 written by Claude Pageau"
echo "-----------------------------------------------"
cd "$progpath"

# Check if progname exists
if [ ! -e $progpath/$progname ] ; then
  echo "ERROR   - Could Not Find $progpath/$progname"
  exit 1
fi

if [ -z "$( pgrep -f $progpath/$progname )" ]; then
  if [ "$1" = "start" ]; then
     echo "START   - Start $progpath/$progname in Background ..."
     $progpath/$progname >/dev/null 2>&1 &
  fi
else
  if [ "$1" = "stop" ]; then
    echo "STATUS  - Stopping $progpath/$progname ...."
    progPID=$( pgrep -f $progpath/$progname )
    sudo kill $progPID
  fi
fi

if [ -z "$( pgrep -f $progpath/$progname )" ]; then
    echo "STATUS  - $progpath/$progname is Not Running ..."
    echo "INFO    - To Start $progpath/$progname execute command below"
    echo "INFO    - $0 start"
else
    progPID=$(pgrep -f $progpath/$progname)
    echo "STATUS  - $progpath/$progname is Running ..."
    echo "STATUS  - PID is $progPID"
    echo "INFO    - To Stop $progpath/$progname execute command below"
    echo "INFO    - $0 stop"
fi
echo "Done"
