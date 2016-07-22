#!/bin/sh
echo "-----------------------------"
echo "IP Addresses on This Computer"
echo "-----------------------------"
ifconfig | grep 'inet ' | grep -v 127.0.0 | cut -d " " -f 12
echo "---------- Done -------------"
