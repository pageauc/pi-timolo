#!/bin/bash

echo "This script will convert an h264 rpi camera video to mp4"
echo "so it can be viewed using a regular media player "
echo "To install MP4Box execute the command below"
echo " sudo apt-get install -y gpac"
echo "usage"
echo "$0 filename.h264"

MP4Box -fps 30 -add $1.h264 $1.mp4
