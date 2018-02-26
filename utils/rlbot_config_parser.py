import configparser
import os

import sys

from agents.base_agent import BaseAgent, BOT_CONFIG_LOADOUT_HEADER, BOT_CONFIG_LOADOUT_ORANGE_HEADER, \
    BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY
from utils.agent_creator import import_agent
from utils.custom_config import ConfigObject

PARTICIPANT_CONFIGURATION_HEADER = 'Participant Configuration'
PARTICIPANT_BOT_KEY = 'participant_is_bot'
PARTICIPANT_RLBOT_KEY = 'participant_is_rlbot_controlled'
PARTICIPANT_CONFIG_KEY = 'participant_config'
PARTICIPANT_BOT_SKILL_KEY = 'participant_bot_skill'
PARTICIPANT_TEAM = 'participant_team'
RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
PARTICIPANT_COUNT_KEY = 'num_participants'


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
        else:
            bot_config = config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, i)
            bot_config_path = bot_config
            sys.path.append(os.path.dirname(bot_config_path))
            raw_bot_config = configparser.RawConfigParser()
            raw_bot_config.read(bot_config_path)
            config_file_list.append(raw_bot_config)

    return config_file_list


def create_bot_config_layout():
    config_object = ConfigObject()
    rlbot_header = config_object.add_header_name(RLBOT_CONFIGURATION_HEADER)
    rlbot_header.add_value('num_participants', int, default=2, description='The number of players on the field')

    participant_header = config_object.add_header_name(PARTICIPANT_CONFIGURATION_HEADER, is_indexed=True)
    participant_header.add_value(PARTICIPANT_TEAM, int, default=0,
                                 description="Which team the player should be on:" +
                                             "\nteam 0 (blue) shoots on positive goal, " +
                                             "team 1 (orange) shoots on negative goal")

    participant_header.add_value(PARTICIPANT_CONFIG_KEY, str, default='./agents/atba/atba.cfg',
                                 description="The location of the configuration file for a specific agent")

    participant_header.add_value(PARTICIPANT_BOT_KEY, bool, default='yes',
                                 description='Accepted values are "1", "yes", "true", and "on", for True,' +
                                             ' and "0", "no", "false", and "off", for False\n' +
                                             'You can have up to 4 local players and they must ' +
                                             'be activated in game or it will crash.\n' +
                                             'If no player is specified you will be spawned in as spectator!')

    participant_header.add_value(PARTICIPANT_RLBOT_KEY, bool, default='yes',
                                 description='Accepted values are "1", "yes", "true", and "on", for True,' +
                                             ' and "0", "no", "false", and "off", for False\n' +
                                             'By specifying \'no\' here you can use default bots ' +
                                             'like the rookie, all-star, etc.')

    participant_header.add_value(PARTICIPANT_BOT_SKILL_KEY, float, default=1.0,
                                 description='If participant is a bot and not RLBot controlled,' +
                                             ' this value will be used to set bot skill.\n' +
                                             '0.0 is Rookie, 0.5 is pro, 1.0 is all-star. ' +
                                             ' You can set values in-between as well.')
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


def parse_configurations(gameInputPacket, config_parser, bot_configs):
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

    bot_config_object = BaseAgent.create_agent_configurations()

    # Set configuration values for bots and store name and team
    for i in range(num_participants):
        bot_config_object.reset()
        bot_config_object.parse_file(participant_configs[i])

        bot_name, team_number, bot_module, bot_parameters = load_bot_config(i, gameInputPacket.sPlayerConfiguration[i],
                                                                            bot_config_object, config_parser, name_dict)

        bot_names.append(bot_name)
        bot_teams.append(team_number)
        bot_modules.append(bot_module)
        bot_parameter_list.append(bot_parameters)

    return num_participants, bot_names, bot_teams, bot_modules, bot_parameter_list


def load_bot_config(index, bot_configuration, bot_config_object, overall_config, name_dict):
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
    bot_configuration.bBot = overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_KEY, index)
    bot_configuration.bRLBotControlled = overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_RLBOT_KEY, index)
    bot_configuration.fBotSkill = overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY, index)
    bot_configuration.iPlayerIndex = index

    loadout_header = BOT_CONFIG_LOADOUT_HEADER
    if team_num == 1 and bot_config_object.has_section(BOT_CONFIG_LOADOUT_ORANGE_HEADER):
        loadout_header = BOT_CONFIG_LOADOUT_ORANGE_HEADER

    # Setting up the bots name
    bot_name = bot_config_object.get(loadout_header, 'name')
    bot_configuration.wName = get_sanitized_bot_name(name_dict, bot_name)

    BaseAgent.parse_bot_loadout(bot_configuration, bot_config_object, loadout_header)

    bot_module = 'NO_MODULE_FOR_PARTICIPANT'
    bot_parameters = None

    if bot_configuration.bRLBotControlled:
        bot_module = bot_config_object.get(BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY)
        agent = import_agent(bot_module)
        bot_parameters = agent.create_agent_configurations()
        bot_parameters.parse_file(bot_config_object.get_raw_file())

    return bot_name, team_num, bot_module, bot_parameters
