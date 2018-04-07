import os
from PyQt5.QtCore import QTimer

from RLBotFramework.gui.index_manager import IndexManager
from RLBotFramework.gui.base_gui_agent import BaseGuiAgent
from RLBotFramework.parsing.rlbot_config_parser import create_bot_config_layout, get_num_players
from RLBotFramework.gui.presets import LoadoutPreset, AgentPreset


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
        self.agent_class.overall_config = overall_config

        self.index_manager = self.index_manager_class(10)
        self.loadout_presets = {}
        self.agent_presets = {}

        self.load_cfg("rlbot.cfg")

        self.agents = []
        self.load_agents()

    def load_cfg(self, config_path):
        if self.overall_config is None:
            self.overall_config = create_bot_config_layout()
        self.overall_config.parse_file(config_path, 10)
        self.agent_class.overall_config = self.overall_config

    def save_overall_config(self):
        def save():
            if not os.path.exists(self.overall_config_path):
                return
            with open(self.overall_config_path, "w") as f:
                f.write(str(self.overall_config))
        if self.overall_config_timer is None:
            self.overall_config_timer = QTimer()
            self.overall_config_timer.timeout.connect(save)
        self.overall_config_timer.start(5)  # Time-out for timer over here

    def load_agents(self, config_file=None):
        """
        Loads all agents for this team from the rlbot.cfg
        :param config_file:  A config file that is similar to rlbot.cfg
        """
        if config_file is not None:
            self.overall_config = config_file
        num_participants = get_num_players(self.overall_config)
        for i in range(num_participants):
            agent = self.add_agent(overall_index=i)
            loadout_preset = self.add_loadout_preset(agent.get_agent_config_path())
            agent.loadout_preset = loadout_preset.get_name()
            agent_preset = self.add_agent_preset(agent.get_agent_config_path())
            agent.agent_preset = agent_preset.get_name()

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
        agent = self.agent_class(overall_index=overall_index, team_i=team_index)
        self.agents.append(agent)
        return agent

    def add_loadout_preset(self, file_path):
        preset = LoadoutPreset(file_path)
        print(preset.get_name())
        self.loadout_presets[preset.get_name()] = preset
        return preset

    def add_agent_preset(self, file_path):
        preset = AgentPreset(file_path)
        preset_name = os.path.basename(file_path)
        self.agent_presets[preset_name] = preset
        return preset

    def remove_agent(self, agent):
        """
        Removes the given agent from this team frame.
        :param agent: An instance of BaseAgentFrame
        """
        self.index_manager.free_index(agent.overall_index)
        self.agents.remove(agent)
        agent.remove()

    def _remove_agent(self, agent):
        """
        Called by BaseGui subclasses to handle agent removal in GUI.
        :param agent: An instance of BaseGuiAgent
        """
        raise NotImplementedError('Subclasses of BaseGui must override this.')

    @staticmethod
    def main():
        raise NotImplementedError('Subclasses of BaseGui must override this.')