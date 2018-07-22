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

# Some of these are dictionaries instead of lists because we need to map multiple possible config values to the same
# number. This is to provide backwards compatibility for some old values that have been in rlbot.cfg for a long time.
# Anything that is a list instead of a map was either never in the old rlbot.cfg, or had an identical default value,
# so the mapping is not required.

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
    "ThrowbackStadium"
]

match_length_types = [
    "5 Minutes",
    "10 Minutes",
    "20 Minutes",
    "Unlimited"
]

max_score_types = {
    "0": 0,  # For backwards compatibility
    "Unlimited": 0,
    "1 Goal": 1,
    "3 Goals": 2,
    "5 Goals": 3
}

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

ball_max_speed_mutator_types = {
    "0": 0,  # For backwards compatibility
    "Default": 0,
    "Slow": 1,
    "Fast": 2,
    "Super Fast": 3
}

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

ball_size_mutator_types = {
    "1.0": 0,  # For backwards compatibility
    "Default": 0,
    "Small": 1,
    "Large": 2,
    "Gigantic": 3
}

ball_bounciness_mutator_types = {
    "1.0": 0,  # For backwards compatibility
    "Default": 0,
    "Low": 1,
    "High": 2,
    "Super High": 3
}

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
    "Spikes Only"
]

boost_strength_mutator_types = {
    "Default": 0,  # For backwards compatibility
    "1x": 0,
    "1.5x": 1,
    "2x": 2,
    "10x": 3
}

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

respawn_time_mutator_types = {
    "3.0": 0,  # For backwards compatibility
    "3 Seconds": 0,
    "2 Seconds": 1,
    "1 Second": 2,
    "Disable Goal Reset": 3
}



def add_match_settings_header(config_object):
    match_header = config_object.add_header_name(MATCH_CONFIGURATION_HEADER)
    match_header.add_value(PARTICIPANT_COUNT_KEY, int, default=2,
                           description='Number of bots/players which will be spawned.  We support up to max 10.')
    match_header.add_value(GAME_MODE, str, default="Soccer",
                           description="""What game mode the game should load.
                           Accepted values are "Soccer", "Hoops", "Dropshot", "Hockey", "Rumble" """)
    match_header.add_value(GAME_MAP, str, default="DFHStadium",
                           description="""What game mode the game should load into. Too many to list.""")
    match_header.add_value(SKIP_REPLAYS, bool, default=False,
                           description="""Automatically skip replays after a goal.""")
    match_header.add_value(INSTANT_START, bool, default=False,
                           description="""Skip the kickoff countdown""")


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


def parse_mutator_settings(mutator_settings, config):
    """
    Assigns the mutator settings to the settings object for the dll
    :param mutator_settings:
    :param config:
    """
    mutator_settings.match_length = match_length_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_MATCH_LENGTH))
    mutator_settings.max_score = max_score_types[config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_MAX_SCORE)]
    mutator_settings.overtime_option = overtime_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_OVERTIME))
    mutator_settings.series_length_option = series_length_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_SERIES_LENGTH))
    mutator_settings.game_speed_option = game_speed_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_GAME_SPEED))
    mutator_settings.ball_max_speed_option = ball_max_speed_mutator_types[config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BALL_MAX_SPEED)]
    mutator_settings.ball_type_option = ball_type_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BALL_TYPE))
    mutator_settings.ball_weight_option = ball_weight_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BALL_WEIGHT))
    mutator_settings.ball_size_option = ball_size_mutator_types[config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BALL_SIZE)]
    mutator_settings.ball_bounciness_option = ball_bounciness_mutator_types[config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BALL_BOUNCINESS)]
    mutator_settings.boost_amount_option = boost_amount_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BOOST_AMOUNT))
    mutator_settings.rumble_option = rumble_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_RUMBLE))
    mutator_settings.boost_strength_option = boost_strength_mutator_types[config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BOOST_STRENGTH)]
    mutator_settings.gravity_option = gravity_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_GRAVITY))
    mutator_settings.demolish_option = demolish_mutator_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_DEMOLISH))
    mutator_settings.respawn_time_option = respawn_time_mutator_types[config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_RESPAWN_TIME)]


def parse_match_settings(match_settings, config):
    """
    Parses the matching settings modifying the match settings object.
    :param match_settings:
    :param config:
    :return:
    """

    match_settings.game_mode = game_mode_types.index(config.get(MATCH_CONFIGURATION_HEADER, GAME_MODE))
    match_settings.game_map = map_types.index(config.get(MATCH_CONFIGURATION_HEADER, GAME_MAP))
    match_settings.skip_replays = config.getboolean(MATCH_CONFIGURATION_HEADER, SKIP_REPLAYS)
    match_settings.instant_start = config.getboolean(MATCH_CONFIGURATION_HEADER, INSTANT_START)

    parse_mutator_settings(match_settings.mutator_settings, config)
