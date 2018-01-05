#!/bin/bash
# Convenient pi-timolo-install.sh script written by Claude Pageau 1-Jul-2016
ver="5.00"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
echo "$0 $ver  written by Claude Pageau"

# List of valid plugins to Check/Download
PLUGINS_DIR='plugins'  # Default folder install location
pluginFiles=("__init__.py" "dashcam.py" "secfast.py" "secQTL.py" "secstill.py" \
"secvid.py" "shopcam.py" "slowmo.py" "TLlong.py" "TLshort.py")

mkdir -p $PLUGINS_DIR
cd $PLUGINS_DIR
INSTALL_PATH=$( pwd )
echo "INFO  - Current Folder is $INSTALL_PATH"

for fname in "${pluginFiles[@]}" ; do
  if [ -f $fname ]; then     # check if local file exists.
    echo "INFO  - $fname Skip Download Since Local Copy Found"
  else
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR - $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/pi-timolo/master/source/plugins/$fname"
        fi
    fi
  fi
done

echo "
      How to Implement pi-timolo plugins
-----------------------------------------------------------
Plugins configure pi-timolo for special tasks by overlaying
the plugin variables over the current config.py settings.
Plugin Files can be found in the pi-timolo/plugins subfolder.
You can customize a particular plugin or create your own.

To enable pi-timolo plugins

    cd ~/pi-timolo
    nano config.py

Edit pluginEnable= variable per below.

    pluginEnable=True

Edit pluginName=  variable to point to a plugin file
in the plugins folder. Do Not include .py extension.
ctrl-x y to exit nano and save changes.

For further details about plugins, See Readme.md or GitHub wiki
here https://github.com/pageauc/pi-timolo/wiki/How-to-Use-Plugins

Good Luck Claude ...
Bye"

