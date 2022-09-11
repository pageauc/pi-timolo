#!/bin/sh
echo "-----------------------------"
echo "IP Addresses on This Computer"
echo "-----------------------------"
ip route get 8.8.8.8 | sed -n '/src/{s/.*src *\([^ ]*\).*/\1/p;q}'
echo "---------- Done -------------"
