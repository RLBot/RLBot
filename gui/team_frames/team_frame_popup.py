import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import os


class TeamFrame(tk.Frame):
    def __init__(self, parent, is_blue_team, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.is_blue = is_blue_team

        self.agents_frame = ttk.Frame(self)
        self.add_agent_frame = tk.Frame(self.agents_frame)

        self.agents = list()
        agent = self.AgentFrame(self.agents_frame, self.is_blue)
        self.agents.append(agent)
        self.agents[0].grid(row=0, column=0)
        self.agents_frame.pack(side="top", fill="both")

    class AgentFrame(tk.Frame):
        name_widgets = list()
        looks_widgets = list()
        bot_type_widgets = list()

        def __init__(self, parent, is_blue_team, *args, **kwargs):
            tk.Frame.__init__(self, parent, *args, *kwargs)
            self.is_blue = is_blue_team
            self.name = tk.StringVar(value="A bot")
            self.looks_path = tk.StringVar()
            self.bot_type = tk.StringVar(value="Psyonix Bot")
            self.initialise_widgets()

        def initialise_widgets(self):
            self.name_widgets.append(ttk.Label(self, text="In-game name: ", anchor="e"))
            self.name_widgets.append(ttk.Entry(self, textvariable=self.name))

            self.looks_widgets.append(ttk.Label(self, text="Appearance path: ", anchor="e"))
            self.looks_widgets.append(ttk.Entry(self, textvariable=self.looks_path, state="readonly", takefocus=False))
            self.looks_widgets.append(ttk.Button(self, text="Select file", command=self.change_looks_path))

            self.bot_type_widgets.append(ttk.Label(self, text="Bot type: ", anchor="e"))
            self.bot_type_widgets.append(ttk.Combobox(self, state="readonly"))
            self.bot_type_widgets[1].bind("<<ComboboxSelected>>", lambda e: print("Test"))
            self.bot_type_widgets.append(
                ttk.Button(self, text="Edit config", command=lambda e: print("test"), state="disabled"))

            self.grid_items(0, 0, self.name_widgets, self.looks_widgets, self.bot_type_widgets)

        def change_looks_path(self):
            """Popup, ask for the loadout config and apply that path."""
            config_path = askopenfilename(
                initialdir=os.path.dirname(os.path.realpath(__file__)),
                filetypes=[("Config File", "*.cfg")],
                title="Choose a file")
            if config_path:
                self.looks_path.set(config_path)

        @staticmethod
        def grid_items(start_row=0, start_index=0, *widgets):
            """Grid all items found in WIDGETS starting in row START_ROW from index START_INDEX"""
            for row, widget_list in enumerate(widgets):
                row += start_row
                for column, widget in enumerate(widget_list):
                    column += start_index
                    widget.grid(row=row, column=column, sticky="nsew")




if __name__ == '__main__':
    root = tk.Tk()
    runner = TeamFrame(root, True)
    runner.pack(side="top", fill="both", expand=True)
    root.mainloop()
