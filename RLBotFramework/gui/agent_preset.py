import os
import PyQt5.QtCore.QTimer
from configparser import RawConfigParser

from RLBotFramework.utils.class_importer import import_agent
from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY
from RLBotFramework.parsing.agent_config_parser import get_bot_config_bundle, BotConfigBundle


class AgentPreset:
    def __init__(self, agent_class=BaseAgent, file_path=None):
        self.config = BaseAgent.create_agent_configurations()
        self.config_path = file_path
        self.agent_class = agent_class

    def load(self, file_path=None):
        if file_path is None:
            file_path = self.config_path
        if not os.path.exists(self.config_path):
            raise FileNotFoundError("File " + str(file_path) + " not found!")
        self.config_path = file_path
        self.config.parse_file(self.config_path)
        return self.config

    def load_class(self):
        config_path = self.get_agent_config_path()
        agent_cfg = RawConfigParser()
        agent_cfg.read(config_path)
        bot_module = agent_cfg.get(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)
        self.agent_class = import_agent(bot_module).get_loaded_class()
        self.config = self.agent_class.create_agent_configurations()
        self.config.parse_file(agent_cfg)

        # config_bundle = get_bot_config_bundle(self.get_agent_config_path())
        # python_file = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)
        # self.agent_class = import_agent(python_file).get_loaded_class()
        #
        # self.agent_config = self.agent_class.create_agent_configurations()
        # self.agent_config.parse_file(config_bundle.config_obj)
        # self.config_bundle = BotConfigBundle(config_bundle.config_directory, self.agent_config)

    def save_loadout_config(self, file_path=None, time_out=0):
        if file_path is None:
            file_path = self.config_path
        if not os.path.exists(self.config_path):
            raise FileNotFoundError("File " + str(file_path) + " not found!")

        def save():
            if not os.path.exists(self.config_path):
                return
            with open(self.config_path, "w") as f:
                f.write(str(self.config))

        if self.save_loadout_timer is None:
            self.save_loadout_timer = PyQt5.QtCore.QTimer()
            self.save_loadout_timer.timeout.connect(save)
        self.save_loadout_timer.start(time_out)  # Time-out for timer over here