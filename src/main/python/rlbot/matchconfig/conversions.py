import json
from pathlib import Path

from rlbot.matchconfig.loadout_config import LoadoutConfig, LoadoutPaintConfig
from rlbot.matchconfig.match_config import MatchConfig, ExtensionConfig, MutatorConfig, PlayerConfig
from rlbot.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, PARTICIPANT_TYPE_KEY, load_bot_appearance, PARTICIPANT_BOT_SKILL_KEY
from rlbot.parsing.bot_config_bundle import BotConfigBundle, get_bot_config_bundles
from rlbot.parsing.custom_config import ConfigObject
from rlbot.parsing.incrementing_integer import IncrementingInteger
from rlbot.parsing.match_settings_config_parser import get_num_players, parse_match_settings
from rlbot.parsing.rlbot_config_parser import create_bot_config_layout, NETWORKING_ROLE_KEY, NETWORK_ADDRESS_KEY
from rlbot.parsing.rlbot_config_parser import RLBOT_CONFIGURATION_HEADER, EXTENSION_PATH_KEY

# ====== rlbot.cfg -> MatchConfig ======
from rlbot.utils.structures.start_match_structures import MAX_PLAYERS


def read_match_config_from_file(match_config_path: Path) -> MatchConfig:
    """
    Parse the rlbot.cfg file on disk into the python datastructure.
    """
    config_obj = create_bot_config_layout()
    config_obj.parse_file(match_config_path, max_index=MAX_PLAYERS)
    return parse_match_config(config_obj, match_config_path, {}, {})


def parse_match_config(config_parser: ConfigObject, config_location, config_bundle_overrides,
                       looks_config_overrides) -> MatchConfig:

    match_config = MatchConfig()
    match_config.mutators = MutatorConfig()

    # Determine number of participants
    num_players = get_num_players(config_parser)

    parse_match_settings(match_config, config_parser)

    # Retrieve bot config files
    config_bundles = get_bot_config_bundles(num_players, config_parser, config_location, config_bundle_overrides)

    match_config.player_configs = []

    human_index_tracker = IncrementingInteger(0)

    # Set configuration values for bots and store name and team
    for i in range(num_players):

        config_bundle = config_bundles[i]

        if i not in looks_config_overrides:
            looks_config_object = config_bundle.get_looks_config()
        else:
            looks_config_object = looks_config_overrides[i]

        player_config = _load_bot_config(i, config_bundle, looks_config_object, config_parser, human_index_tracker)

        match_config.player_configs.append(player_config)

    extension_path = config_parser.get(RLBOT_CONFIGURATION_HEADER, EXTENSION_PATH_KEY)
    if extension_path and extension_path != 'None':  # The string 'None' ends up in people's config a lot.
        match_config.extension_config = ExtensionConfig()
        match_config.extension_config.python_file_path = extension_path

    match_config.networking_role = config_parser.get(RLBOT_CONFIGURATION_HEADER, NETWORKING_ROLE_KEY)
    match_config.network_address = config_parser.get(RLBOT_CONFIGURATION_HEADER, NETWORK_ADDRESS_KEY)

    return match_config


def get_team(config, index):
    """
    Returns which team the bot is on (represented by an integer)
    """
    return config.getint(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, index)


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
    elif bot_type == 'party_member_bot':
        # this is a bot running under a human

        is_rlbot = True
        is_bot = False
    else:
        raise ValueError('participant_type value is not "human", "rlbot", "psyonix" or "party_member_bot"')

    return is_bot, is_rlbot


def _load_bot_config(index, config_bundle: BotConfigBundle,
                     looks_config_object: ConfigObject, overall_config: ConfigObject,
                     human_index_tracker: IncrementingInteger) -> PlayerConfig:
    """
    Loads the config data of a single bot
    :param index: This is the bot index (where it appears in game_cars)
    :param bot_configuration: A config object that will eventually be transformed and sent to the game.
    :param config_bundle: A config object for a single bot
    :param overall_config: This is the config for the entire session not one particular bot
    :param human_index_tracker: An object of type HumanIndexManager that helps set human_index correctly.
    :return:
    """

    bot_configuration = PlayerConfig()
    bot_configuration.config_path = config_bundle.config_path

    team_num = get_team(overall_config, index)

    bot_configuration.team = team_num

    # Setting up data about what type of bot it is
    bot_type = overall_config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TYPE_KEY, index)
    bot_configuration.bot, bot_configuration.rlbot_controlled = get_bot_options(bot_type)
    bot_configuration.bot_skill = overall_config.getfloat(
        PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY, index)

    if not bot_configuration.bot:
        bot_configuration.human_index = human_index_tracker.increment()

    # Setting up the bots name
    bot_configuration.name = config_bundle.name

    loadout_config = load_bot_appearance(looks_config_object, team_num)
    bot_configuration.loadout_config = loadout_config

    return bot_configuration


# ====== MatchConfig -> JSON ======
# The JSON conversion serializes and deserializes MatchConfig in its entirety,
# including player config which is usually specified in different files.

known_types = {
    MatchConfig: '__MatchConfig__',
    MutatorConfig: '__MutatorConfig__',
    ExtensionConfig: '__ExtensionConfig__',
    PlayerConfig: '__PlayerConfig__',
    LoadoutConfig: '__LoadoutConfig__',
    LoadoutPaintConfig: '__LoadoutPaintConfig__',
}


class ConfigJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        for cls, tag in known_types.items():
            if not isinstance(obj, cls):
                continue
            json_obj = obj.__dict__.copy()
            json_obj[tag] = True
            return json_obj
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

# ====== JSON -> MatchConfig ======


def as_match_config(json_obj) -> MatchConfig:
    for cls, tag in known_types.items():
        if not json_obj.get(tag, False):
            continue
        obj = cls()
        del json_obj[tag]
        obj.__dict__ = json_obj
        return obj
    return json_obj
