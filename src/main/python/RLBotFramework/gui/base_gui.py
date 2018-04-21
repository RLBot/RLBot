import os
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog
import sys

from RLBotFramework.gui.index_manager import IndexManager
from RLBotFramework.gui.base_gui_agent import BaseGuiAgent
from RLBotFramework.parsing.rlbot_config_parser import create_bot_config_layout, get_num_players
from RLBotFramework.gui.presets import LoadoutPreset, AgentPreset
from RLBotFramework.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY
from RLBotFramework.agents.base_agent import BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY
from RLBotFramework.utils.class_importer import get_python_root


class BaseGui:
    """
    Handles GUI functions that should be shared across all GUIs, such as:
        index_manager, overall_config, add_agent/remove_agent (with index_manager handled)
    """

    index_manager_class = IndexManager
    agent_class = BaseGuiAgent

    def __init__(self, overall_config=None):
        self.overall_config = overall_config
        self.overall_config_path = None
        self.overall_config_timer = None
        self.agent_class.overall_config = overall_config

        self.index_manager = self.index_manager_class(10)
        self.loadout_presets = {}
        self.agent_presets = {}
        self.agents = []

    def load_overall_config(self, config_path=None):
        if self.overall_config is None:
            self.overall_config = create_bot_config_layout()
        self.agent_class.overall_config = self.overall_config
        if config_path is None:
            config_path = QFileDialog.getOpenFileName(self, "Load Overall Config", "", "Config Files (*.cfg)")[0]
            if not config_path:
                self.show_status_message("No file selected, not loading config")
                return
        if not os.path.isfile(config_path):
            raise FileNotFoundError("The file " + config_path + " does not exist, not loading config")
        self.overall_config_path = config_path
        self.overall_config.parse_file(config_path, 10)
        self.load_agents()
        self.update_overall_config_stuff()

    def save_overall_config(self, time_out=5000):
        def save():
            if not os.path.exists(self.overall_config_path):
                return
            with open(self.overall_config_path, "w") as f:
                f.write(str(self.overall_config))
            self.show_status_message("Saved the overall config")
        if self.overall_config_timer is None:
            self.overall_config_timer = QTimer()
            self.overall_config_timer.setSingleShot(True)
            self.overall_config_timer.timeout.connect(save)
        save_path = self.overall_config_path
        if save_path is None or not os.path.exists(save_path):
            save_path = QFileDialog.getSaveFileName(self, "Save Overall Config", "", "Config Files (*.cfg)")[0]
            if not save_path:
                self.show_status_message("Unable to save a config without location")
                return
            self.overall_config_path = save_path
        self.overall_config_timer.start(time_out)  # Time-out for timer over here

    def load_agents(self, config_file=None):
        """
        Loads all agents for this team from the rlbot.cfg
        :param config_file:  A config file that is similar to rlbot.cfg
        """
        if config_file is not None:
            self.overall_config = config_file
        self.agents.clear()
        num_participants = get_num_players(self.overall_config)
        for i in range(num_participants):
            self.load_agent(i)

    def load_agent(self, overall_index=None):
        if not self.index_manager.has_free_slots():
            return None
        if overall_index is None:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.use_index(overall_index)
        agent = self.add_agent(overall_index=overall_index)

        agent_preset = self.add_agent_preset(agent.get_agent_config_path())
        agent.set_agent_preset(agent_preset)

        loadout_file = self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY, overall_index)
        if loadout_file is None or loadout_file == "None":
            directory = os.path.dirname(os.path.realpath(agent.get_agent_config_path()))
            file_path = agent_preset.config.get(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
            loadout_file = os.path.realpath(os.path.join(directory, file_path))
        else:
            directory = get_python_root()
            file_path = loadout_file
            loadout_file = os.path.realpath(os.path.join(directory, file_path))
        loadout_preset = self.add_loadout_preset(loadout_file)
        agent.set_loadout_preset(loadout_preset)
        return agent

    def add_agent(self, overall_index=None, team_index=None):
        """
        Creates the agent using self.agent_class and adds it to the index manager.
        :param overall_index: The index of the bot in the config file if it already exists.
        :param team_index: The index of the team to place the agent in
        :return agent:
        """
        if not self.index_manager.has_free_slots():
            return
        if overall_index is None:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.use_index(overall_index)
        agent = self.agent_class(overall_index=overall_index)
        if team_index is not None:
            agent.set_team(team_index)

        self.agents.append(agent)
        return agent

    def add_loadout_preset(self, file_path):
        if os.path.basename(file_path).replace(".cfg", "") in self.loadout_presets:
            return self.loadout_presets[os.path.basename(file_path).replace(".cfg", "")]
        preset = LoadoutPreset(file_path)
        self.loadout_presets[preset.get_name()] = preset
        return preset

    def add_agent_preset(self, file_path):
        if os.path.basename(file_path).replace(".cfg", "") in self.agent_presets:
            return self.agent_presets[os.path.basename(file_path).replace(".cfg", "")]
        preset = AgentPreset(file_path)
        self.agent_presets[preset.get_name()] = preset
        return preset

    def remove_agent(self, agent):
        """
        Removes the given agent from this team frame.
        :param agent: An instance of BaseAgentFrame
        """
        self.index_manager.free_index(agent.overall_index)
        self.agents.remove(agent)

    def show_status_message(self, message):
        raise NotImplementedError("Subclasses of BaseGui must override this.")

    def _remove_agent(self, agent):
        """
        Called by BaseGui subclasses to handle agent removal in GUI.
        :param agent: An instance of BaseGuiAgent
        """
        raise NotImplementedError("Subclasses of BaseGui must override this.")

    def update_overall_config_stuff(self):
        raise NotImplementedError("Subclasses of BaseGui must override this.")

    @staticmethod
    def main():
        raise NotImplementedError("Subclasses of BaseGui must override this.")
