import ctypes


class PlayerInput(ctypes.Structure):
    _fields_ = [("fThrottle", ctypes.c_float),
                ("fSteer", ctypes.c_float),
                ("fPitch", ctypes.c_float),
                ("fYaw", ctypes.c_float),
                ("fRoll", ctypes.c_float),
                ("bJump", ctypes.c_bool),
                ("bBoost", ctypes.c_bool),
                ("bHandbrake", ctypes.c_bool)]
