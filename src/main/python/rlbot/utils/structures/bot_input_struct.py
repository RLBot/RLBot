import ctypes


class PlayerInput(ctypes.Structure):
    _fields_ = [("throttle", ctypes.c_float),
                ("steer", ctypes.c_float),
                ("pitch", ctypes.c_float),
                ("yaw", ctypes.c_float),
                ("roll", ctypes.c_float),
                ("jump", ctypes.c_bool),
                ("boost", ctypes.c_bool),
                ("handbrake", ctypes.c_bool),
                ("use_item", ctypes.c_bool)]
