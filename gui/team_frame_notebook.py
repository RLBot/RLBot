import tkinter as tk
from tkinter import ttk

from gui.agent_frame import AgentFrame
from utils.rlbot_config_parser import get_num_players, get_team


class TeamFrame(tk.Frame):
    def __init__(self, parent, team_index, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.team_index = team_index

        self.agents_frame = ttk.Notebook(self)
        self.agents_frame.bind("<<NotebookTabChanged>>", lambda event: self.switch_tab())
        self.add_agent_frame = tk.Frame(self.agents_frame)
        self.agents_frame.add(self.add_agent_frame, text="  +  ")

        self.agents = list()
        self.add_agent(0)

        self.agents_frame.pack(side="top", fill="both")

    def is_blue_team(self):
        return self.team_index == 0

    def switch_tab(self):
        """Handle tab switch to add an agent if switched to Add Agent tab"""
        if self.agents_frame.tab(self.agents_frame.index("current"), option="text") == "  +  ":
            self.add_agent(self.agents_frame.index("current"))

    def update_tabs(self):
        team_name = "Blue" if self.is_blue_team() else "Orange"
        for i, widget in reversed(list(enumerate(self.agents_frame.tabs()))):
            label = self.agents_frame.tab(widget, option="text")
            if not label.endswith(str(i + 1)) and label != "  +  ":
                self.agents_frame.tab(widget, text=team_name + " Bot " + str(i + 1))

    def add_agent(self, index, config_file=None, overall_index=-1):
        """Add an agent to the according team."""
        color = "Blue" if self.is_blue_team() else "Orange"
        self.agents.append(self.create_agent(self.agents_frame, self.is_blue_team()))
        self.agents_frame.insert(index, self.agents[index], text=color + " Bot " + str(index + 1))
        if len(self.agents) > 4:
            self.agents_frame.hide(self.add_agent_frame)
        self.agents_frame.select(index)

    def remove_agent(self, agent):
        """Remove agent AGENT from the list and Notebook"""
        self.agents_frame.hide(self.add_agent_frame)
        agent.destroy()
        self.agents.remove(agent)
        if len(self.agents) == 0:
            self.add_agent(0)
        self.agents_frame.add(self.add_agent_frame)
        self.update_tabs()

    def create_agent(self, config_file=None, overall_index=-1):
        agent = AgentFrame(self.agents_frame, self.team_index)
        if config_file is not None:
            agent.load_config(config_file, overall_index)
        return agent

    def load_agents(self, config_file):
        num_participants = get_num_players(config_file)
        agent_count = 0
        for i in range(num_participants):
            team_index = get_team(config_file, i)
            if team_index == self.team_index:
                self.add_agent(agent_count, config_file=config_file, overall_index=i)
                agent_count += 1


if __name__ == '__main__':
    root = tk.Tk()
    runner = TeamFrame(root, True)
    runner.pack(side="top", fill="both", expand=True)
    root.mainloop()
