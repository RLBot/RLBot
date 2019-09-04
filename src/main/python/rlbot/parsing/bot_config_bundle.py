import configparser
import os

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, LOOKS_CONFIG_KEY, \
    PYTHON_FILE_KEY, LOGO_FILE_KEY, SUPPORTS_EARLY_START_KEY
from rlbot.parsing.agent_config_parser import create_looks_configurations, PARTICIPANT_CONFIGURATION_HEADER, \
    PARTICIPANT_CONFIG_KEY
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.logging_utils import get_logger

logger = get_logger('rlbot')


class BotConfigBundle:
    def __init__(self, config_directory, config_obj: ConfigObject, config_file_name: str = None):
        self.config_directory = config_directory
        self.config_file_name = config_file_name
        self.config_path = os.path.join(self.config_directory, self.config_file_name)
        self.config_obj = config_obj
        self.base_agent_config = BaseAgent.base_create_agent_configurations()
        self.base_agent_config.parse_file(self.config_obj, config_directory=config_directory)
        self.name = config_obj.get(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY)
        self.looks_path = self.get_absolute_path(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
        self.python_file = self.get_absolute_path(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)
        self.supports_early_start = self.base_agent_config.get(BOT_CONFIG_MODULE_HEADER, SUPPORTS_EARLY_START_KEY)

    def get_logo_file(self):
        # logo.png is a convention we established during the wintertide tournament.
        logo_name = self.base_agent_config.get(BOT_CONFIG_MODULE_HEADER, LOGO_FILE_KEY) or 'logo.png'
        logo_file = os.path.join(self.config_directory, logo_name)
        if os.path.exists(logo_file):
            return os.path.realpath(logo_file)
        return None

    def get_absolute_path(self, header, key):
        path = self.base_agent_config.get(header, key)
        if path is None:
            raise configparser.NoSectionError(f"Could not find {header}: {key} in the provided configuration!")
        if os.path.isabs(path):
            return path
        if self.config_directory is None:
            raise ValueError(f"Can't locate {path} because it's a relative path and we don't know where to look!")
        joined = os.path.join(self.config_directory, path)
        return os.path.realpath(joined)

    def get_looks_config(self) -> ConfigObject:
        """
        Creates a looks config from the config bundle
        :param config_bundle:
        :return:
        """
        return create_looks_configurations().parse_file(self.looks_path)


def get_bot_config_bundle(bot_config_path) -> BotConfigBundle:
    if not os.path.isfile(bot_config_path):
        raise FileNotFoundError(f"Could not find bot config file {bot_config_path}!")
    raw_bot_config = configparser.RawConfigParser()
    raw_bot_config.read(bot_config_path, encoding='utf8')
    config_directory = os.path.dirname(os.path.realpath(bot_config_path))
    bundle = BotConfigBundle(config_directory, raw_bot_config, os.path.basename(bot_config_path))
    validate_bot_config(bundle)
    return bundle


def validate_bot_config(config_bundle) -> None:
    """
    Checks the config bundle to see whether it has all required attributes.
    """
    if not config_bundle.name:
        bot_config = os.path.join(config_bundle.config_directory, config_bundle.config_file_name or '')
        raise AttributeError(f"Bot config {bot_config} has no name configured!")

    # This will raise an exception if we can't find the looks config, or if it's malformed
    config_bundle.get_looks_config()


def get_bot_config_bundles(num_participants, config: ConfigObject, config_location, config_bundle_overrides):
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
