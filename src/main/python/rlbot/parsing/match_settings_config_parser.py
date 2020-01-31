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

logger = get_logger('config_parser')

game_mode_types = [
    "Soccer",
    "Hoops",
    "Dropshot",
    "Hockey",
    "Rumble",
]

map_types = [
    "DFHStadium",
    "Mannfield",
    "ChampionsField",
    "UrbanCentral",
    "BeckwithPark",
    "UtopiaColiseum",
    "Wasteland",
    "NeoTokyo",
    "AquaDome",
    "StarbaseArc",
    "Farmstead",
    "SaltyShores",
    "DFHStadium_Stormy",
    "DFHStadium_Day",
    "Mannfield_Stormy",
    "Mannfield_Night",
    "ChampionsField_Day",
    "BeckwithPark_Stormy",
    "BeckwithPark_Midnight",
    "UrbanCentral_Night",
    "UrbanCentral_Dawn",
    "UtopiaColiseum_Dusk",
    "DFHStadium_Snowy",
    "Mannfield_Snowy",
    "UtopiaColiseum_Snowy",
    "Badlands",
    "Badlands_Night",
    "TokyoUnderpass",
    "Arctagon",
    "Pillars",
    "Cosmic",
    "DoubleGoal",
    "Octagon",
    "Underpass",
    "UtopiaRetro",
    "Hoops_DunkHouse",
    "DropShot_Core707",
    "ThrowbackStadium",
    "ForbiddenTemple",
    "RivalsArena",
    "Farmstead_Night",
    "SaltyShores_Night"
]

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
                           Accepted values are "Soccer", "Hoops", "Dropshot", "Hockey", "Rumble" """)
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

    parse_mutator_settings(match_settings.mutators, config)
