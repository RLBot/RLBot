

MUTATOR_CONFIGURATION_HEADER = "Mutator Configuration"
MUTATOR_MATCH_LENGTH = "Match Length"
MUTATOR_MAX_SCORE = "Max Score"
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
    "DropShot_Core707"
]

match_length_types = [
    "5 Minutes",
    "10 Minutes",
    "20 Minutes",
    "Unlimited"
]

boost_types = [
    "Default",
    "Unlimited",
    "Recharge (Slow)",
    "Recharge (Fast)",
    "No Boost"
]


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
    mutator_header.add_value(MUTATOR_MATCH_LENGTH, str, default="Unlimited",
                             description="Changes the length of the match, 3 for unlimited")
    mutator_header.add_value(MUTATOR_MAX_SCORE, int, default=0,
                             description="Changes the number of goals needed to win, 0 for unlimited")
    mutator_header.add_value(MUTATOR_GAME_SPEED, str, default="Default",
                             description="'Default', 'Slo-Mo' or 'Time Warp'\n"
                                         "    Slo-Mo slows the game down\n"
                                         "    Time Warp only slows the game down when a player touches the ball")
    mutator_header.add_value(MUTATOR_BALL_MAX_SPEED, int, default=0,  # TODO find real default max
                             description="Sets max speed of the ball in km/h, 0 for unlimited.")
    mutator_header.add_value(MUTATOR_BALL_TYPE, str, default="Default",
                             description="Changes the type of the ball (use 'Default', 'Cube', 'Puck' or 'Basketball')")
    mutator_header.add_value(MUTATOR_BALL_WEIGHT, str, default="Default",
                             description="Changes the weight of the ball (use 'Default', 'Super Light', "
                                         "'Light' or 'Heavy')")
    mutator_header.add_value(MUTATOR_BALL_SIZE, float, default=1.0,  # TODO find real default size
                             description="Changes the size of the ball")
    mutator_header.add_value(MUTATOR_BALL_BOUNCINESS, float, default=1.0,  # TODO find real default
                             description="Changes the bounciness of the ball")
    mutator_header.add_value(MUTATOR_BOOST_AMOUNT, str, default="Default",
                             description="Changes the amount of boost\n (use 'Default', 'Unlimited', "
                                         "'Recharge (Slow)', 'Recharge (Fast)' or 'No Boost')")
    mutator_header.add_value(MUTATOR_RUMBLE, str, default="None",
                             description="Changes rumble type\n(use 'None', 'Default', "
                                         "'Slow', 'Civilized', 'Desctuction Derby' or 'Spring Loaded'")
    mutator_header.add_value(MUTATOR_BOOST_STRENGTH, float, default=1.0,
                             description="Amount to multiply default boost strength with")
    mutator_header.add_value(MUTATOR_GRAVITY, str, default="Default",
                             description="Changes gravity for both cars and ball\n"
                                         "(use 'Default', 'Low', 'High' or 'Super High'")
    mutator_header.add_value(MUTATOR_DEMOLISH, str, default="Default",
                             description="Changes demolishment sensitivity\n(use 'Default', 'Disabled', "
                                         "'Friendly Fire', 'On Contact' or 'On Contact (FF)'")
    mutator_header.add_value(MUTATOR_RESPAWN_TIME, float, default=3,
                             description="Time in seconds taken to respawn for demolished players\n"
                                         "use -1 to set Disable Goal Reset")


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

    mutator_settings.boost_options = boost_types.index(config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BOOST_AMOUNT))


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