import tkinter as tk
from tkinter import ttk
from utils.rlbot_config_parser import get_num_players, get_team


class BaseTeamFrame(tk.Frame):
    overall_config = None
    agents_frame = None
    add_agent_object = None

    def __init__(self, parent, team_index, agent_index_manager, agent_frame_class,
                 overall_config=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.overall_config = overall_config
        self.team_index = team_index
        self.agent_frame_class = agent_frame_class
        self.index_manager = agent_index_manager

        self.agents = list()

    def is_blue_team(self):
        return self.team_index == 0

    def initialize_team_frame(self):
        self.initialize_agents_frame()
        self.initialize_add_agent()
        if self.overall_config is not None:
            self.load_agents()
        else:
            self.add_agent()

    def initialize_agents_frame(self):
        self.agents_frame = tk.Frame(self)
        self.agents_frame.grid()

    def initialize_add_agent(self):
        self.add_agent_object = ttk.Button(self.get_agents_frame(), text="Add bot", command=self.add_agent)
        self.add_agent_object.grid(row=10, column=0, sticky="se")

    def add_agent(self, overall_index=-1):
        """
        Adds an agent to this frame, creates it too.
        :param overall_index: The index of the bot in the config file if it already exists.
        """
        if overall_index == -1:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.mark_used(overall_index)
        self.agents.append(self.create_agent(overall_index))
        self._place_agent(len(self.agents) - 1)

    def place_add_agent(self):
        if not self.add_agent_object.winfo_ismapped():
            self.add_agent_object.grid(row=10, column=0, sticky="se")

    def _place_agent(self, index):
        """
        Visually places the latest agent in the frame.
        :param index: The index of the agent added.
        """
        self.agents[index].grid(row=self.agents[index].overall_index, column=0, sticky="e")

    def remove_agent(self, agent):
        """
        Removes the given agent from this team frame.
        :param agent: An instance of BaseAgentFrame
        """
        agent.destroy()
        self.index_manager.free_index(agent.overall_index)
        self.agents.remove(agent)
        if len(self.agents) == 0:
            self.add_agent()
        if len(self.agents) < 5:
            self.place_add_agent()

    def remove_add_agent(self):
        if self.add_agent_object.winfo_ismapped():
            self.add_agent_object.grid_forget()

    def get_agents_frame(self):
        return self.agents_frame

    def create_agent(self, overall_index):
        """
        Creates a new agent frame, loads config data if needed.
        :param overall_index: An optional value if the overall index of this agent is already specified.
        :return: an instance of BaseAgentFrame
        """
        agent = self.agent_frame_class(self.get_agents_frame(), self.team_index)
        agent.overall_index = overall_index
        agent.initialize_widgets()
        agent.load_config(self.overall_config, overall_index)
        agent.refresh_widgets()
        return agent

    def load_agents(self, config_file=None):
        """
        Loads all agents for this team from the rlbot.cfg
        :param config_file:  A config file that is similar to rlbot.cfg
        """
        if config_file is not None:
            self.overall_config = config_file
        num_participants = get_num_players(self.overall_config)
        for i in range(num_participants):
            team_index = get_team(self.overall_config, i)
            if team_index == self.team_index:
                self.add_agent(overall_index=i)

    def get_configs(self):
        configs = {}
        for agent in self.agents:
            index, config = agent.get_config()
            configs[index] = config
        return configs
