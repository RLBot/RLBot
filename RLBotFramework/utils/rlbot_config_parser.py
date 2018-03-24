import configparser
import logging
import os

import sys

from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_LOADOUT_HEADER, BOT_CONFIG_LOADOUT_ORANGE_HEADER, \
    BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY
from RLBotFramework.utils.class_importer import import_agent
from RLBotFramework.utils.custom_config import ConfigObject
from RLBotFramework.utils.structures.bot_input_struct import get_player_configuration_list

PARTICIPANT_CONFIGURATION_HEADER = 'Participant Configuration'
PARTICIPANT_TYPE_KEY = 'participant_type'
PARTICIPANT_CONFIG_KEY = 'participant_config'
PARTICIPANT_BOT_SKILL_KEY = 'participant_bot_skill'
PARTICIPANT_TEAM = 'participant_team'
RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'

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

TEAM_CONFIGURATION_HEADER = "Team Configuration"

PARTICIPANT_COUNT_KEY = 'num_participants'
EXTENSION_PATH_KEY = 'extension_path'

logger = logging.getLogger('rlbot')


# Cut off at 31 characters and handle duplicates
def get_sanitized_bot_name(dict, name):
    if name not in dict:
        new_name = name[:31]  # Make sure name does not exceed 31 characters
        dict[name] = 1
    else:
        count = dict[name]
        new_name = name[:27] + "(" + str(count + 1) + ")"  # Truncate at 27 because we can have up to '(10)' appended
        dict[name] = count + 1

    return new_name


def get_bot_config_file_list(botCount, config, bot_configs):
    """
    Adds all the config files or config objects.
    :param botCount:
    :param config:
    :param bot_configs: These are configs that have been loaded from the gui, they get assigned a bot index.
    :return:
    """
    config_file_list = []
    for i in range(botCount):
        if i in bot_configs:
            config_file_list.append(bot_configs[i])
            logger.debug("Config available")
        else:
            bot_config_path = config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, i)
            raw_bot_config = configparser.RawConfigParser()
            raw_bot_config.read(bot_config_path)
            config_file_list.append(raw_bot_config)
            logger.debug("Reading raw config")

    return config_file_list


def create_bot_config_layout():
    config_object = ConfigObject()
    rlbot_header = config_object.add_header_name(RLBOT_CONFIGURATION_HEADER)
    rlbot_header.add_value('num_participants', int, default=2,
                           description='Number of bots/players which will be spawned.  We support up to max 10.')
    rlbot_header.add_value(EXTENSION_PATH_KEY, str, default=None,
                           description='A path to the extension file we want to load')

    participant_header = config_object.add_header_name(PARTICIPANT_CONFIGURATION_HEADER, is_indexed=True)
    participant_header.add_value(PARTICIPANT_CONFIG_KEY, str, default='./agents/atba/atba.cfg',
                                 description="""The location of the configuration file for your agent here.
                                             Only total_num_participants config files will be read!
                                             Everything needs a config, even players and default bots.
                                             We still set loadouts and names from config!""")

    participant_header.add_value(PARTICIPANT_TEAM, int, default=0,
                                 description="Which team the player should be on:" +
                                             "\nteam 0 (blue) shoots on positive goal, " +
                                             "team 1 (orange) shoots on negative goal")

    participant_header.add_value(PARTICIPANT_TYPE_KEY, str, default='rlbot',
                                 description='Accepted values are "human", "rlbot", "psyonix", and "possessed_human"\n' +
                                             'You can have up to 4 local players and they must ' +
                                             'be activated in game or it will crash.\n' +
                                             'If no player is specified you will be spawned in as spectator!\n' +
                                             'human - not controlled by the framework\n' +
                                             'rlbot - controlled by the framework\n' +
                                             'psyonix - default bots (skill level can be changed with participant_bot_skill\n' +
                                             'possessed_human - controlled by the framework but the game detects it as a human')

    participant_header.add_value(PARTICIPANT_BOT_SKILL_KEY, float, default=1.0,
                                 description='If participant is a bot and not RLBot controlled,' +
                                             ' this value will be used to set bot skill.\n' +
                                             '0.0 is Rookie, 0.5 is pro, 1.0 is all-star. ' +
                                             ' You can set values in-between as well.')

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

    team_header = config_object.add_header_name(TEAM_CONFIGURATION_HEADER)
    team_header.add_value("Team Blue Color", int, default=0,
                          description="Changes Blue team color, use 0 to use default color")
    team_header.add_value("Team Blue Name", str, default="Blue",
                          description="Changes the Team name to use instead of 'Blue'")
    team_header.add_value("Team Orange Color", int, default=0,
                          description="Changes Blue team color, use 0 to use default color")
    team_header.add_value("Team Orange Name", str, default="Blue",
                          description="Changes the Team name to use instead of 'Orange'")
    return config_object


def get_team(config, index):
    """
    Returns which team the bot is on (represented by an integer)
    """
    return config.getint(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, index)


def get_num_players(config):
    """
    Returns the number of players specified by the config parser
    """
    return config.getint(RLBOT_CONFIGURATION_HEADER, PARTICIPANT_COUNT_KEY)


def parse_configurations(gameInputPacket, config_parser, bot_configs, looks_configs):
    bot_names = []
    bot_teams = []
    bot_modules = []

    # Determine number of participants
    num_participants = get_num_players(config_parser)

    # Retrieve bot config files
    participant_configs = get_bot_config_file_list(num_participants, config_parser, bot_configs)

    # Create empty lists

    bot_parameter_list = []
    name_dict = {}

    gameInputPacket.iNumPlayers = num_participants

    player_configuration_list = get_player_configuration_list(gameInputPacket)

    # Set configuration values for bots and store name and team
    for i in range(num_participants):
        if i not in looks_configs:
            looks_config_object = configparser.RawConfigParser()
            looks_config_object_path = participant_configs[i].get("Locations", "looks_config")
            looks_config_object.read(looks_config_object_path)
        else:
            looks_config_object = looks_configs[i]

        bot_name, team_number, bot_module, bot_parameters = load_bot_config(i, player_configuration_list[i],
                                                                            participant_configs[i], looks_config_object,
                                                                            config_parser, name_dict)

        bot_names.append(bot_name)
        bot_teams.append(team_number)
        bot_modules.append(bot_module)
        bot_parameter_list.append(bot_parameters)

    return num_participants, bot_names, bot_teams, bot_modules, bot_parameter_list


def load_bot_config(index, bot_configuration, bot_config_object, looks_config_object, overall_config, name_dict):
    """
    Loads the config data of a single bot
    :param index: This is the bot index (where it appears in game_cars)
    :param bot_configuration: This is the game_tick_packet configuration that is sent back to the game
    :param bot_config_object: A config object for a single bot
    :param overall_config: This is the config for the entire session not one particular bot
    :param name_dict: A mapping of used names so we can make sure to not reuse bot names.
    :return:
    """
    team_num = get_team(overall_config, index)

    bot_configuration.ucTeam = team_num

    # Setting up data about what type of bot it is
    bot_type = overall_config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TYPE_KEY, index)

    if bot_type == 'human':
        is_bot = False
        is_rlbot = False
    elif bot_type == 'rlbot':
        is_bot = True
        is_rlbot = True
    elif bot_type == 'psyonix':
        is_bot = True
        is_rlbot = False
    elif bot_type == 'possessed_human':
        is_bot = False
        is_rlbot = True
    else:
        raise ValueError('participant_type value is not "human", "rlbot", "psyonix", or "possessed_human"')

    bot_configuration.bBot = is_bot
    bot_configuration.bRLBotControlled = is_rlbot
    bot_configuration.fBotSkill = overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY, index)

    if not bot_configuration.bBot:
        bot_configuration.iHumanIndex = index

    loadout_header = BOT_CONFIG_LOADOUT_HEADER
    if team_num == 1 and looks_config_object.has_section(BOT_CONFIG_LOADOUT_ORANGE_HEADER):
        loadout_header = BOT_CONFIG_LOADOUT_ORANGE_HEADER

    # Setting up the bots name
    bot_name = looks_config_object.get(loadout_header, 'name')
    bot_configuration.wName = get_sanitized_bot_name(name_dict, bot_name)

    BaseAgent.parse_bot_loadout(bot_configuration, looks_config_object, loadout_header)

    bot_module = 'NO_MODULE_FOR_PARTICIPANT'
    bot_parameters = None

    if bot_configuration.bRLBotControlled:
        bot_module = bot_config_object.get(BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY)
        agent = import_agent(bot_module)
        dirpath = os.path.dirname(os.path.realpath(sys.modules[agent.__module__].__file__))
        if dirpath not in sys.path:
            sys.path.append(dirpath)
        bot_parameters = agent.create_agent_configurations()
        bot_parameters.parse_file(bot_config_object)

    return bot_name, team_num, bot_module, bot_parameters
