from rlbot.parsing.agent_config_parser import add_participant_header
from rlbot.parsing.match_settings_config_parser import add_mutator_header, add_match_settings_header
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.logging_utils import get_logger


TEAM_CONFIGURATION_HEADER = "Team Configuration"
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
EXTENSION_PATH_KEY = 'extension_path'
NETWORKING_ROLE_KEY = 'networking_role'
NETWORK_ADDRESS_KEY = 'network_address'

logger = get_logger('rlbot')


def create_bot_config_layout():
    config_object = ConfigObject()
    rlbot_header = config_object.add_header_name(RLBOT_CONFIGURATION_HEADER)
    rlbot_header.add_value(EXTENSION_PATH_KEY, str, default=None,
                           description='A path to the extension file we want to load')
    rlbot_header.add_value(NETWORKING_ROLE_KEY, str, default='none',
                           description='Defines the behavior when connecting multiple RLBot instances over a network.')
    rlbot_header.add_value(NETWORK_ADDRESS_KEY, str, default='127.0.0.1',
                           description='The IP address to connect to if networking is desired.')

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

