import tkinter as tk
from tkinter import ttk

from gui.agent_frame import AgentFrame


class TeamFrame(tk.Frame):
    def __init__(self, parent, is_blue_team, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.is_blue = is_blue_team

        self.agents_book = ttk.Notebook(self)
        self.agents_book.bind("<<NotebookTabChanged>>", lambda event: self.switch_tab())
        self.add_agent_frame = tk.Frame(self.agents_book)
        self.agents_book.add(self.add_agent_frame, text="  +  ")

        self.agents = list()
        self.add_agent(0)

        self.agents_book.pack(side="top", fill="both")

    def switch_tab(self):
        """Handle tab switch to add an agent if switched to Add Agent tab"""
        if self.agents_book.tab(self.agents_book.index("current"), option="text") == "  +  ":
            self.add_agent(self.agents_book.index("current"))

    def update_tabs(self):
        color = "Blue" if self.is_blue else "Orange"
        for i, widget in reversed(list(enumerate(self.agents_book.tabs()))):
            label = self.agents_book.tab(widget, option="text")
            if not label.endswith(str(i + 1)) and label != "  +  ":
                self.agents_book.tab(widget, text=color + " Bot " + str(i + 1))

    def add_agent(self, index):
        """Add an agent to the according team."""
        color = "Blue" if self.is_blue else "Orange"
        self.agents.append(AgentFrame(self.agents_book, self.is_blue))
        self.agents_book.insert(index, self.agents[index], text=color + " Bot " + str(index + 1))
        if len(self.agents) > 4:
            self.agents_book.hide(self.add_agent_frame)
        self.agents_book.select(index)

    def remove_agent(self, agent):
        """Remove agent AGENT from the list and Notebook"""
        self.agents_book.hide(self.add_agent_frame)
        agent.destroy()
        self.agents.remove(agent)
        if len(self.agents) == 0:
            self.add_agent(0)
        self.agents_book.add(self.add_agent_frame)
        self.update_tabs()

    def load_agents(self, config_file):

if __name__ == '__main__':
    root = tk.Tk()
    runner = TeamFrame(root, True)
    runner.pack(side="top", fill="both", expand=True)
    root.mainloop()
