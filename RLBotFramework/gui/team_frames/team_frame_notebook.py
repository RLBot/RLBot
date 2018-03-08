import tkinter as tk
from tkinter import ttk

from RLBotFramework.gui.team_frames.base_team_frame import BaseTeamFrame


class NotebookTeamFrame(BaseTeamFrame):
    add_agent_frame = None

    def __init__(self, parent, overall_config, team_index, agent_frame_class, *args, **kwargs):
        super().__init__(parent, overall_config, team_index, agent_frame_class, *args, *kwargs)

    def get_agents_frame(self):
        return self.agents_frame

    def initialize_agents_frame(self):
        self.agents_frame = ttk.Notebook(self)
        self.agents_frame.bind("<<NotebookTabChanged>>", lambda event: self.switch_tab())

        self.agents_frame.pack(side="top", fill="both")

    def initialize_add_agent(self):
        self.add_agent_frame = tk.Frame(self.agents_frame)
        self.agents_frame.add(self.add_agent_frame, text="  +  ")

    def switch_tab(self):
        """Handle tab switch to add an agent if switched to Add Agent tab"""
        if self.agents_frame.tab(self.agents_frame.index("current"), option="text") == "  +  ":
            self.add_agent()

    def update_tabs(self):
        team_name = "Blue" if self.is_blue_team() else "Orange"
        for i, widget in reversed(list(enumerate(self.agents_frame.tabs()))):
            label = self.agents_frame.tab(widget, option="text")
            if not label.endswith(str(i + 1)) and label != "  +  ":
                self.agents_frame.tab(widget, text=team_name + " Bot " + str(i + 1))

    def place_add_agent(self):
        self.agents_frame.add(self.add_agent_frame, text="  +  ")

    def _place_agent(self, index):
        color = "Blue" if self.is_blue_team() else "Orange"
        self.agents_frame.insert(index, self.agents[index], text=color + " Bot " + str(index + 1))
        self.agents_frame.select(index)

    def remove_agent(self, agent):
        """Remove agent AGENT from the list and Notebook"""
        self.agents_frame.hide(self.add_agent_frame)
        super().remove_agent(agent)
        self.update_tabs()

    def remove_add_agent(self):
        self.agents_frame.hide(self.add_agent_frame)


if __name__ == '__main__':
    from RLBotFramework.gui import AgentFrame
    root = tk.Tk()
    team_frame = NotebookTeamFrame(root, 0, AgentFrame)
    team_frame.pack(side="top", fill="both", expand=True)
    root.mainloop()
