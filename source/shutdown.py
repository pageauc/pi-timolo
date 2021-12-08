#!/usr/bin/env python
# written by Claude Pageau.

# Purpose
# Safely shutdown (halt) Raspberry pi using a normally open momentary switch

# Hardware Requirements
# Requires one small normally open momentary push button switch 
# and two short insulated wires.  

# Instructions
# Mount switch and Connect each wire per below.
# Connect control wire from one switch terminal to RPI GPIO control pin 5   (default)
# Connect ground wire from second switch terminal to RPI GPIO ground pin 6 (default)
# or set gpio_pin variable below to desired control pin
# If desired set button_hold_sec variable below to number of seconds to
# hold down momentary switch before action taken
# default is 2 seconds.  0=No delay

# Software Install
#     cd ~
#     mkdir shutdown
#     cd shutdown
#     wget https://raw.github.com/pageauc/pi-timolo/master/source/shutdown.py
#     chmod +x shutdown.py
#     sudo crontab -e
# Add line below to sudo crontab -e (without #) Ctrl-x y to exit nano and save change
#     @reboot /home/pi/shutdown/shutdown.py

# Operating Instructions
# After initial power boot press momentary switch for specfied time
# to Initiate safe shutown (halt).  You can then safely power off RPI
# or
# After halt, wait approx 5 seconds then press switch
# again for specified time to intiate a restart of RPI

import RPi.GPIO as GPIO
import time
import subprocess

button_hold_sec = 2   # default=2 number of seconds to hold button before action taken
gpio_pin = 5   # Set GPIO pin you want to use.  default is 5 and ground is 6

GPIO.setmode(GPIO.BOARD)
# set GPIO pin to input, and enable the internal pull-up resistor
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

start_time  = time.time()
shutdown = False
while not shutdown:
    if GPIO.input(gpio_pin):
        start_time = time.time()
    else:
        hold_time = time.time() - start_time
        if hold_time >= button_hold_sec:
            shutdown = True
    time.sleep(.1)    # short delay to avoid high cpu due to looping 
subprocess.call("/sbin/shutdown -h now", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
