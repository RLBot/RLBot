import os
from PyQt5.QtCore import QTimer

from RLBotFramework.agents.base_agent import BaseAgent


class Preset:
    def __init__(self, config, file_path=None):
        self.config = config
        self.config_path = file_path
        self.name = os.path.basename(file_path).strip(".cfg")
        if file_path is not None:
            self.load(file_path)

    def load(self, file_path=None):
        if file_path is None:
            file_path = self.config_path
        if not os.path.exists(self.config_path):
            raise FileNotFoundError("File " + str(file_path) + " not found!")
        self.config_path = file_path
        self.config.parse_file(self.config_path)
        return self.config

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
            self.save_loadout_timer = QTimer()
            self.save_loadout_timer.timeout.connect(save)
        self.save_loadout_timer.start(time_out)  # Time-out for timer over here

    def get_name(self):
        return self.name


class LoadoutPreset(Preset):
    def __init__(self, file_path=None):
        super().__init__(BaseAgent.create_looks_configurations(), file_path)


class AgentPreset(Preset):
    def __init__(self, file_path=None):
        super().__init__(BaseAgent.create_agent_configurations(), file_path)
        self.name = os.path.basename(file_path).strip(".cfg")
