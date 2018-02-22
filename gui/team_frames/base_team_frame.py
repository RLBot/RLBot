import tkinter as tk
from tkinter import ttk
from utils.rlbot_config_parser import get_num_players, get_team


class BaseTeamFrame(tk.Frame):
    overall_config = None

    def __init__(self, parent, team_index, agent_index_manager, agent_frame_class,
                 overall_config=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.overall_config = overall_config
        self.team_index = team_index
        self.agent_frame_class = agent_frame_class
        self.index_manager = agent_index_manager

        self.agents_frame = tk.Frame(self)
        self.agents_frame.pack(side="top", fill="both")
        self.agents = list()
        self.initialise_add_agent()
        if overall_config is not None:
            self.load_agents()
        else:
            self.add_agent(0)

    def is_blue_team(self):
        return self.team_index == 0

    def initialise_add_agent(self):
        ttk.Button(self.get_agents_frame(), text="Add bot", command=lambda: self.add_agent()).grid(
            row=5, column=0, sticky="se")

    def add_agent(self, overall_index=-1):
        self.agents.append(self.create_agent(overall_index))
        index = len(self.agents) - 1
        self.agents[index].grid(row=index, column=0)

    def remove_agent(self, agent):
        agent.destroy()
        self.agents.remove(agent)
        if len(self.agents) == 0:
            self.add_agent(0)

    def get_agents_frame(self):
        return self.agents_frame

    def create_agent(self, overall_index=-1):
        agent = self.agent_frame_class(self.get_agents_frame(), self.team_index)
        if overall_index == -1:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.mark_used(overall_index)
        agent.initialise_widgets()
        agent.load_config(self.overall_config, overall_index)
        return agent

    def load_agents(self, config_file=None):
        if config_file is not None:
            self.overall_config = config_file
        num_participants = get_num_players(self.overall_config)
        for i in range(num_participants):
            team_index = get_team(self.overall_config, i)
            if team_index == self.team_index:
                self.add_agent(overall_index=i)
