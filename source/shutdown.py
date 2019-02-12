#!/usr/bin/env python
# written by Claude Pageau

# Safely shutdown Raspberry pi using a momentary switch
# use a physical push button, toggle switch or just short two gpio jumper wires
# You can salvage an old switch from a computer or other device.
# Connect momentary switch to pin 5 and 6 (default)
# or set gpio_pin variable to desired pin below
#
# Set button_hold variable to number of seconds to
# hold down momentary switch before action taken
# default is 2 seconds.  0=No delay
#
# Add line below to sudo crontab -e (without #) change path as necessary
# @reboot /home/pi/shutdown/shutdown.py
#
# make sure shutdown.py is executable
# chmod +x shutdown.py
#
# After initial power boot press switch for specified time
# to Initiate safe shutown (halt)
# After shutdown wait 5 seconds then press switch again
# for specified time to initiate a startup
# Wait a few seconds between between operations

import RPi.GPIO as GPIO
import time
import subprocess

button_hold = 2       # number of seconds to hold button before action taken
gpio_pin = 5          # Set GPIO pin you want to use.  default is 5 and ground is 6

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
        if hold_time > button_hold:
            shutdown = True
    time.sleep(.1)
subprocess.call("/sbin/shutdown -h now", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
