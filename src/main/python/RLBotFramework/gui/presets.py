import os
from PyQt5.QtCore import QTimer
from configparser import RawConfigParser

from RLBotFramework.agents.base_agent import BaseAgent
from RLBotFramework.agents.base_agent import PYTHON_FILE_KEY, BOT_CONFIG_MODULE_HEADER
from RLBotFramework.utils.class_importer import import_agent, get_python_root


class Preset:
    def __init__(self, config, file_path, name):
        self.config = config
        self.config_path = file_path
        self.name = name
        self.save_loadout_timer = None
        self.auto_save = True
        if file_path is not None:
            self.load(file_path)

    def load(self, file_path=None):
        if file_path is None:
            file_path = self.config_path
        if not os.path.isfile(file_path):
            self.config_path = ""
            return
        self.config_path = file_path
        self.config.parse_file(file_path)
        return self.config

    def save_config(self, file_path=None, time_out=0):
        if file_path is not None:
            self.config_path = file_path

        def save():
            if self.config_path is None or self.config_path == "":
                return
            with open(self.config_path, "w") as f:
                f.write(str(self.config))

        if self.save_loadout_timer is None:
            self.save_loadout_timer = QTimer()
            self.save_loadout_timer.setSingleShot(True)
            self.save_loadout_timer.timeout.connect(save)
        self.save_loadout_timer.start(time_out)  # Time-out for timer over here

    def set_auto_save(self, auto_save):
        self.auto_save = auto_save

    def get_name(self):
        return self.name


class LoadoutPreset(Preset):
    def __init__(self, name, file_path=None):
        super().__init__(BaseAgent.create_looks_configurations(), file_path, name)


class AgentPreset(Preset):
    def __init__(self, name, file_path=None):
        basic_config = BaseAgent.create_agent_configurations()

        if file_path is not None and os.path.isfile(file_path):
            file_path = os.path.realpath(file_path)
            basic_config.parse_file(file_path)
        else:
            base_agent_path = os.path.join(get_python_root(), "RLBotFramework", "agents", "base_agent.py")
            rel_path = os.path.relpath(base_agent_path, get_python_root())
            basic_config.set_value(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, rel_path)

        python_file_path = os.path.realpath(os.path.join(os.path.dirname(
            os.path.realpath(file_path)), basic_config.get(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)))
        try:
            self.agent_class = import_agent(python_file_path).get_loaded_class()
        except (ValueError, ModuleNotFoundError):
            self.agent_class = BaseAgent

        super().__init__(self.agent_class.create_agent_configurations(), file_path, name)
        # Make sure the path to the python file actually gets set to that path, even if there was no config at file_path
        self.config.set_value(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, basic_config.get(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY))

    def load(self, file_path=None):
        self.config = self.agent_class.create_agent_configurations()
        super().load(file_path)

    def load_agent_class(self, python_file_path):
        try:
            self.agent_class = import_agent(python_file_path).get_loaded_class()
        except (ValueError, ModuleNotFoundError):
            self.agent_class = BaseAgent
        old_config = self.config.copy()
        self.config = self.agent_class.create_agent_configurations()
        self.config.parse_file(old_config)
