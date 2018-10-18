"""
This module will be imported into pi-timolo.py and will
execute the userMotionCode function after
motion is detected.  The filenamePath will be passed
in case you want to process the file as an attachment
or include in a message, Etc.  If you need to import other
python modules they can be added to the top of this
module and used in the userMotionCode.
You can also include other functions within this module
as long as they are directly or indirectly called
within the userMotionCode function since that is
the only function that is called in the pi-timolo.py
program when motion is detected.
For more information see pi-timolo github Wiki
"""

#------------------------------------------------------------------------------
def userMotionCode(filenamePath):
    """
    Users can put code here that needs to be run
    after motion detected and image/video taken
    Eg Notify or activate something.

    Note all functions and variables will be imported.
    pi-timolo.py will execute this function userMotionCode(filename)
    in pi-timolo.py per example below

        user_motion_code.userMotionCode(filename)

    """
    # Insert User code Below
    # print("User Code Executing from userMotionCode function")
    # print("file path is %s" % filenamePath)
