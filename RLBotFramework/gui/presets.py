import os
from PyQt5.QtCore import QTimer
from configparser import RawConfigParser

from RLBotFramework.agents.base_agent import BaseAgent
from RLBotFramework.agents.base_agent import PYTHON_FILE_KEY, BOT_CONFIG_MODULE_HEADER
from RLBotFramework.utils.class_importer import import_agent, get_base_repo_path


class Preset:
    def __init__(self, config, file_path):
        self.config = config
        self.config_path = file_path
        self.name = os.path.basename(file_path).replace(".cfg", "")
        self.save_loadout_timer = None
        self.auto_save = True
        if file_path is not None:
            self.load(file_path)

    def load(self, file_path=None):
        if file_path is None:
            file_path = self.config_path
        if not os.path.exists(self.config_path):
            return
        self.config_path = file_path
        self.config.parse_file(self.config_path)
        return self.config

    def save_config(self, file_path=None, time_out=0):
        if file_path is not None:
            self.config_path = file_path

        def save():
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
    def __init__(self, file_path):
        super().__init__(BaseAgent.create_looks_configurations(), file_path)


class AgentPreset(Preset):
    def __init__(self, file_path):
        file_path = os.path.realpath(file_path)
        basic_config = BaseAgent.create_agent_configurations()

        if os.path.exists(file_path):
            basic_config.parse_file(file_path)
        else:
            atba_file_path = os.path.join(get_base_repo_path(), "agents", "atba", "atba.py")
            rel_path = os.path.relpath(atba_file_path, os.path.dirname(file_path))
            basic_config.set_value(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, rel_path)

        python_file_path = os.path.realpath(os.path.join(os.path.dirname(
            os.path.realpath(file_path)), basic_config.get(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)))
        self.agent_class = import_agent(python_file_path).get_loaded_class()

        super(AgentPreset, self).__init__(self.agent_class.create_agent_configurations(), file_path)
        # Make sure the path to the python file actually gets set to that path, even if there was no config at file_path
        self.config.set_value(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, basic_config.get(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY))

    def load(self, file_path=None):
        self.config = self.agent_class.create_agent_configurations()
        super(AgentPreset, self).load(file_path)
