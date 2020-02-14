import json
from json import JSONDecodeError

from rlbot.matchconfig.loadout_config import LoadoutConfig, LoadoutPaintConfig, Color
from rlbot.parsing.custom_config import ConfigObject, ConfigHeader
from rlbot.utils.logging_utils import get_logger

PARTICIPANT_CONFIGURATION_HEADER = 'Participant Configuration'
PARTICIPANT_CONFIG_KEY = 'participant_config'
PARTICIPANT_BOT_SKILL_KEY = 'participant_bot_skill'
PARTICIPANT_TYPE_KEY = 'participant_type'
PARTICIPANT_TEAM = 'participant_team'
PARTICIPANT_LOADOUT_CONFIG_KEY = 'participant_loadout_config'
BOT_CONFIG_LOADOUT_HEADER = 'Bot Loadout'
BOT_CONFIG_LOADOUT_ORANGE_HEADER = 'Bot Loadout Orange'
BOT_CONFIG_LOADOUT_PAINT_BLUE_HEADER = 'Bot Paint Blue'
BOT_CONFIG_LOADOUT_PAINT_ORANGE_HEADER = 'Bot Paint Orange'

logger = get_logger('rlbot')


def add_participant_header(config_object):
    participant_header = config_object.add_header_name(PARTICIPANT_CONFIGURATION_HEADER, is_indexed=True)
    participant_header.add_value(PARTICIPANT_CONFIG_KEY, str, default=None,
                                 description="""The location of the configuration file for your agent here.
                                             Only total_num_participants config files will be read!
                                             Everything needs a config, even players and default bots.
                                             We still set loadouts and names from config!""")

    participant_header.add_value(PARTICIPANT_TEAM, int, default=0,
                                 description="Which team the player should be on:" +
                                             "\nteam 0 (blue) shoots on positive goal, " +
                                             "team 1 (orange) shoots on negative goal")

    participant_header.add_value(PARTICIPANT_TYPE_KEY, str, default='rlbot',
                                 description="""Accepted values are "human", "rlbot", "psyonix" and "party_member_bot"
                                             You can have up to 4 local players and they must
                                             be activated in game or it will crash.
                                             If no player is specified you will be spawned in as spectator!
                                             human - not controlled by the framework
                                             rlbot - controlled by the framework
                                             psyonix - default bots (skill level can be changed with participant_bot_skill
                                             party_member_bot - controlled by an rlbot but the game detects it as a human""")

    participant_header.add_value(PARTICIPANT_BOT_SKILL_KEY, float, default=1.0,
                                 description='If participant is a bot and not RLBot controlled,' +
                                             ' this value will be used to set bot skill.\n' +
                                             '0.0 is Rookie, 0.5 is pro, 1.0 is all-star. ' +
                                             ' You can set values in-between as well.')

    participant_header.add_value(PARTICIPANT_LOADOUT_CONFIG_KEY, str, default="None",
                                 description="""A path to a loadout config file which will override the path in the agent config
                                             Use None to extract the path from the agent config""")


def load_bot_appearance(looks_config_object: ConfigObject, team_num: int) -> LoadoutConfig:
    loadout_config = LoadoutConfig()
    loadout_config.paint_config = LoadoutPaintConfig()

    loadout_header = BOT_CONFIG_LOADOUT_HEADER
    if team_num == 1 and looks_config_object.has_section(BOT_CONFIG_LOADOUT_ORANGE_HEADER):
        loadout_header = BOT_CONFIG_LOADOUT_ORANGE_HEADER

    parse_bot_loadout(loadout_config, looks_config_object, loadout_header)

    if team_num == 0 and looks_config_object.has_section(BOT_CONFIG_LOADOUT_PAINT_BLUE_HEADER):
        parse_bot_loadout_paint(loadout_config.paint_config, looks_config_object, BOT_CONFIG_LOADOUT_PAINT_BLUE_HEADER)

    if team_num == 1 and looks_config_object.has_section(BOT_CONFIG_LOADOUT_PAINT_ORANGE_HEADER):
        parse_bot_loadout_paint(loadout_config.paint_config, looks_config_object,
                                BOT_CONFIG_LOADOUT_PAINT_ORANGE_HEADER)

    return loadout_config


def create_looks_configurations() -> ConfigObject:
    config = ConfigObject()
    config.add_header(BOT_CONFIG_LOADOUT_HEADER, create_loadout())
    config.add_header(BOT_CONFIG_LOADOUT_ORANGE_HEADER, create_loadout())
    config.add_header(BOT_CONFIG_LOADOUT_PAINT_BLUE_HEADER, create_loadout_paint())
    config.add_header(BOT_CONFIG_LOADOUT_PAINT_ORANGE_HEADER, create_loadout_paint())
    return config


def create_loadout() -> ConfigHeader:
    header = ConfigHeader()
    header.add_value('team_color_id', int, default=0, description='Primary Color selection')
    header.add_value('custom_color_id', int, default=0, description='Secondary Color selection')
    header.add_value('car_id', int, default=0, description='Car type (Octane, Merc, etc)')
    header.add_value('decal_id', int, default=0, description='Type of decal')
    header.add_value('wheels_id', int, default=0, description='Wheel selection')
    header.add_value('boost_id', int, default=0, description='Boost selection')
    header.add_value('antenna_id', int, default=0, description='Antenna Selection')
    header.add_value('hat_id', int, default=0, description='Hat Selection')
    header.add_value('paint_finish_id', int, default=0, description='Paint Type (for first color)')
    header.add_value('custom_finish_id', int, default=0, description='Paint Type (for secondary color)')
    header.add_value('engine_audio_id', int, default=0, description='Engine Audio Selection')
    header.add_value('trails_id', int, default=0, description='Car trail Selection')
    header.add_value('goal_explosion_id', int, default=0, description='Goal Explosion Selection')
    header.add_value('primary_color_lookup', str, default=None,
                     description='Finds the closest primary color swatch based on the provided RGB value '
                                 'like [34, 255, 60]')
    header.add_value('secondary_color_lookup', str, default=None,
                     description='Finds the closest secondary color swatch based on the provided RGB value '
                                 'like [34, 255, 60]')

    return header


def create_loadout_paint() -> ConfigHeader:
    header = ConfigHeader()

    header.add_value('car_paint_id', int, default=0)
    header.add_value('decal_paint_id', int, default=0)
    header.add_value('wheels_paint_id', int, default=0)
    header.add_value('boost_paint_id', int, default=0)
    header.add_value('antenna_paint_id', int, default=0)
    header.add_value('hat_paint_id', int, default=0)
    header.add_value('trails_paint_id', int, default=0)
    header.add_value('goal_explosion_paint_id', int, default=0)

    return header


def parse_bot_loadout(player_configuration, bot_config, loadout_header):
    player_configuration.team_color_id = bot_config.getint(loadout_header, 'team_color_id')
    player_configuration.custom_color_id = bot_config.getint(loadout_header, 'custom_color_id')
    player_configuration.car_id = bot_config.getint(loadout_header, 'car_id')
    player_configuration.decal_id = bot_config.getint(loadout_header, 'decal_id')
    player_configuration.wheels_id = bot_config.getint(loadout_header, 'wheels_id')
    player_configuration.boost_id = bot_config.getint(loadout_header, 'boost_id')
    player_configuration.antenna_id = bot_config.getint(loadout_header, 'antenna_id')
    player_configuration.hat_id = bot_config.getint(loadout_header, 'hat_id')
    player_configuration.paint_finish_id = bot_config.getint(loadout_header, 'paint_finish_id')
    player_configuration.custom_finish_id = bot_config.getint(loadout_header, 'custom_finish_id')
    player_configuration.engine_audio_id = bot_config.getint(loadout_header, 'engine_audio_id')
    player_configuration.trails_id = bot_config.getint(loadout_header, 'trails_id')
    player_configuration.goal_explosion_id = bot_config.getint(loadout_header, 'goal_explosion_id')
    player_configuration.primary_color_lookup = parse_color_string(
        bot_config.get(loadout_header, 'primary_color_lookup'))
    player_configuration.secondary_color_lookup = parse_color_string(
        bot_config.get(loadout_header, 'secondary_color_lookup'))


def parse_color_string(color_lookup_string):
    if color_lookup_string is None:
        return None
    if color_lookup_string == 'None':
        return None
    try:
        color_array = json.loads(color_lookup_string)
        return Color(
            red=color_array[0],
            green=color_array[1],
            blue=color_array[2],
            alpha=color_array[3] if len(color_array) > 3 else 255)
    except JSONDecodeError:
        logger.warn(f"Failed to parse color lookup: {color_lookup_string}")
        return None


def parse_bot_loadout_paint(paint_config: LoadoutPaintConfig, bot_config: ConfigObject, loadout_header: str):
    paint_config.car_paint_id = bot_config.getint(loadout_header, 'car_paint_id')
    paint_config.decal_paint_id = bot_config.getint(loadout_header, 'decal_paint_id')
    paint_config.wheels_paint_id = bot_config.getint(loadout_header, 'wheels_paint_id')
    paint_config.boost_paint_id = bot_config.getint(loadout_header, 'boost_paint_id')
    paint_config.antenna_paint_id = bot_config.getint(loadout_header, 'antenna_paint_id')
    paint_config.hat_paint_id = bot_config.getint(loadout_header, 'hat_paint_id')
    paint_config.trails_paint_id = bot_config.getint(loadout_header, 'trails_paint_id')
    paint_config.goal_explosion_paint_id = bot_config.getint(loadout_header, 'goal_explosion_paint_id')
