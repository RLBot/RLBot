import ctypes

MAX_PLAYERS = 10
MAX_NAME_LENGTH = 32


def get_player_configuration_list_type():
    return PlayerConfiguration * MAX_PLAYERS


class PlayerConfiguration(ctypes.Structure):
    _fields_ = [("bBot", ctypes.c_bool),
                ("bRLBotControlled", ctypes.c_bool),
                ("fBotSkill", ctypes.c_float),
                ("iHumanIndex", ctypes.c_int),
                ("wName", ctypes.c_wchar * MAX_NAME_LENGTH),
                ("ucTeam", ctypes.c_ubyte),
                ("ucTeamColorID", ctypes.c_ubyte),
                ("ucCustomColorID", ctypes.c_ubyte),
                ("iCarID", ctypes.c_int),
                ("iDecalID", ctypes.c_int),
                ("iWheelsID", ctypes.c_int),
                ("iBoostID", ctypes.c_int),
                ("iAntennaID", ctypes.c_int),
                ("iHatID", ctypes.c_int),
                ("iPaintFinishID", ctypes.c_int),
                ("iCustomFinishID", ctypes.c_int),
                ("iEngineAudioID", ctypes.c_int),
                ("iTrailsID", ctypes.c_int),
                ("iGoalExplosionID", ctypes.c_int)]


class MatchSettings(ctypes.Structure):
    _fields_ = [("numPlayers", ctypes.c_int),
                ("GameMode", ctypes.c_uint),
                ("GameMap", ctypes.c_uint),
                ("MapVariation", ctypes.c_uint),
                ("skipReplays", ctypes.c_bool),
                ("instantStart", ctypes.c_bool),
               ]


class MutatorSettings(ctypes.Structure):
    _fields_ = [("MatchLength", ctypes.c_uint),
                ("BoostOptions", ctypes.c_uint),
                ]


class MatchConfigurationWrapper(ctypes.Structure):
    _fields_ = [("playerConfiguration", get_player_configuration_list_type()),
                ("matchSettings", MatchSettings),
                ("mutatorSettings", MutatorSettings),
               ]


def get_player_configuration_list(match_configuration_wrapper):
    player_list = []
    for i in range(MAX_PLAYERS):
        player_list.append(PlayerConfiguration())
    return match_configuration_wrapper.playerConfiguration
