import tkinter as tk
from tkinter import ttk

from gui.agent_frames.base_agent_frame import BaseAgentFrame
from gui.custom_agent_frame import CustomAgentFrame
from gui.utils import get_file


class AgentFrame(BaseAgentFrame):
    bot_config = None
    config_options_path = {}

    agent_config_path_widgets = None
    is_bot_widgets = None
    rlbot_controlled_widgets = None
    bot_level_widgets = None
    agent_path_widgets = None
    custom_agent_options = None
    custom_agent_frame = None

    def __init__(self, parent, team_index, *args, **kwargs):
        super().__init__(parent, team_index, *args, **kwargs)
        self.agent_path = tk.StringVar()
        self.agent_config_path = tk.StringVar()
        self.is_bot = tk.BooleanVar()
        self.rlbot_controlled = tk.BooleanVar()
        self.bot_level = tk.StringVar(value="All-Star")

    def initialise_widgets(self):
        # Agent config
        self.agent_config_path_widgets = list()  # row 0
        self.agent_config_path_widgets.append(ttk.Label(self, text="Config path:", anchor="e"))
        self.agent_config_path_widgets.append(ttk.Entry(self, textvariable=self.agent_config_path, state="readonly", takefocus=False))
        self.agent_config_path_widgets.append(ttk.Button(self, text="Select file",
                                                         command=self.change_agent_config_path))

        # rlbot.cfg options
        self.is_bot_widgets = list()  # row 1
        self.is_bot_widgets.append(ttk.Label(self, text="Is bot: ", anchor="e"))
        self.is_bot_widgets.append(
            ttk.Combobox(self, textvariable=self.is_bot, values=(False, True), state="readonly"))
        self.is_bot_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_is_bot())
        self.is_bot_widgets[1].current(1)

        self.rlbot_controlled_widgets = list()  # row 2
        self.rlbot_controlled_widgets.append(ttk.Label(self, text="RLBot controlled: ", anchor="e"))
        self.rlbot_controlled_widgets.append(
            ttk.Combobox(self, textvariable=self.rlbot_controlled, values=(False, True), state="readonly"))
        self.rlbot_controlled_widgets[1].bind("<<ComboboxSelected>>", lambda e: self.change_rlbot_controlled())
        self.rlbot_controlled_widgets[1].current(0)

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

        self.custom_agent_options = tk.Frame(self, borderwidth=2, relief=tk.SUNKEN)  # row 7
        ttk.Button(self, text="Remove", command=lambda: self.parent.master.remove_agent(self)).grid(row=8, column=2)
        ttk.Button(self, text="Edit Config", command=self.popup_custom_config).grid(row=8, column=0)

        self.grid_items(0, 0, self.agent_config_path_widgets, self.is_bot_widgets)
        self.change_is_bot()
        self.change_rlbot_controlled()

    def popup_custom_config(self):
        """Popups a window to edit all config options of the bot"""
        new_window = tk.Toplevel()
        new_window.title(self.agent_class[0] if self.agent_class is not None else 'BaseAgent')
        custom_agent_frame = CustomAgentFrame(new_window, self.agent_class, self.config_object)
        self.config_object = custom_agent_frame.initialise_custom_config()
        custom_agent_frame.pack()

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
            self.load_agent_from_path(agent_file_path)
            self.load_agent_config(self.agent_class)

    def change_agent_config_path(self):
        """Popup, ask for the config and apply that path."""
        config_path = get_file(
            filetypes=[("Config File", "*.cfg")],
            title="Choose a file")
        if config_path:
            self.agent_config_path.set(config_path)
            self.set_agent_config_path(config_path)
            self.load_agent_config()

    def change_rlbot_controlled(self, hide=False):
        """Hide or show the widgets which have to do with the rlbot_controlled value."""
        if hide:
            for i in [3, 4, 5, 6]:
                for widget in self.grid_slaves(row=i):
                    widget.grid_forget()
            return
        if self.rlbot_controlled.get():
            for widget in self.grid_slaves(row=3):
                widget.grid_forget()
            self.grid_items(4, 0, self.agent_path_widgets)
            self.custom_agent_options.grid(row=6, column=0, columnspan=3, sticky="nsew")
        else:
            for i in [4, 5, 6]:
                for widget in self.grid_slaves(row=i):
                    widget.grid_forget()
            self.grid_items(3, 0, self.bot_level_widgets)

    def check_for_settings(self):
        """Return list with items missing, if nothing an empty list."""
        missing = list()
        if not self.agent_config_path.get():
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
        super().load_config(config_file, overall_index)
        self.agent_config_path.set(self.get_agent_config_path())
        self.is_bot_widgets[1].current(self.is_participant_bot())
        self.rlbot_controlled_widgets[1].current(self.is_participant_custom_bot())
        level = self.get_bot_skill()
        bot_level = 0 if level <= .25 else 1 if level <= .75 else 2
        self.bot_level_widgets[1].current(bot_level)
        self.change_is_bot()
        self.change_rlbot_controlled()
        self.agent_path.set(self.agent_class.__name__)
