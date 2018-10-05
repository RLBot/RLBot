import ctypes

from rlbot.utils.structures.game_data_struct import Physics

MAX_SLICES = 3600


class Slice(ctypes.Structure):
    _fields_ = [("physics", Physics)]


class BallPrediction(ctypes.Structure):
    _fields_ = [("slices", Slice * MAX_SLICES),
                ('slices_length', ctypes.c_int)]
