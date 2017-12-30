#!/bin/bash
progName=$(basename -- "$0")
echo "$progName ver 9.6  written by Claude Pageau"

echo "$0 is Running.  
 This is a sample script that will be
 replaced by watch-app.sh if watch_config-On=true
 This will enable remote configuration from a remote storage service

 Upload a script called remote-run.sh to the folder pointed to by
 watch-app.sh variable sync_dir variable.  watch-app.sh will 
 download and execute the script if it is named remote-run.sh

 See pi-timolo GitHub Wiki for more details 

$progName Bye ...
"
