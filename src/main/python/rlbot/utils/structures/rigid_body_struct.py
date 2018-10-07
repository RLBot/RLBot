import ctypes

from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.game_data_struct import Vector3
from rlbot.utils.structures.start_match_structures import MAX_PLAYERS


class Quaternion(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float),
                ("w", ctypes.c_float)]


class RigidBodyState(ctypes.Structure):
    _fields_ = [("location", Vector3),
                ("rotation", Quaternion),
                ("velocity", Vector3),
                ("angular_velocity", Vector3),
                ("frame", ctypes.c_ulong)]


class PlayerRigidBodyState(ctypes.Structure):
    _fields_ = [("state", RigidBodyState),
                ("input", PlayerInput)]


class BallRigidBodyState(ctypes.Structure):
    _fields_ = [("state", RigidBodyState)]


class RigidBodyTick(ctypes.Structure):
    _fields_ = [("ball", BallRigidBodyState),
                ("players", PlayerRigidBodyState * MAX_PLAYERS),
                ("players_length", ctypes.c_int)]
