import time

from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.logging_utils import get_logger

MUTATOR_CONFIGURATION_HEADER = "Mutator Configuration"
MUTATOR_MATCH_LENGTH = "Match Length"
MUTATOR_MAX_SCORE = "Max Score"
MUTATOR_OVERTIME = "Overtime"
MUTATOR_SERIES_LENGTH = "Series Length"
MUTATOR_GAME_SPEED = "Game Speed"
MUTATOR_BALL_MAX_SPEED = "Ball Max Speed"
MUTATOR_BALL_TYPE = "Ball Type"
MUTATOR_BALL_WEIGHT = "Ball Weight"
MUTATOR_BALL_SIZE = "Ball Size"
MUTATOR_BALL_BOUNCINESS = "Ball Bounciness"
MUTATOR_BOOST_AMOUNT = "Boost Amount"
MUTATOR_RUMBLE = "Rumble"
MUTATOR_BOOST_STRENGTH = "Boost Strength"
MUTATOR_GRAVITY = "Gravity"
MUTATOR_DEMOLISH = "Demolish"
MUTATOR_RESPAWN_TIME = "Respawn Time"

MATCH_CONFIGURATION_HEADER = 'Match Configuration'
PARTICIPANT_COUNT_KEY = 'num_participants'
GAME_MODE = 'game_mode'
GAME_MAP = 'game_map'
SKIP_REPLAYS = 'skip_replays'
INSTANT_START = 'start_without_countdown'
EXISTING_MATCH_BEHAVIOR = 'existing_match_behavior'
ENABLE_LOCKSTEP = 'enable_lockstep'
ENABLE_RENDERING = 'enable_rendering'
ENABLE_STATE_SETTING = 'enable_state_setting'
AUTO_SAVE_REPLAY = 'auto_save_replay'

logger = get_logger('config_parser')

game_mode_types = [
    "Soccer",
    "Hoops",
    "Dropshot",
    "Hockey",
    "Rumble",
    "Heatseeker",
    "Gridiron",
]

# This dict needs to say in its current order, because it gets turned into a list
# and then used for index lookup in the GameMap enum in rlbot.fbs.
# If this becomes a superset of the GameMap enum, that's OK.
game_map_dict = {
    "DFHStadium": "Stadium_P",
    "Mannfield": "EuroStadium_P",
    "ChampionsField": "cs_p",
    "UrbanCentral": "TrainStation_P",
    "BeckwithPark": "Park_P",
    "UtopiaColiseum": "UtopiaStadium_P",
    "Wasteland": "wasteland_s_p",
    "NeoTokyo": "NeoTokyo_Standard_P",
    "AquaDome": "Underwater_P",
    "StarbaseArc": "arc_standard_p",
    "Farmstead": "farm_p",
    "SaltyShores": "beach_P",
    "DFHStadium_Stormy": "Stadium_Foggy_P",
    "DFHStadium_Day": "stadium_day_p",
    "Mannfield_Stormy": "EuroStadium_Rainy_P",
    "Mannfield_Night": "EuroStadium_Night_P",
    "ChampionsField_Day": "cs_day_p",
    "BeckwithPark_Stormy": "Park_Rainy_P",
    "BeckwithPark_Midnight": "Park_Night_P",
    "UrbanCentral_Night": "TrainStation_Night_P",
    "UrbanCentral_Dawn": "TrainStation_Dawn_P",
    "UtopiaColiseum_Dusk": "UtopiaStadium_Dusk_P",
    "DFHStadium_Snowy": "Stadium_Winter_P",
    "Mannfield_Snowy": "eurostadium_snownight_p",
    "UtopiaColiseum_Snowy": "UtopiaStadium_Snow_P",
    "Badlands": "Wasteland_P",
    "Badlands_Night": "Wasteland_Night_P",
    "TokyoUnderpass": "NeoTokyo_P",
    "Arctagon": "ARC_P",
    "Pillars": "Labs_CirclePillars_P",
    "Cosmic": "Labs_Cosmic_V4_P",
    "DoubleGoal": "Labs_DoubleGoal_V2_P",
    "Octagon": "Labs_Octagon_02_P",
    "Underpass": "Labs_Underpass_P",
    "UtopiaRetro": "Labs_Utopia_P",
    "Hoops_DunkHouse": "HoopsStadium_P",
    "DropShot_Core707": "ShatterShot_P",
    "ThrowbackStadium": "ThrowbackStadium_P",
    "ForbiddenTemple": "CHN_Stadium_P",
    "RivalsArena": "cs_hw_p",
    "Farmstead_Night": "Farm_Night_P",
    "SaltyShores_Night": "beach_night_p",
    "NeonFields": "music_p",
    "DFHStadium_Circuit": "Stadium_Race_Day_P",
    "DeadeyeCanyon": "Outlaw_P",
    "StarbaseArc_Aftermath": "ARC_Darc_P",
    "Wasteland_Night": "Wasteland_Night_S_P",
    'BeckwithPark_GothamNight': "Park_Bman_P",
    "ForbiddenTemple_Day": "CHN_Stadium_Day_P",
    "UrbanCentral_Haunted": "Haunted_TrainStation_P",
    "ChampionsField_NFL": "BB_P",
    "ThrowbackStadium_Snowy": "ThrowbackHockey_p",
    "Basin": "Labs_Basin_P",
    "Corridor": "Labs_Corridor_P",
    "Loophole": "Labs_Holyfield_P",
    "Galleon": "Labs_Galleon_P",
    "GalleonRetro": "Labs_Galleon_Mast_P",
    "Hourglass": "Labs_PillarGlass_P",
    "Barricade": "Labs_PillarHeat_P",
    "Colossus": "Labs_PillarWings_P",
    "BeckwithPark_Snowy": "Park_Snowy_P",
    "NeoTokyo_Comic": "NeoTokyo_Toon_P",
    "UtopiaColiseum_Gilded": "UtopiaStadium_Lux_P",
    "SovereignHeights": "Street_P",
    "Hoops_TheBlock": "HoopsStreet_P",
    "Farmstead_Spooky": "Farm_HW_P",
    "ChampionsField_NikeFC": "swoosh_p",
    "ForbiddenTemple_FireAndIce": "fni_stadium_p",
    "DeadeyeCanyon_Oasis": "outlaw_oasis_p",
    "EstadioVida_Dusk": "ff_dusk_p",
    "Mannfield_Dusk": "eurostadium_dusk_p",
    "Farmstead_Pitched": "farm_grs_p",
    "Farmstead_Upsidedown": "farm_hw_p",
    "Wasteland_Pitched": "wasteland_grs_p",
    "Neotokyo_Hacked": "neotokyo_hax_p",
}

map_types = list(game_map_dict.keys())

match_length_types = [
    "5 Minutes",
    "10 Minutes",
    "20 Minutes",
    "Unlimited"
]

max_score_types = [
    "Unlimited",
    "1 Goal",
    "3 Goals",
    "5 Goals",
]

overtime_mutator_types = [
    "Unlimited",
    "+5 Max, First Score",
    "+5 Max, Random Team"
]

series_length_mutator_types = [
    "Unlimited",
    "3 Games",
    "5 Games",
    "7 Games",
]

game_speed_mutator_types = [
    "Default",
    "Slo-Mo",
    "Time Warp"
]

ball_max_speed_mutator_types = [
    "Default",
    "Slow",
    "Fast",
    "Super Fast"
]

ball_type_mutator_types = [
    "Default",
    "Cube",
    "Puck",
    "Basketball"
]

ball_weight_mutator_types = [
    "Default",
    "Light",
    "Heavy",
    "Super Light"
]

ball_size_mutator_types = [
    "Default",
    "Small",
    "Large",
    "Gigantic"
]

ball_bounciness_mutator_types = [
    "Default",
    "Low",
    "High",
    "Super High"
]

boost_amount_mutator_types = [
    "Default",
    "Unlimited",
    "Recharge (Slow)",
    "Recharge (Fast)",
    "No Boost"
]

rumble_mutator_types = [
    "None",
    "Default",
    "Slow",
    "Civilized",
    "Destruction Derby",
    "Spring Loaded",
    "Spikes Only",
    "Spike Rush"
]

boost_strength_mutator_types = [
    "1x",
    "1.5x",
    "2x",
    "10x"
]

gravity_mutator_types = [
    "Default",
    "Low",
    "High",
    "Super High"
]

demolish_mutator_types = [
    "Default",
    "Disabled",
    "Friendly Fire",
    "On Contact",
    "On Contact (FF)"
]

respawn_time_mutator_types = [
    "3 Seconds",
    "2 Seconds",
    "1 Second",
    "Disable Goal Reset",
]

existing_match_behavior_types = [
    "Restart If Different",
    "Restart",
    "Continue And Spawn",
]


def add_match_settings_header(config_object):
    match_header = config_object.add_header_name(MATCH_CONFIGURATION_HEADER)
    match_header.add_value(PARTICIPANT_COUNT_KEY, int, default=0,
                           description='Number of bots/players which will be spawned.  We support up to max 64.')
    match_header.add_value(GAME_MODE, str, default="Soccer",
                           description="""What game mode the game should load.
                           Accepted values are "Soccer", "Hoops", "Dropshot", "Hockey", "Rumble", "Heatseeker", "Gridiron" """)
    match_header.add_value(GAME_MAP, str, default="DFHStadium",
                           description="""Which map the game should load into. Too many to list.""")
    match_header.add_value(SKIP_REPLAYS, bool, default=False,
                           description="""Automatically skip replays after a goal. Also stops match replays from being saved.""")
    match_header.add_value(INSTANT_START, bool, default=False,
                           description="""Skip the kickoff countdown""")
    match_header.add_value(EXISTING_MATCH_BEHAVIOR, str, default="Restart If Different",
                           description="""What should we do if you click run while a match is already in progress?""")
    match_header.add_value(ENABLE_LOCKSTEP, bool, default=False,
                           description="""If True, the framework will wait for outputs from all bots before advancing to the next frame.""")
    match_header.add_value(ENABLE_RENDERING, bool, default=True,
                           description="""If True, bots will be able to draw lines and text in the game.""")
    match_header.add_value(ENABLE_STATE_SETTING, bool, default=True,
                           description="""If True, bots will be able to teleport cars and the ball etc.""")
    match_header.add_value(AUTO_SAVE_REPLAY, bool, default=False,
                           description="""If True, you will be prompted to save a replay at the end of the match.""")


def add_mutator_header(config_object):
    mutator_header = config_object.add_header_name(MUTATOR_CONFIGURATION_HEADER)
    mutator_header.add_value(MUTATOR_MATCH_LENGTH, str, default="5 Minutes")
    mutator_header.add_value(MUTATOR_MAX_SCORE, str, default="Unlimited")
    mutator_header.add_value(MUTATOR_OVERTIME, str, default="Unlimited")
    mutator_header.add_value(MUTATOR_SERIES_LENGTH, str, default="Unlimited")
    mutator_header.add_value(MUTATOR_GAME_SPEED, str, default="Default")
    mutator_header.add_value(MUTATOR_BALL_MAX_SPEED, str, default="Default")
    mutator_header.add_value(MUTATOR_BALL_TYPE, str, default="Default")
    mutator_header.add_value(MUTATOR_BALL_WEIGHT, str, default="Default")
    mutator_header.add_value(MUTATOR_BALL_SIZE, str, default="Default")
    mutator_header.add_value(MUTATOR_BALL_BOUNCINESS, str, default="Default")
    mutator_header.add_value(MUTATOR_BOOST_AMOUNT, str, default="Default")
    mutator_header.add_value(MUTATOR_RUMBLE, str, default="None")
    mutator_header.add_value(MUTATOR_BOOST_STRENGTH, str, default="1x")
    mutator_header.add_value(MUTATOR_GRAVITY, str, default="Default")
    mutator_header.add_value(MUTATOR_DEMOLISH, str, default="Default")
    mutator_header.add_value(MUTATOR_RESPAWN_TIME, str, default="3 Seconds")


def get_num_players(config):
    """
    Returns the number of players specified by the config parser
    """
    return config.getint(MATCH_CONFIGURATION_HEADER, PARTICIPANT_COUNT_KEY)


def parse_mutator_settings(mutator_settings, config: ConfigObject):
    """
    Assigns the mutator settings to the settings object for the dll
    :param mutator_settings:
    :param config:
    """
    mutator_settings.match_length = safe_get_mutator(match_length_types, config, MUTATOR_MATCH_LENGTH)
    mutator_settings.max_score = safe_get_mutator(max_score_types, config, MUTATOR_MAX_SCORE, {'0': 'Unlimited'})
    mutator_settings.overtime = safe_get_mutator(overtime_mutator_types, config, MUTATOR_OVERTIME)
    mutator_settings.series_length = safe_get_mutator(series_length_mutator_types, config, MUTATOR_SERIES_LENGTH)
    mutator_settings.game_speed = safe_get_mutator(game_speed_mutator_types, config, MUTATOR_GAME_SPEED)
    mutator_settings.ball_max_speed = safe_get_mutator(
        ball_max_speed_mutator_types, config, MUTATOR_BALL_MAX_SPEED, {'0': 'Default'})
    mutator_settings.ball_type = safe_get_mutator(ball_type_mutator_types, config, MUTATOR_BALL_TYPE)
    mutator_settings.ball_weight = safe_get_mutator(ball_weight_mutator_types, config, MUTATOR_BALL_WEIGHT)
    mutator_settings.ball_size = safe_get_mutator(
        ball_size_mutator_types, config, MUTATOR_BALL_SIZE, {'1.0': 'Default'})
    mutator_settings.ball_bounciness = safe_get_mutator(
        ball_bounciness_mutator_types, config, MUTATOR_BALL_BOUNCINESS, {'1.0': 'Default'})
    mutator_settings.boost_amount = safe_get_mutator(boost_amount_mutator_types, config, MUTATOR_BOOST_AMOUNT)
    mutator_settings.rumble = safe_get_mutator(rumble_mutator_types, config, MUTATOR_RUMBLE)
    mutator_settings.boost_strength = safe_get_mutator(
        boost_strength_mutator_types, config, MUTATOR_BOOST_STRENGTH, {'Default': '1x', '1.0': '1x'})
    mutator_settings.gravity = safe_get_mutator(gravity_mutator_types, config, MUTATOR_GRAVITY)
    mutator_settings.demolish = safe_get_mutator(demolish_mutator_types, config, MUTATOR_DEMOLISH)
    mutator_settings.respawn_time = safe_get_mutator(respawn_time_mutator_types, config, MUTATOR_RESPAWN_TIME, {
                                                            '3.0': '3 Seconds', '3': '3 Seconds'})


def safe_get_mutator(mutator_options, config, mutator_name, replacement_table={}):

    value = config.get(MUTATOR_CONFIGURATION_HEADER, mutator_name)

    if value in replacement_table:
        logger.warn('**************************************')
        logger.warn(f'The value you\'ve set for {mutator_name} ({value}) is deprecated and will need to be changed to '
                    f'"{replacement_table[value]}" for the next version. Please check your rlbot.cfg!')
        logger.warn('**************************************')
        time.sleep(2.0)
        value = replacement_table[value]

    if value in mutator_options:
        return value
    else:
        logger.warn('**************************************')
        logger.warn(f'The value you\'ve set for {mutator_name} ({value}) is invalid, and will be ignored. '
                    'Please check your rlbot.cfg!')
        logger.warn('**************************************')
        time.sleep(2.0)
        return mutator_options[0]


def parse_match_settings(match_settings, config: ConfigObject):
    """
    Parses the matching settings modifying the match settings object.
    :param match_settings:
    :param config:
    :return:
    """

    match_settings.game_mode = config.get(MATCH_CONFIGURATION_HEADER, GAME_MODE)
    match_settings.game_map = config.get(MATCH_CONFIGURATION_HEADER, GAME_MAP)
    match_settings.skip_replays = config.getboolean(MATCH_CONFIGURATION_HEADER, SKIP_REPLAYS)
    match_settings.instant_start = config.getboolean(MATCH_CONFIGURATION_HEADER, INSTANT_START)
    match_settings.existing_match_behavior = config.get(MATCH_CONFIGURATION_HEADER, EXISTING_MATCH_BEHAVIOR)
    match_settings.enable_lockstep = config.getboolean(MATCH_CONFIGURATION_HEADER, ENABLE_LOCKSTEP)
    match_settings.enable_rendering = config.getboolean(MATCH_CONFIGURATION_HEADER, ENABLE_RENDERING)
    match_settings.enable_state_setting = config.getboolean(MATCH_CONFIGURATION_HEADER, ENABLE_STATE_SETTING)
    match_settings.auto_save_replay = config.getboolean(MATCH_CONFIGURATION_HEADER, AUTO_SAVE_REPLAY)

    parse_mutator_settings(match_settings.mutators, config)
