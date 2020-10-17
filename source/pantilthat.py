#!/usr/bin/python
'''
Driver for waveshare pantilthat modified by Claude Pageau to
make compatible with pimoroni pantilthat that uses pan and tilt
servo min/max positions of -90 to +90 with 0 being servo center
Default settings can be overridden per help() function.
'''
import time
import math
import smbus

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PanTilt:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __MODE2              = 0x01
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.prog_ver = '0.7'
    self.pan_servo = 0  # pan servo
    self.tilt_servo = 1  # tilt servo
    self.flip_servo = False  # Do Not Flip Pan and Tilt
    self.address = address
    self.debug = debug
    if (self.debug):
        print("Reseting pantilt")
    self.bus = smbus.SMBus(1)
    self.setPWMFreq(50)         # Set default setting
    self.setServoPulse(1, 500)  # Set default setting
    self.write(self.__MODE1, 0x00)

  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
        print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
        print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result

  def setPWMFreq(self, freq=50):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
        print("Setting PWM frequency to %d Hz" % freq)
        print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
        print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)
    self.write(self.__MODE2, 0x04)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
        print("channel: %d LED_ON: %d LED_OFF: %d" % (channel, on, off))

  def setServoPulse(self, channel=1, pulse=5000):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
    self.setPWM(channel, 0, int(pulse))

  def setRotationAngle(self, channel, Angle):
    ''' channel is the servo number. where 0=pan and 1=tilt
        Make Compatilble with Pimoroni pantilthat setup
        using -90 and + 90 servo values.
        if flip_server = False.  0 = servo center position
    '''
    Angle = Angle + 90
    if(Angle >= 0 and Angle <= 180):
        temp = Angle * (2000 / 180) + 501
        self.setServoPulse(channel, temp)
    else:
        print("Angle %i is Out of Range must be between -90 and +90" % Angle)

  def pan(self, angle):
    ''' Pan Left and Right with Left = -90 and Right = 90
        if flip_servo = False
    '''
    if angle > 90:
        angle = 90
    if angle < -90:
        angle = -90
    if self.flip_servo:
        self.setRotationAngle(self.tilt_servo, angle)
    else:
        self.setRotationAngle(self.pan_servo, angle)

  def tilt(self, angle):
    ''' Tilt Up and Down  with Up = -90 and Down = 90
        if flip_servo = False
    '''
    if angle > 90:
        angle = 90
    if angle < -90:
        angle = -90
    if self.flip_servo:
        self.setRotationAngle(self.pan_servo, angle)
    else:
        self.setRotationAngle(self.tilt_servo, angle)

  def start(self):
    self.write(self.__MODE2, 0x04)
    # Just restore the stopped state that should be set for stop

  def stop(self):
    self.write(self.__MODE2, 0x00) # Please use initialization or __MODE2 =0x04

  def help(self):
    '''Display library help, implemenation examples and options
    '''
    print('pantilthat.py Driver for waveshare pan tilt hat hardware.')
    print('Modified by Claude Pageau based on original driver at https://github.com/waveshare/Pan-Tilt-HAT')
    print('This driver uses BCM2835 For Details See http://www.airspayce.com/mikem/bcm2835/\n')
    print('Implementation Example\n')
    print('   from waveshare.pantilthat import PanTilt # import library')
    print('   pantilthat = PanTilt() # Initialize pantilt servo library')
    print('   pantilthat.pan(0)      # valid values -90 to +90 Move pan servo horizontally to center position')
    print('   pantilthat.tilt(-10)   # valid values -90 to +90 Move tilt servo vertically to slightly above center\n')
    print('Other Options\n')
    print('   pantilthat.__version__()   # Display version Number')
    print('   pantilthat.setPWMFreq(50)  # Optional pwm frequency setting')
    print('   pantilthat.setServoPulse(1, 500)  # Optional pwm servo pulse setting')
    print('   pantilthat.debug = True        # Display additional servo information messages')
    print('   pantilthat.flip_servo = False  # Optionally flips pan and tilt in case servo plugin is different')
    print('   pantilthat.stop()   # Turn Off pwm to both servo channels')
    print('   pantilthat.start()  # Turn On pwm to both servo channels after stop')
    print('   pantilthat.help()   # Display this help message')
    print('Note: currently there is no timeout similar to Pimoroni')
    print('Bye ...')

  def __version__(self):
    return self.prog_ver