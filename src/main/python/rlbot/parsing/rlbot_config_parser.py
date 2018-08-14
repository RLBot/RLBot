from rlbot.parsing.agent_config_parser import load_bot_config, get_bot_config_bundles, add_participant_header, \
    get_looks_config
from rlbot.parsing.incrementing_integer import IncrementingInteger
from rlbot.parsing.match_settings_config_parser import add_mutator_header, get_num_players, \
    add_match_settings_header, parse_match_settings
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.start_match_structures import get_player_configuration_list


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


def parse_configurations(start_match_configuration, config_parser, config_location, config_bundle_overrides, looks_configs):
    bot_names = []
    bot_teams = []
    python_files = []

    # Determine number of participants
    num_participants = get_num_players(config_parser)

    parse_match_settings(start_match_configuration, config_parser)

    # Retrieve bot config files
    config_bundles = get_bot_config_bundles(num_participants, config_parser, config_location, config_bundle_overrides)

    # Create empty lists

    bot_parameter_list = []
    name_dict = {}

    start_match_configuration.num_players = num_participants

    player_configuration_list = get_player_configuration_list(start_match_configuration)

    human_index_tracker = IncrementingInteger(0)

    # Set configuration values for bots and store name and team
    for i in range(num_participants):

        config_bundle = config_bundles[i]

        if i not in looks_configs:
            looks_config_object = get_looks_config(config_bundle)
        else:
            looks_config_object = looks_configs[i]

        bot_name, team_number, python_file, bot_parameters = load_bot_config(i, player_configuration_list[i],
                                                                             config_bundle, looks_config_object,
                                                                             config_parser, name_dict,
                                                                             human_index_tracker)

        bot_names.append(bot_name)
        bot_teams.append(team_number)
        python_files.append(python_file)
        bot_parameter_list.append(bot_parameters)

    return num_participants, bot_names, bot_teams, python_files, bot_parameter_list
