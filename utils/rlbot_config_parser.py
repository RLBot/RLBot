import configparser
import os

import sys

from agents.base_agent import BaseAgent, BOT_CONFIG_LOADOUT_HEADER, BOT_CONFIG_LOADOUT_ORANGE_HEADER, \
    BOT_CONFIG_MODULE_HEADER
from utils.custom_config import ConfigObject

PARTICPANT_CONFIGURATION_HEADER = 'Participant Configuration'
PARTICPANT_BOT_KEY = 'participant_is_bot'
PARTICPANT_RLBOT_KEY = 'participant_is_rlbot_controlled'
PARTICPANT_CONFIG_KEY = 'participant_config'
PARTICPANT_BOT_SKILL_KEY = 'participant_bot_skill'
PARTICPANT_TEAM = 'participant_team'
RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'


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


def get_bot_config_file_list(botCount, config):
    config_file_list = []
    for i in range(botCount):
        config_file_list.append(config.get(PARTICPANT_CONFIGURATION_HEADER, PARTICPANT_CONFIG_KEY, str(i)))
    return config_file_list


def create_bot_config_parser():
    config_object = ConfigObject()
    rlbot_header = config_object.add_header_name(RLBOT_CONFIGURATION_HEADER)
    rlbot_header.add_value('num_participants', int, default=2, description='The number of players on the field')

    participant_header = config_object.add_header_name(PARTICPANT_CONFIGURATION_HEADER, is_indexed=True)
    participant_header.add_value(PARTICPANT_TEAM, int, default=0,
                                 description="Which team the player should be on:" +
                                             "\nteam 0 (blue) shoots on positive goal, " +
                                             "team 1 (orange) shoots on negative goal")

    participant_header.add_value(PARTICPANT_CONFIG_KEY, str, default='./agents/atba/atba.cfg',
                                 description="The location of the configuration file for a specific agent")

    participant_header.add_value(PARTICPANT_BOT_KEY, bool, default='yes',
                                 description='Accepted values are "1", "yes", "true", and "on", for True,' +
                                             ' and "0", "no", "false", and "off", for False\n' +
                                             'You can have up to 4 local players and they must ' +
                                             'be activated in game or it will crash.\n' +
                                             'If no player is specified you will be spawned in as spectator!')

    participant_header.add_value(PARTICPANT_RLBOT_KEY, bool, default='yes',
                                 description='Accepted values are "1", "yes", "true", and "on", for True,' +
                                             ' and "0", "no", "false", and "off", for False\n' +
                                             'By specifying \'no\' here you can use default bots ' +
                                             'like the rookie, all-star, etc.')

    participant_header.add_value(PARTICPANT_BOT_SKILL_KEY, float, default=1.0,
                                 description='If participant is a bot and not RLBot controlled,' +
                                             ' this value will be used to set bot skill.\n' +
                                             '0.0 is Rookie, 0.5 is pro, 1.0 is all-star. ' +
                                             ' You can set values in-between as well.')


def parse_configurations(gameInputPacket, config_parser):
    bot_names = []
    bot_teams = []
    bot_modules = []


    # Determine number of participants
    num_participants = config_parser.getint(RLBOT_CONFIGURATION_HEADER, 'num_participants')

    # Retrieve bot config files
    participant_configs = get_bot_config_file_list(num_participants, config_parser)

    # Create empty lists


    bot_parameter_list = []
    name_dict = dict()

    gameInputPacket.iNumPlayers = num_participants

    bot_config_object = BaseAgent.create_agent_configurations()

    # Set configuration values for bots and store name and team
    for i in range(num_participants):
        bot_config_path = participant_configs[i]
        sys.path.append(os.path.dirname(bot_config_path))
        bot_config = configparser.RawConfigParser()
        bot_config.read(bot_config_path)

        bot_config_object.reset()
        bot_config_object.parse_file(bot_config)

        team_num = config_parser.getint(PARTICPANT_CONFIGURATION_HEADER,
                                        PARTICPANT_TEAM, str(i))

        loadout_header = BOT_CONFIG_LOADOUT_HEADER
        if (team_num == 1 and bot_config.has_section(BOT_CONFIG_LOADOUT_ORANGE_HEADER)):
            loadout_header = BOT_CONFIG_LOADOUT_ORANGE_HEADER

        gameInputPacket.sPlayerConfiguration[i].bBot = config_parser.getboolean(PARTICPANT_CONFIGURATION_HEADER,
                                                                                PARTICPANT_BOT_KEY, i)
        gameInputPacket.sPlayerConfiguration[i].bRLBotControlled = config_parser.getboolean(
            PARTICPANT_CONFIGURATION_HEADER,
            PARTICPANT_RLBOT_KEY, i)
        gameInputPacket.sPlayerConfiguration[i].fBotSkill = config_parser.getfloat(PARTICPANT_CONFIGURATION_HEADER,
                                                                                   PARTICPANT_BOT_SKILL_KEY, i)
        gameInputPacket.sPlayerConfiguration[i].iPlayerIndex = i

        gameInputPacket.sPlayerConfiguration[i].wName = get_sanitized_bot_name(name_dict,
                                                                               bot_config.get(loadout_header, 'name'))
        gameInputPacket.sPlayerConfiguration[i].ucTeam = team_num

        BaseAgent.parse_bot_loadout(gameInputPacket.sPlayerConfiguration[i], bot_config_object, loadout_header)

        bot_parameter_list.append(bot_config)

        bot_names.append(bot_config.get(loadout_header, 'name'))
        bot_teams.append(config_parser.getint(PARTICPANT_CONFIGURATION_HEADER, PARTICPANT_TEAM, i))
        if gameInputPacket.sPlayerConfiguration[i].bRLBotControlled:
            bot_modules.append(bot_config.get(BOT_CONFIG_MODULE_HEADER, 'agent_module'))
        else:
            bot_modules.append('NO_MODULE_FOR_PARTICIPANT')
