import configparser
import inspect
import os

from PyQt5.QtCore import QTimer

from rlbot.agents.base_agent import BaseAgent, LOOKS_CONFIG_KEY
from rlbot.agents.base_agent import PYTHON_FILE_KEY, BOT_CONFIG_MODULE_HEADER
from rlbot.parsing.agent_config_parser import get_bot_config_bundle
from rlbot.utils.class_importer import import_agent


class Preset:
    """
    Stores a config, the config path, a preset name and has methods to save/load the preset
    """
    def __init__(self, config, file_path, name):
        self.config = config
        self.config_path = file_path
        self.name = name
        self.save_loadout_timer = None
        if file_path is not None:
            self.load(file_path)

    def load(self, file_path=None):
        if file_path is None:
            file_path = self.config_path
        if not os.path.isfile(file_path):
            self.config_path = ""
            return
        self.config_path = file_path
        raw_parser = configparser.RawConfigParser()
        raw_parser.read(file_path, encoding='utf8')
        for section in self.config.headers.keys():
            if not raw_parser.has_section(section):
                raise configparser.NoSectionError(section)
        self.config.parse_file(raw_parser)
        return self.config

    def save_config(self, file_path=None, time_out=0, message_out=None):
        if file_path is not None:
            self.config_path = file_path

        def save():
            if self.config_path is None or self.config_path == "":
                return

            self.save_loadout_timer.setInterval(1000)
            if self.remaining_save_timer > 0:
                message_out("Saving preset " + self.name + " in " + str(self.remaining_save_timer) + " seconds", 1000)
                self.remaining_save_timer -= 1
            else:
                with open(self.config_path, "w", encoding='utf8') as f:
                    f.write(str(self.config))
                message_out("Saved preset " + self.name + " to " + self.config_path, 5000)
                self.save_loadout_timer.stop()

        if self.save_loadout_timer is None:
            self.save_loadout_timer = QTimer()
            self.save_loadout_timer.timeout.connect(save)
        self.remaining_save_timer = time_out
        self.save_loadout_timer.start(0)  # Time-out for timer over here

    def get_name(self):
        return self.name


class LoadoutPreset(Preset):
    """
    A class extending Preset to handle a LoadoutPreset, which is based on the looks configurations file
    """
    def __init__(self, name, file_path=None):
        super().__init__(BaseAgent._create_looks_configurations(), file_path, name)


class AgentPreset(Preset):
    """
    A class extending Preset to handle an AgentPreset, which is based on the agent configuration file and which also contains the Agent class
    """
    def __init__(self, name, file_path=None):

        self.looks_path = None

        if file_path is not None and os.path.isfile(file_path):
            config_bundle = get_bot_config_bundle(file_path)
            self.looks_path = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
            python_file_path = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)

        else:
            python_file_path = inspect.getfile(BaseAgent)

        try:
            self.agent_class = import_agent(python_file_path).get_loaded_class()
        except (ValueError, ModuleNotFoundError, FileNotFoundError) as e:
            raise ValueError("Problem when processing {}: {}".format(file_path, str(e)))

        super().__init__(self.agent_class.base_create_agent_configurations(), file_path, name)
        # Make sure the path to the python file actually gets set to that path, even if there was no config at file_path
        self.config.set_value(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, python_file_path)

    def load(self, file_path=None):
        self.config = self.agent_class.base_create_agent_configurations()
        super().load(file_path)

    def load_agent_class(self, python_file_path):
        result = True
        self.agent_class = import_agent(python_file_path).get_loaded_class()
        old_config = self.config.copy()
        self.config = self.agent_class.base_create_agent_configurations()
        self.config.parse_file(old_config)
        return result
