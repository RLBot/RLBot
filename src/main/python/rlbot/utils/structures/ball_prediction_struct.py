import ctypes

from rlbot.utils.structures.game_data_struct import Physics

MAX_SLICES = 360


class Slice(ctypes.Structure):
    _fields_ = [("physics", Physics),
                ("game_seconds", ctypes.c_float)]


class BallPrediction(ctypes.Structure):
    _fields_ = [("slices", Slice * MAX_SLICES),
                ('num_slices', ctypes.c_int)]
