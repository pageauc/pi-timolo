#!/bin/bash
echo "    Downloading and Installing pi-timolo dependencies."
ecoh "    One Moment Please ......."
sudo apt-get install python-imaging python-picamera mencoder rsync
echo "    Install complete."
echo "    Edit the config.py variables to suit your needs per comments"
echo "    Run pi-timolo.py with command below to Test.  See Readme.txt"
echo "    for additional instructions"
echo "sudo ./pi-timolo.py"
