# PI-TIMOLO rclone-samples

## Introduction
This is a collection of sample rclone scripts.  The logic is
identical but variables are different. For details see Wiki
[How to Setup rclone](https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-rclone#sample-rclone-scripts) 

## How to Implement
You can review samples and copy a script to a unique name or edit one of the samples
Change required variables per comments. You should test script before putting
into production as a crontab entry.

    cd ~/pi-timolo.py
    cp rclone-samples/rclone-master.sh ./rclone-test.sh
    
This will copy a copy of the master file into the pi-timolo folder
To edit    
    
    nano rclone-test.sh
    
***ctrl-x y*** to exit and save changes
    
## How To Test script
You must have already setup a remote storage name.  For details See  
[How to Configure a Remote Storage Service](https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-rclone#how-to-configure-a-remote-storage-service)

    ./rclone-test.sh    
        
## How to Automate

See [pi-timolo Wiki How to Automate rclone](https://github.com/pageauc/pi-timolo/wiki/How-to-Setup-rclone#how-to-automate-rclone)