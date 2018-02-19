import os
import importlib
import inspect
import tkinter as tk
from tkinter import ttk

from agents.base_agent import BaseAgent
from gui.agent_frames.base_agent_frame import BaseAgentFrame
from gui.custom_agent_frame import CustomAgentFrame
from gui.utils import get_file, get_base_repo_path


class AgentFrame(BaseAgentFrame):
    bot_config = None
    agent_class = None
    config_options_path = {}

    looks_widgets = None
    is_bot_widgets = None
    rlbot_controlled_widgets = None
    bot_level_widgets = None
    agent_path_widgets = None
    agent_config_widgets = None
    custom_agent_options = None
    custom_agent_frame = None

    def __init__(self, parent, team_index, *args, **kwargs):
        super().__init__(parent, team_index, *args, **kwargs)
        self.agent_path = tk.StringVar()
        self.looks_path = tk.StringVar()
        self.is_bot = tk.BooleanVar()
        self.rlbot_controlled = tk.BooleanVar()
        self.bot_level = tk.StringVar(value="All-Star")

    def initialise_widgets(self):
        self.looks_widgets = list()  # row 0
        self.looks_widgets.append(ttk.Label(self, text="Loadout path:", anchor="e"))
        self.looks_widgets.append(ttk.Entry(self, textvariable=self.looks_path, state="readonly", takefocus=False))
        self.looks_widgets.append(ttk.Button(self, text="Select file", command=self.change_looks_path))

        # rlbot.cfg options
        self.is_bot_widgets = list()  # row 1
        self.is_bot_widgets.append(ttk.Label(self, text="Is bot: ", anchor="e"))
        self.is_bot_widgets.append(
            ttk.Combobox(self, textvariable=self.is_bot, values=(True, False), state="readonly"))
        self.is_bot_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_is_bot())
        self.is_bot_widgets[1].current(0)

        self.rlbot_controlled_widgets = list()  # row 2
        self.rlbot_controlled_widgets.append(ttk.Label(self, text="RLBot controlled: ", anchor="e"))
        self.rlbot_controlled_widgets.append(
            ttk.Combobox(self, textvariable=self.rlbot_controlled, values=(True, False), state="readonly"))
        self.rlbot_controlled_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_rlbot_controlled())
        self.rlbot_controlled_widgets[1].current(1)

        self.bot_level_widgets = list()
        self.bot_level_widgets.append(ttk.Label(self, text="Bot level: ", anchor="e"))
        self.bot_level_widgets.append(ttk.Combobox(self, textvariable=self.bot_level, state="readonly",
                                                   values=("Rookie", "Pro", "All-Star")))
        # Agent path
        self.agent_path_widgets = list()  # row 4
        self.agent_path_widgets.append(ttk.Label(self, text="Agent path: ", anchor="e"))
        self.agent_path_widgets.append(
            ttk.Entry(self, textvariable=self.agent_path, state="readonly", takefocus=False))
        self.agent_path_widgets.append(
            ttk.Button(self, text="Select file", command=self.change_bot_path))

        # Agent config
        self.agent_config_widgets = list()  # row 5
        self.agent_config_widgets.append(ttk.Label(self, text="Bot Parameters: ", anchor="e"))
        self.agent_config_widgets.append(ttk.Combobox(self, state="readonly"))
        self.agent_config_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_config())
        self.agent_config_widgets.append(
            ttk.Button(self, text="Add config", command=self.add_config_option, state="disabled"))

        self.custom_agent_options = tk.Frame(self, borderwidth=2, relief=tk.SUNKEN)  # row 7
        ttk.Button(self, text="Remove", command=lambda: self.parent.master.remove_agent(self)).grid(row=8, column=2)
        ttk.Button(self, text="Edit Config", command=self.popup_custom_config).grid(row=8, column=0)

        self.grid_items(0, 0, self.looks_widgets, self.is_bot_widgets)
        self.change_is_bot()
        self.change_rlbot_controlled()

    def popup_custom_config(self):
        """Popups a window to edit all config options of the bot"""
        new_window = tk.Toplevel()
        new_window.title(self.agent_class[0] if self.agent_class is not None else 'BaseAgent')
        custom_agent_frame = CustomAgentFrame(new_window, self.agent_class, self.config_object)
        self.config_object = custom_agent_frame.initialise_custom_config()
        custom_agent_frame.pack()

    def add_config_option(self):
        """Popup, ask for an extra config option and add it to the combobox"""
        config_path = get_file(
            filetypes=[("Config File", "*.cfg")],
            title="Choose a file.")
        if config_path:
            config_name = os.path.splitext(os.path.basename(os.path.realpath(config_path)))[0]
            self.config_options_path[config_name] = config_path
            self.agent_config_widgets[1]['values'] += (config_name,)
            self.agent_config_widgets[1].set(config_name)
            self.change_config()

    def change_config(self):
        """Handle ComboboxSelected Event and show/hide the Custom Frame."""
        config_name = self.agent_config_widgets[1].get()
        if config_name == "custom":
            if not self.custom_agent_options.winfo_ismapped():
                self.custom_agent_options.grid(row=6, column=0, columnspan=3, sticky="nsew")
        else:
            if self.custom_agent_options.winfo_ismapped():
                self.custom_agent_options.grid_forget()

    def change_is_bot(self, hide=False):
        """Hide or show the widgets which have to do with the is_bot value."""
        if self.is_bot.get() and not hide:
            if self.rlbot_controlled_widgets[0].winfo_ismapped():
                return
            self.grid_items(2, 0, self.rlbot_controlled_widgets)
            self.change_rlbot_controlled()
        else:
            if not self.rlbot_controlled_widgets[0].winfo_ismapped():
                return
            for widget in self.grid_slaves(row=2):
                widget.grid_forget()
            self.change_rlbot_controlled(hide=True)

    def change_bot_path(self):
        """Popup, ask for a new agent path and apply that path."""
        agent_file_path = get_file(
            filetypes=[("Python File", "*.py")],
            title="Choose a file")
        if agent_file_path:
            self.agent_path.set(agent_file_path)
            self.agent_config_widgets[2]["state"] = "normal"
            self.agent_config_widgets[1]['values'] = ("custom",)
            self.agent_config_widgets[1].set("custom")
            agent_path = self.agent_path.get()
            original_path = get_base_repo_path().replace(os.sep, "/")
            print(agent_path)
            print(original_path)
            module = self.agent_path.get().replace(original_path, "", 1).replace("/", ".")[1:-3]
            print('module', module)
            agent_package = importlib.import_module(module)
            agent_class = [m for m in inspect.getmembers(agent_package, inspect.isclass) if
                               m[1].__module__ == module]
            if len(agent_class) > 1:
                popup = tk.Toplevel()
                popup.title("Choose agent class")
                popup.transient(self)
                popup.grab_set()
                popup.protocol("WM_DELETE_WINDOW", lambda: None)
                selected = tk.IntVar()
                tk.Label(popup, text="Select the class and press continue").grid(row=0, column=0, columnspan=2,
                                                                                 padx=(10, 10), pady=(10, 5))
                for i in range(len(agent_class)):
                    ttk.Radiobutton(popup, text=agent_class[i][0], value=i, variable=selected).grid(
                        row=i + 1, column=0, sticky="nsew", padx=(10, 0))
                selected.set(0)

                def chosen_class():
                    self.agent_class = agent_class[selected.get()]
                    popup.destroy()

                ttk.Button(popup, text="Continue", command=chosen_class).grid(row=len(agent_class), column=1,
                                                                              padx=(0, 10), pady=(0, 10))
                self.wait_window(popup)
            else:
                self.agent_class = agent_class[0]
            self.change_config()

    def change_looks_path(self):
        """Popup, ask for the loadout config and apply that path."""
        config_path = get_file(
            filetypes=[("Config File", "*.cfg")],
            title="Choose a file")
        if config_path:
            self.looks_path.set(config_path)

    def change_rlbot_controlled(self, hide=False):
        """Hide or show the widgets which have to do with the rlbot_controlled value."""
        if hide:
            for i in [3, 4, 5, 6]:
                for widget in self.grid_slaves(row=i):
                    widget.grid_forget()
            return
        if self.rlbot_controlled.get():
            if self.rlbot_controlled_widgets[0].winfo_ismapped():
                for widget in self.grid_slaves(row=3):
                    widget.grid_forget()
            self.grid_items(4, 0, self.agent_path_widgets, self.agent_config_widgets)
            self.custom_agent_options.grid(row=6, column=0, columnspan=3, sticky="nsew")
        else:
            for i in [4, 5, 6]:
                for widget in self.grid_slaves(row=i):
                    widget.grid_forget()
            self.grid_items(3, 0, self.bot_level_widgets)

    def check_for_settings(self):
        """Return list with items missing, if nothing an empty list."""
        missing = list()
        if not self.looks_path.get():
            missing.append("Loadout Path")
        if self.rlbot_controlled.get():
            if not self.agent_path.get():
                missing.append("Agent Path")
        return missing

    @staticmethod
    def grid_items(start_row=0, start_index=0, *widgets):
        """Grid all items found in WIDGETS starting in row START_ROW from index START_INDEX"""
        for row, widget_list in enumerate(widgets):
            row += start_row
            for column, widget in enumerate(widget_list):
                column += start_index
                widget.grid(row=row, column=column, sticky="nsew")

    def load_config(self, config_file, overall_index):
        self.overall_config = config_file
        self.overall_index = overall_index
        pass
