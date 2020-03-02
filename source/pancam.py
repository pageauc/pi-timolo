''' Implement a pantilt capability for pi=timolo using the pimoroni pantilthat
    You will need to import the pantilthat module per
       sudo apt-get install -y pantilthat

    You can edit the CAM_STOPS list for the required camera positions.
    Also edit any __init__ variables to suit

    Example Test implementation

    import pancam
    cam = pancam.CamMove()
    cam_pos = 0
    while True:
        cam_pos = cam.move(cam_pos)

'''

import time
import sys

try:
    import pantilthat
except ImportError:
    print('ERROR - Failed to import pantilthat')
    print('        Install modules per  sudo apt-get install pantilthat')
    sys.exit()

class CamMove():
    ''' Use pimoroni pantilthat to pan left/right for each timelapse image
        written by Claude Pageau
    '''
    def __init__(self):
        try:  # Try to read variables from config.py
            from config import verbose
            self.VERBOSE = verbose
            from config import CAM_STOPS 
            self.CAM_STOPS = CAM_STOPS
        except ImportError:  # Set default cam stop positions if import fails
            self.VERBOSE = True
            self.CAM_STOPS = [(90, 0),
                              (60, 0),
                              (30, 0),
                              (0, 0),
                              (-30, 0),
                              (-60, 0),
                              (-90, 0),
                              (-60, 0),
                              (-30, 0),
                              (0, 0),
                              (30, 0),
                              (60, 0)
                             ]
        self.PAN_MAX = 90       # max pimoroni hat pan pos is -90 to + 90
        self.TILT_MAX = 90      # max pimoroni hat tilt pos is -90 to + 90
        self.PANTILT_DELAY = .001  # short delay for moving servo
        self.cam_pos = 0        # set sequence start position

    def move(self, next_stop=0):
        ''' Move the pan tilt servos to angles per CAM_STOPS list index
        '''
        if next_stop >= len(self.CAM_STOPS):
            self.cam_pos = 0
        # Get the next cam position
        self.pan, self.tilt = self.CAM_STOPS[self.cam_pos]
        # for pimoroni pantilt servos
        # Maximum pan and tilt limits are -90 to + 90
        if self.pan > self.PAN_MAX:
            self.pan = self.PAN_MAX
        if self.pan < -self.PAN_MAX:
            self.pan = -self.PAN_MAX
        if self.tilt > self.TILT_MAX:
            self.tilt = self.TILT_MAX
        if self.tilt < -self.TILT_MAX:
            self.tilt = -self.TILT_MAX
        if self.VERBOSE:
            print('pancam - Move to Pos %i/%i at pantilt(%i, %i)' % 
                  (self.cam_pos, len(self.CAM_STOPS), self.pan, self.tilt))
        pantilthat.pan(self.pan)       # move pan servo
        time.sleep(self.PANTILT_DELAY) # give time for servo to move
        pantilthat.tilt(self.tilt)     # move tilt servo
        time.sleep(self.PANTILT_DELAY) # give time for servo to move
        self.cam_pos += 1
        return self.cam_pos
