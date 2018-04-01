

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

def add_mutator_header(config_object):
    mutator_header = config_object.add_header_name(MUTATOR_CONFIGURATION_HEADER)
    mutator_header.add_value(MUTATOR_MATCH_LENGTH, int, default=5,
                             description="Changes the length of the match, 0 for unlimited")
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
                             description="Changes the amount of boost \n (use 'Default', 'Unlimited', "
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
