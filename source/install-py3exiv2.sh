#!/bin/bash
ver="5.1"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# get cur dir of this script progName=$(basename -- "$0")
cd $DIR
echo "$progName $ver  written by Claude Pageau"
echo "INFO  : Install Dependencies"
sudo apt-get install -y git
sudo apt-get install -y python-all-dev libexiv2-dev libboost-python-dev
sudo apt-get install -y g++
echo "INFO  : Done Dependencies ..."
if [ -d py3exiv2 ]; then
    echo "WARN  : py3exiv2 Folder Already Exists"
else
    echo "INFO  : git clone https://github.com/mcmclx/py3exiv2.git"
    git clone https://github.com/mcmclx/py3exiv2.git
fi
cd py3exiv2
echo "INFO  : Running python3 configure"
python3 configure.py
echo "INFO  : Compile from Source per build.sh"
echo "INFO  : This will Take Several Minutes So Be Patient ..."
./build.sh
echo "INFO  : Installing pyexiv2 support for python3 per build.sh -i"
sudo ./build.sh -i
echo "INFO  : python3 pyexiv2 Support Added.

    To Test open python3 console and
    test import of pyexiv2 per commands below

    python3
    import pyexiv2

ctrl-d to exit python 3

    If import was Successful, You Can Delete py3exiv2 directory per
    
        sudo rm -r py3exiv2

Bye ...
"

