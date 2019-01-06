import configparser
import os

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, LOOKS_CONFIG_KEY, PYTHON_FILE_KEY
from rlbot.parsing.custom_config import ConfigObject


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
        return BaseAgent._create_looks_configurations().parse_file(self.looks_path)
