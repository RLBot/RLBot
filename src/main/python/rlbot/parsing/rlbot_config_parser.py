from rlbot.matchconfig.match_config import MatchConfig, ExtensionConfig, MutatorConfig
from rlbot.parsing.agent_config_parser import load_bot_config, get_bot_config_bundles, add_participant_header
from rlbot.parsing.incrementing_integer import IncrementingInteger
from rlbot.parsing.match_settings_config_parser import add_mutator_header, get_num_players, \
    add_match_settings_header, parse_match_settings
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.logging_utils import get_logger


TEAM_CONFIGURATION_HEADER = "Team Configuration"
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
EXTENSION_PATH_KEY = 'extension_path'

logger = get_logger('rlbot')


def create_bot_config_layout():
    config_object = ConfigObject()
    rlbot_header = config_object.add_header_name(RLBOT_CONFIGURATION_HEADER)
    rlbot_header.add_value(EXTENSION_PATH_KEY, str, default=None,
                           description='A path to the extension file we want to load')

    team_header = config_object.add_header_name(TEAM_CONFIGURATION_HEADER)
    team_header.add_value("Team Blue Color", int, default=0,
                          description="Changes Blue team color, use 0 to use default color")
    team_header.add_value("Team Blue Name", str, default="Blue",
                          description="Changes the Team name to use instead of 'Blue'")
    team_header.add_value("Team Orange Color", int, default=0,
                          description="Changes Blue team color, use 0 to use default color")
    team_header.add_value("Team Orange Name", str, default="Orange",
                          description="Changes the Team name to use instead of 'Orange'")
    add_match_settings_header(config_object)
    add_mutator_header(config_object)
    add_participant_header(config_object)
    return config_object


def parse_configurations(config_parser: ConfigObject, config_location, config_bundle_overrides,
                         looks_config_overrides) -> MatchConfig:

    match_config = MatchConfig()
    match_config.mutators = MutatorConfig()

    # Determine number of participants
    match_config.num_players = get_num_players(config_parser)

    parse_match_settings(match_config, config_parser)

    # Retrieve bot config files
    config_bundles = get_bot_config_bundles(match_config.num_players, config_parser, config_location, config_bundle_overrides)

    match_config.player_configs = []

    human_index_tracker = IncrementingInteger(0)

    # Set configuration values for bots and store name and team
    for i in range(match_config.num_players):

        config_bundle = config_bundles[i]

        if i not in looks_config_overrides:
            looks_config_object = config_bundle.get_looks_config()
        else:
            looks_config_object = looks_config_overrides[i]

        player_config = load_bot_config(i, config_bundle, looks_config_object, config_parser, human_index_tracker)

        match_config.player_configs.append(player_config)

    extension_path = config_parser.get(RLBOT_CONFIGURATION_HEADER, EXTENSION_PATH_KEY)
    if extension_path:
        match_config.extension_config = ExtensionConfig()
        match_config.extension_config.python_file_path = extension_path

    return match_config
