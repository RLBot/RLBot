# from RLBotFramework.parsing.agent_config_parser import get_team
from RLBotFramework.parsing.custom_config import ConfigObject
from RLBotFramework.gui.index_manager import IndexManager
from RLBotFramework.gui.base_gui_agent import BaseGuiAgent
from RLBotFramework.parsing.rlbot_config_parser import create_bot_config_layout, get_num_players


class BaseGui:
    overall_config = None
    agents_frame = None
    add_agent_object = None

    index_manager = IndexManager
    agent_class = BaseGuiAgent

    def __init__(self, overall_config=None):
        self.overall_config = overall_config
        self.agent_class.overall_config = overall_config

        self.index_manager = self.index_manager(10)

        self.gui_config = self.create_gui_config()
        self.latest_save_path = self.gui_config.get("GUI Configuration", "latest_save_path")
        self.load_cfg(self.latest_save_path)

        self.agents = []
        self.load_agents()

    def load_cfg(self, config_path, teams=False, match_settings=False):
        if self.overall_config is None:
            self.overall_config = create_bot_config_layout()
        self.overall_config.parse_file(config_path, 10)
        if teams:
            self.index_manager.numbers = set()
            self.team1.load_agents(self.overall_config)
            self.team2.load_agents(self.overall_config)
        if match_settings:
            self.match_settings.load_match_settings(self.overall_config)
        self.agent_class.overall_config = self.overall_config

    def load_agents(self, config_file=None):
        """
        Loads all agents for this team from the rlbot.cfg
        :param config_file:  A config file that is similar to rlbot.cfg
        """
        if config_file is not None:
            self.overall_config = config_file
        num_participants = get_num_players(self.overall_config)
        for i in range(num_participants):
            self.add_agent(overall_index=i)

    def add_agent(self, overall_index=None):
        """
        Creates the agent using self.agent_class and adds it to the index manager.
        :param overall_index: The index of the bot in the config file if it already exists.
        """
        if not self.index_manager.has_free_slots():
            return
        if overall_index is None:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.use_index(overall_index)
        agent = self.agent_class(overall_index)
        self._add_agent(agent)
        self.agents.append(agent)

    def _add_agent(self, agent):
        """
        Called by BaseGui subclasses to handle agent creation in GUI.
        :param agent:
        :return:
        """
        raise NotImplementedError('Subclasses of BaseGui must override this.')

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
    def create_gui_config():
        config = ConfigObject()
        config.add_header_name("GUI Configuration") \
            .add_value("blue_team_type", str, default="default") \
            .add_value("orange_team_type", str, default="default") \
            .add_value("agent_type", str, default="default") \
            .add_value("latest_save_path", str, default="rlbot.cfg")
        return config


    def main(self):
        raise NotImplementedError('Subclasses of BaseGui must override this.')