#!/bin/sh
ip address list | grep inet | grep -v 127.0.0 | cut -d " " -f 6 | cut -d "/" -f 1
