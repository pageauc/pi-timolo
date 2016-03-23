#!/bin/bash
echo "=============================================="
echo "pi-timolo ver 2.9  Install Dependencies ...."
echo "NOTE: To upgrade pi-timolo rename pi-timolo.py and rerun this setup."
echo "      eg mv pi-timolo.py pi-timolo.py.old"
echo "=============================================="
if [ ! -e pi-timolo.py ]; then
  echo "Upgrading  - Downloading pi-timolo.tar from github.  One Moment Please ....."
  if [ -e pi-timolo.tar ]; then
    sudo rm pi-timolo.tar
  fi
  wget https://raw.github.com/pageauc/pi-timolo/master/pi-timolo.tar
  echo "Extracting - pi-timolo.tar to current folder"
  if [ -e config.py ]; then
    echo "Saving previous config.py to config.py.prev"
    cp config.py config.py.prev
  fi
  tar -pxvf pi-timolo.tar
fi
echo "Download and Install pi-timolo dependencies. One Moment Please ..."
sudo apt-get install -y python-picamera python-imaging dos2unix python-pyexiv2 libav-tools
if [ -e gdrive ]; then
  echo "Upgrading  - Copying gdrive to /usr/local/bin/gdrive"
  sudo chmod +x gdrive
  sudo cp gdrive /usr/local/bin
  echo "============== gdrive version ================"  
  echo "/usr/local/bin/gdrive version"
  /usr/local/bin/gdrive | grep version
  echo "See Readme.md for setting up gdrive security token"
else
  echo "Error - Could not find gdrive file in current folder.  Please investigate ..."
  echo "pi-timolo syncing feature will not be available"
fi
echo "============= SETUP COMPLETE ================"
echo ""
echo "1 - Edit the config.py variables to suit your needs per comments"
echo ""
echo "nano config.py"
echo ""
echo "2 - Run pi-timolo.py with command below to Test. ctrl-c to exit"
echo ""
echo "python ./pi-timolo.py"
echo ""
echo "3 - See Readme.md for additional instructions."
echo "=============================================="

