import configparser

import os

from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_LOADOUT_HEADER, BOT_CONFIG_LOADOUT_ORANGE_HEADER, \
    BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, LOOKS_CONFIG_KEY
from RLBotFramework.utils.class_importer import import_agent
from RLBotFramework.utils.logging_utils import get_logger

PARTICIPANT_CONFIGURATION_HEADER = 'Participant Configuration'
PARTICIPANT_CONFIG_KEY = 'participant_config'
PARTICIPANT_BOT_SKILL_KEY = 'participant_bot_skill'
PARTICIPANT_TYPE_KEY = 'participant_type'
PARTICIPANT_TEAM = 'participant_team'

logger = get_logger('rlbot')


class BotConfigBundle:
    def __init__(self, config_directory, config_obj):
        self.config_directory = config_directory
        self.config_obj = config_obj
        self.base_agent_config = BaseAgent.create_agent_configurations()
        self.base_agent_config.parse_file(self.config_obj)

    def get_absolute_path(self, header, key):
        joined = os.path.join(self.config_directory, self.base_agent_config.get(header, key))
        return os.path.realpath(joined)


def add_participant_header(config_object):
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
                                 description="""Accepted values are "human", "rlbot", "psyonix", "party_member_bot", and "controller_passthrough"
                                             You can have up to 4 local players and they must 
                                             be activated in game or it will crash.
                                             If no player is specified you will be spawned in as spectator!
                                             human - not controlled by the framework
                                             rlbot - controlled by the framework
                                             psyonix - default bots (skill level can be changed with participant_bot_skill
                                             party_member_bot - controlled by an rlbot but the game detects it as a human
                                             controller_passthrough - controlled by a human but runs through the framework""")

    participant_header.add_value(PARTICIPANT_BOT_SKILL_KEY, float, default=1.0,
                                 description='If participant is a bot and not RLBot controlled,' +
                                             ' this value will be used to set bot skill.\n' +
                                             '0.0 is Rookie, 0.5 is pro, 1.0 is all-star. ' +
                                             ' You can set values in-between as well.')


def get_looks_config(config_bundle):
    """
    Creates a looks config from the config bundle
    :param config_bundle:
    :return:
    """
    looks_path = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
    return BaseAgent.create_looks_configurations().parse_file(looks_path)


def get_sanitized_bot_name(dict, name):
    """
    Cut off at 31 characters and handle duplicates.
    :param dict: Holds the list of names for duplicates
    :param name: The name that is being sanitized
    :return: A sanitized version of the name
    """
    if name not in dict:
        new_name = name[:31]  # Make sure name does not exceed 31 characters
        dict[name] = 1
    else:
        count = dict[name]
        new_name = name[:27] + "(" + str(count + 1) + ")"  # Truncate at 27 because we can have up to '(10)' appended
        dict[name] = count + 1

    return new_name


def get_team(config, index):
    """
    Returns which team the bot is on (represented by an integer)
    """
    return config.getint(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, index)


def get_bot_config_bundle(bot_config_path):
    raw_bot_config = configparser.RawConfigParser()
    raw_bot_config.read(bot_config_path)
    config_directory = os.path.dirname(os.path.realpath(bot_config_path))
    return BotConfigBundle(config_directory, raw_bot_config)


def get_bot_config_bundles(num_participants, config, config_location, config_bundle_overrides):
    """
    Adds all the config files or config objects.
    :param num_participants:
    :param config:
    :param config_location: The location of the rlbot.cfg file
    :param config_bundle_overrides: These are configs that have been loaded from the gui, they get assigned a bot index.
    :return:
    """
    config_bundles = []
    for i in range(num_participants):
        if i in config_bundle_overrides:
            config_bundles.append(config_bundle_overrides[i])
            logger.debug("Config available")
        else:
            bot_config_relative_path = config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, i)
            bot_config_path = os.path.join(os.path.dirname(config_location), bot_config_relative_path)
            config_bundles.append(get_bot_config_bundle(bot_config_path))
            logger.debug("Reading raw config")

    return config_bundles


def get_bot_options(bot_type):
    if bot_type == 'human':
        is_bot = False
        is_rlbot = False
    elif bot_type == 'rlbot':
        is_bot = True
        is_rlbot = True
    elif bot_type == 'psyonix':
        is_bot = True
        is_rlbot = False
    elif bot_type == 'controller_passthrough':
        # this is an rlbot but a very specific rlbot
        is_bot = True
        is_rlbot = True
    elif bot_type == 'party_member_bot':
        # this is a bot running under a human

        is_rlbot = True
        is_bot = False
    else:
        raise ValueError('participant_type value is not "human", "rlbot", "psyonix", ' +
                         '"party_member_bot", or "controller_passthrough"')

    return is_bot, is_rlbot


def load_bot_config(index, bot_configuration, config_bundle: BotConfigBundle, looks_config_object, overall_config, name_dict):
    """
    Loads the config data of a single bot
    :param index: This is the bot index (where it appears in game_cars)
    :param bot_configuration: This is the game_tick_packet configuration that is sent back to the game
    :param config_bundle: A config object for a single bot
    :param overall_config: This is the config for the entire session not one particular bot
    :param name_dict: A mapping of used names so we can make sure to not reuse bot names.
    :return:
    """
    team_num = get_team(overall_config, index)

    bot_configuration.team = team_num

    # Setting up data about what type of bot it is
    bot_type = overall_config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TYPE_KEY, index)
    bot_configuration.bot, bot_configuration.rlbot_controlled = get_bot_options(bot_type)
    bot_configuration.bot_skill = overall_config.getfloat(
        PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY, index)

    if not bot_configuration.bot:
        bot_configuration.human_index = index

    loadout_header = BOT_CONFIG_LOADOUT_HEADER
    if team_num == 1 and looks_config_object.has_section(BOT_CONFIG_LOADOUT_ORANGE_HEADER):
        loadout_header = BOT_CONFIG_LOADOUT_ORANGE_HEADER

    # Setting up the bots name
    bot_name = looks_config_object.get(loadout_header, 'name')
    bot_configuration.name = get_sanitized_bot_name(name_dict, bot_name)

    BaseAgent.parse_bot_loadout(bot_configuration, looks_config_object, loadout_header)

    python_file = 'NO_MODULE_FOR_PARTICIPANT'
    bot_parameters = None

    if bot_configuration.rlbot_controlled:
        # Python file relative to the config location.
        python_file = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)
        agent_class_wrapper = import_agent(python_file)
        bot_parameters = agent_class_wrapper.get_loaded_class().create_agent_configurations()
        bot_parameters.parse_file(config_bundle.config_obj)

    return bot_name, team_num, python_file, bot_parameters
