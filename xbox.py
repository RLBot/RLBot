# Thanks to https://github.com/r4dian/Xbox-360-Controller-for-Python/blob/master/xinput.py

import ctypes
import sys
import time, array
from operator import itemgetter, attrgetter
from itertools import count, starmap
#from pyglet import event

# structs according to
# http://msdn.microsoft.com/en-gb/library/windows/desktop/ee417001%28v=vs.85%29.aspx


class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ('buttons', ctypes.c_ushort),  # wButtons
        ('left_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('right_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('l_thumb_x', ctypes.c_short),  # sThumbLX
        ('l_thumb_y', ctypes.c_short),  # sThumbLY
        ('r_thumb_x', ctypes.c_short),  # sThumbRx
        ('r_thumb_y', ctypes.c_short),  # sThumbRy
    ]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ('packet_number', ctypes.c_ulong),  # dwPacketNumber
        ('gamepad', XINPUT_GAMEPAD),  # Gamepad
    ]


class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]

xinput = ctypes.windll.xinput9_1_0  # Check you C:\Windows\System32 folder for xinput dlls
# xinput1_2, xinput1_1 (32-bit Vista SP1)
# xinput1_3 (64-bit Vista SP1)

ERROR_DEVICE_NOT_CONNECTED = 1167
ERROR_SUCCESS = 0
    
def get_state(device_number):
        "Get the state of the controller represented by this object"
        state = XINPUT_STATE()
        res = xinput.XInputGetState(device_number, ctypes.byref(state))
        if res == ERROR_SUCCESS:
            return state
        if res != ERROR_DEVICE_NOT_CONNECTED:
            raise RuntimeError(
                "Unknown error %d attempting to get state of device %d" % (res, device_number))
        # else return None (device is not connected)

def get_xbox_output():
    state = get_state(0)
    output = array.array('f',(0,)*5) # Create a tuple with 5 controller outputs
    buttons = state.gamepad.buttons
    if (buttons >= 16384):
        # x is pressed
        output[2] = 1.0
        buttons = buttons - 16384
    else:
        output[2] = -1.0

    if (buttons >= 8192):
        # b is pressed
        output[3] = 1.0
        buttons = buttons - 8192
    else:
        output[3] = -1.0

    if (buttons >= 4096):
        # a is pressed
        output[4] = 1.0
    else:
        output[4] = -1.0

    if (state.gamepad.left_trigger > 100):
        # Going backwards
        output[0] = -2.0

    if (state.gamepad.right_trigger > 100):
        # Going backwards
        output[0] = 2.0

    if (state.gamepad.l_thumb_y > 30000):
        # Weird case translation from xbox to pc.  When in midair you press y forward to tilt which is forward on keyboard
        output[0] = 2.0

    if (state.gamepad.l_thumb_y < -30000):
        # Weird case translation from xbox to pc.  When in midair you press y backward to tilt which is back on keyboard
        output[0] = -2.0

    if (state.gamepad.l_thumb_x < -8000):
        # Go right
        output[1] = -2.0

    if (state.gamepad.l_thumb_x > 8000):
        # Go left
        output[1] = 2.0
    
    return output
