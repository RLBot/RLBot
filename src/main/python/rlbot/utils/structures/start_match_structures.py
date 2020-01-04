import ctypes

MAX_PLAYERS = 64
MAX_NAME_LENGTH = 32


def get_player_configuration_list_type():
    return PlayerConfiguration * MAX_PLAYERS


class Color(ctypes.Structure):
    _fields_ = [("r", ctypes.c_ubyte),
                ("g", ctypes.c_ubyte),
                ("b", ctypes.c_ubyte),
                ("a", ctypes.c_ubyte)]


class PlayerConfiguration(ctypes.Structure):
    _fields_ = [("bot", ctypes.c_bool),
                ("rlbot_controlled", ctypes.c_bool),
                ("bot_skill", ctypes.c_float),
                ("human_index", ctypes.c_int),
                ("name", ctypes.c_wchar * MAX_NAME_LENGTH),
                ("team", ctypes.c_ubyte),
                ("team_color_id", ctypes.c_ubyte),
                ("custom_color_id", ctypes.c_ubyte),
                ("car_id", ctypes.c_int),
                ("decal_id", ctypes.c_int),
                ("wheels_id", ctypes.c_int),
                ("boost_id", ctypes.c_int),
                ("antenna_id", ctypes.c_int),
                ("hat_id", ctypes.c_int),
                ("paint_finish_id", ctypes.c_int),
                ("custom_finish_id", ctypes.c_int),
                ("engine_audio_id", ctypes.c_int),
                ("trails_id", ctypes.c_int),
                ("goal_explosion_id", ctypes.c_int),
                ("car_paint_id", ctypes.c_int),
                ("decal_paint_id", ctypes.c_int),
                ("wheels_paint_id", ctypes.c_int),
                ("boost_paint_id", ctypes.c_int),
                ("antenna_paint_id", ctypes.c_int),
                ("hat_paint_id", ctypes.c_int),
                ("trails_paint_id", ctypes.c_int),
                ("goal_explosion_paint_id", ctypes.c_int),
                ("use_rgb_lookup", ctypes.c_bool),
                ("primary_color_lookup", Color),
                ("secondary_color_lookup", Color),
                ("spawn_id", ctypes.c_int)]


class MutatorSettings(ctypes.Structure):
    _fields_ = [("match_length", ctypes.c_uint),
                ("max_score", ctypes.c_uint),
                ("overtime_option", ctypes.c_uint),
                ("series_length_option", ctypes.c_uint),
                ("game_speed_option", ctypes.c_uint),
                ("ball_max_speed_option", ctypes.c_uint),
                ("ball_type_option", ctypes.c_uint),
                ("ball_weight_option", ctypes.c_uint),
                ("ball_size_option", ctypes.c_uint),
                ("ball_bounciness_option", ctypes.c_uint),
                ("boost_amount_option", ctypes.c_uint),
                ("rumble_option", ctypes.c_uint),
                ("boost_strength_option", ctypes.c_uint),
                ("gravity_option", ctypes.c_uint),
                ("demolish_option", ctypes.c_uint),
                ("respawn_time_option", ctypes.c_uint),
                ]


class MatchSettings(ctypes.Structure):
    _fields_ = [("player_configuration", get_player_configuration_list_type()),
                ("num_players", ctypes.c_int),
                ("game_mode", ctypes.c_uint),
                ("game_map", ctypes.c_uint),
                ("skip_replays", ctypes.c_bool),
                ("instant_start", ctypes.c_bool),
                ("mutator_settings", MutatorSettings),
                ("existing_match_behavior", ctypes.c_uint),
                ("enable_lockstep", ctypes.c_bool),
                ]
