import configparser
import itertools
import os
from pathlib import Path
from typing import List

from requirements.requirement import Requirement

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, LOOKS_CONFIG_KEY, \
    PYTHON_FILE_KEY, LOGO_FILE_KEY, SUPPORTS_EARLY_START_KEY, LOADOUT_GENERATOR_FILE_KEY, SUPPORTS_STANDALONE
from rlbot.agents.base_loadout_generator import BaseLoadoutGenerator
from rlbot.agents.base_script import SCRIPT_FILE_KEY, BaseScript
from rlbot.agents.rlbot_runnable import REQUIRED_PYTHON_37, RLBotRunnable, REQUIREMENTS_FILE_KEY, REQUIRES_TKINTER, USE_VIRTUAL_ENVIRONMENT_KEY
from rlbot.utils.requirements_management import get_missing_packages, get_packages_needing_upgrade
from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.parsing.agent_config_parser import create_looks_configurations, PARTICIPANT_CONFIGURATION_HEADER, \
    PARTICIPANT_CONFIG_KEY, load_bot_appearance, SCRIPT_CONFIGURATION_HEADER, SCRIPT_CONFIG_KEY
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.class_importer import import_class_with_base
from rlbot.utils.logging_utils import get_logger

logger = get_logger('rlbot')


class RunnableConfigBundle:
    def __init__(self, config_directory, config_obj: ConfigObject, config_file_name: str = None):
        self.config_directory = config_directory
        self.config_file_name = config_file_name
        self.config_path = os.path.join(self.config_directory, self.config_file_name)
        self.config_obj = config_obj
        self.base_agent_config = RLBotRunnable.base_create_agent_configurations()
        self.base_agent_config.parse_file(self.config_obj, config_directory=config_directory)
        self.name = config_obj.get(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY)
        self.supports_early_start = self.base_agent_config.get(BOT_CONFIG_MODULE_HEADER, SUPPORTS_EARLY_START_KEY)
        self.requirements_file = self.get_absolute_path(BOT_CONFIG_MODULE_HEADER, REQUIREMENTS_FILE_KEY)
        self.use_virtual_environment = self.base_agent_config.getboolean(BOT_CONFIG_MODULE_HEADER, USE_VIRTUAL_ENVIRONMENT_KEY)
        self.requires_py37 = self.base_agent_config.getboolean(BOT_CONFIG_MODULE_HEADER, REQUIRED_PYTHON_37)

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
            return None
        if os.path.isabs(path):
            return path
        if self.config_directory is None:
            raise ValueError(f"Can't locate {path} because it's a relative path and we don't know where to look!")
        joined = os.path.join(self.config_directory, path)
        return os.path.realpath(joined)

    def get_missing_python_packages(self) -> List[Requirement]:
        special_reqs = []
        if self.base_agent_config.getboolean(BOT_CONFIG_MODULE_HEADER, REQUIRES_TKINTER):
            special_reqs.append('tkinter')

        if self.use_virtual_environment:
            # Ignore the requirements file for now, because we will be installing it automatically later!
            return get_missing_packages(requirements_file=None, special_reqs=special_reqs)
        else:
            return get_missing_packages(requirements_file=self.requirements_file, special_reqs=special_reqs)

    def get_python_packages_needing_upgrade(self) -> List[Requirement]:
        if self.requirements_file and not self.use_virtual_environment:
            return get_packages_needing_upgrade(requirements_file=self.requirements_file)
        return []


class BotConfigBundle(RunnableConfigBundle):
    def __init__(self, config_directory, config_obj: ConfigObject, config_file_name: str = None):
        super().__init__(config_directory, config_obj, config_file_name)
        self.base_agent_config = BaseAgent.base_create_agent_configurations()
        self.base_agent_config.parse_file(self.config_obj, config_directory=config_directory)
        self.python_file = self.get_absolute_path(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)
        self.supports_standalone = self.base_agent_config.getboolean(BOT_CONFIG_MODULE_HEADER, SUPPORTS_STANDALONE)
        self.looks_path = self.get_absolute_path(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
        self.loadout_generator_file = self.get_absolute_path(BOT_CONFIG_MODULE_HEADER, LOADOUT_GENERATOR_FILE_KEY)

    def get_looks_config(self) -> ConfigObject:
        """
        Creates a looks config from the config bundle
        :param config_bundle:
        :return:
        """
        if self.looks_path is None:
            raise ValueError("Cannot get looks config because looks_path is None")
        return create_looks_configurations().parse_file(self.looks_path)

    def generate_loadout_config(self, player_index: int, team: int) -> LoadoutConfig:
        if self.loadout_generator_file:
            try:
                generator_wrapper = import_class_with_base(self.loadout_generator_file, BaseLoadoutGenerator)
                generator_class = generator_wrapper.get_loaded_class()
                generator = generator_class(Path(self.config_directory))
                loadout_config = generator.generate_loadout(player_index, team)
                if loadout_config and isinstance(loadout_config, LoadoutConfig):
                    return loadout_config
                else:
                    logger.warn(f"Generated loadout is invalid, will fall back to file. Loadout was: {loadout_config}")
            except Exception as e:
                logger.warn(f"Failed to generate loadout config, will fall back to file. Error was: {e}")

        config_object = self.get_looks_config()
        return load_bot_appearance(config_object, team)


class ScriptConfigBundle(RunnableConfigBundle):
    def __init__(self, config_directory, config_obj: ConfigObject, config_file_name):
        super().__init__(config_directory, config_obj, config_file_name)
        self.base_agent_config = BaseScript.base_create_agent_configurations()
        self.base_agent_config.parse_file(self.config_obj, config_directory=config_directory)
        self.script_file = self.get_absolute_path(BOT_CONFIG_MODULE_HEADER, SCRIPT_FILE_KEY)
        if not self.script_file:
            raise AttributeError(f"Script config {self.config_path} has no script file configured!")


def get_config_obj_and_directory(config_path):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Could not find config file {config_path}!")
    raw_bot_config = configparser.RawConfigParser()
    raw_bot_config.read(config_path, encoding='utf8')
    config_directory = os.path.dirname(os.path.realpath(config_path))
    return raw_bot_config, config_directory


def get_bot_config_bundle(bot_config_path) -> BotConfigBundle:
    raw_bot_config, config_directory = get_config_obj_and_directory(bot_config_path)
    bundle = BotConfigBundle(config_directory, raw_bot_config, os.path.basename(bot_config_path))
    validate_bot_config(bundle)
    return bundle


def get_script_config_bundle(config_path) -> ScriptConfigBundle:
    raw_bot_config, config_directory = get_config_obj_and_directory(config_path)
    bundle = ScriptConfigBundle(config_directory, raw_bot_config, os.path.basename(config_path))
    return bundle


def validate_bot_config(config_bundle) -> None:
    """
    Checks the config bundle to see whether it has all required attributes.
    """
    if not config_bundle.looks_path or not config_bundle.name:
        raise AttributeError(f"Bot config {config_bundle.config_path} is missing a name or a looks_path!")

    # This will raise an exception if the looks config is malformed
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


def get_script_config_bundles(match_config: ConfigObject, config_location):
    """
    Adds all the script config bundles found in the match config file.
    Attempts to read indexed config keys until it hits an empty one.
    """
    config_bundles = []
    for i in itertools.count():
        script_config_relative_path = match_config.get(SCRIPT_CONFIGURATION_HEADER, SCRIPT_CONFIG_KEY, i)
        if script_config_relative_path is None or script_config_relative_path == 'None':
            break
        script_config_path = os.path.join(os.path.dirname(config_location), script_config_relative_path)
        config_bundles.append(get_script_config_bundle(script_config_path))

    return config_bundles
