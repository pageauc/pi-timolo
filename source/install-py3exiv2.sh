#!/bin/bash
progVer="5.3"
progName=$(basename -- "$0")
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "$progName $progVer  written by Claude Pageau"
echo "INFO  : Compile python 3 pyexiv2 support from Source"
echo "----------------------------------------------------"
TOTAL_MEM=$(free -m | grep Mem | tr -s " " | cut -f 2 -d " ")
echo "INFO  : Total RAM memory is $TOTAL_MEM mb"

if [ "$TOTAL_MEM" -lt "550" ] ; then
    echo "ERROR : $TOTAL_MEM mb Not enough RAM memory"
    echo "ERROR : To Compile python3 pyexiv2 library from Source."
    echo "Bye ..."
    exit 1
fi

cd $DIR
echo "INFO  : Install Dependencies"
sudo apt-get install -y git
sudo apt-get install -y python-all-dev
sudo apt-get install -y libexiv2-dev
sudo apt-get install -y libboost-python-dev
sudo apt-get install -y g++
echo "INFO  : Done Dependencies ..."

if [ -d py3exiv2 ]; then
    echo "WARN  : py3exiv2 Folder Already Exists"
else
    echo "INFO  : git clone https://github.com/mcmclx/py3exiv2.git"
    git clone https://github.com/mcmclx/py3exiv2.git
    if [ $? -ne 0 ]; then 
        echo "ERROR : Clone Failed. Possible Cause Internet Problem"
        echo "INFO  : Investigate and Try Again"
        echo "$progName $progVer  Bye ..."
        exit 1        
    fi    
fi

cd py3exiv2
echo "INFO  : Current Directory is $DIR/py3exiv2"
echo "INFO  : Running: python3 configure.py"
python3 configure.py
echo "INFO  : Done configure.py "
echo "INFO  : Start Compile of pyexiv2 for python3 from Source per build.sh"
echo "INFO  : This Might Take Some Time ...."
./build.sh
if [ $? -ne 0 ]; then
    echo "ERROR : Compile Failed. Investigate Problem"
    echo "$progName $progVer  Bye ..."
    exit 1
fi
echo "INFO  : Done Compile"
echo "INFO  : Install pyexiv2 Files to /usr/lib/python3/dist-packages/pyexiv2"
sudo ./build.sh -i
echo "INFO  : Install /usr/lib/python3/dist-packages/libexiv2python.so"
echo "INFO  : Install Package files to Dir /usr/lib/python3/dist-packages/pyexiv2"
echo "INFO  : Done Copy"
echo "INFO  : Added python3 pyexiv2 library module.
-------
To Test 
-------
Open python3 console and import pyexiv2 
per commands below

    python3
    import pyexiv2
    pyexiv2.__version__
    
ctrl-d to exit python 3 Console

If import was Successful, You Can Delete py3exiv2 directory per

    sudo rm -r py3exiv2

$progName $progVer
Bye ...
"
exit 0
