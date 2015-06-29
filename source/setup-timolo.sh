#!/bin/bash
echo "    Downloading and Installing pi-timolo dependencies."
echo "    One Moment Please ......."
sudo apt-get install -y python-picamera  python-imaging mencoder dos2unix gpac
sudo chmod +x gdrive
sudo cp gdrive /usr/local/bin
echo "    Install complete."
echo "    Edit the config.py variables to suit your needs per comments"
echo "nano config.py"
echo "    Run pi-timolo.py with command below to Test.  See Readme.md"
echo "    for additional instructions"
echo "sudo ./pi-timolo.py"
echo "See Readme.md for setting up gdrive security token"
