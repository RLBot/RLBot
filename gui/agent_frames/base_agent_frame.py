import importlib
import inspect
import tkinter as tk

import os
from tkinter import ttk

from agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY
from utils.agent_creator import import_agent, get_base_import_package
from utils.rlbot_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, PARTICIPANT_BOT_KEY, \
    PARTICIPANT_RLBOT_KEY, PARTICIPANT_BOT_SKILL_KEY


class BaseAgentFrame(tk.Frame):

    config_object = None  # The config that is
    overall_config = None  # The config that is shared by all agent frames.
    overall_index = -1  # The index that grabs data from the overall_config
    team_index = -1  # The index representing what team the agent belongs to.
    parent = None  # The parent frame
    agent_config_path = None  # The config path for the agent config file
    agent_class = None  # The class for the agent
    agent_config = None

    def __init__(self, parent, team_index, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.team_index = team_index
        self.parent = parent

    def initialise_widgets(self):
        pass

    @staticmethod
    def grid_items(start_row=0, start_index=0, *widgets):
        """Grid all items found in WIDGETS starting in row START_ROW from index START_INDEX"""
        for row, widget_list in enumerate(widgets):
            row += start_row
            for column, widget in enumerate(widget_list):
                column += start_index
                widget.grid(row=row, column=column, sticky="nsew")

    def get_agent_config_path(self):
        return os.path.realpath(self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER,
                                                        PARTICIPANT_CONFIG_KEY, self.overall_index))

    def set_agent_config_path(self, config_path):
        self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY,
                                      config_path, self.overall_index)

    def is_participant_bot(self):
        return self.overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_KEY, self.overall_index)

    def set_is_participant_bot(self, is_bot):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_KEY,
                                             is_bot, self.overall_index)

    def is_participant_custom_bot(self):
        return self.overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_RLBOT_KEY, self.overall_index)

    def set_is_participant_custom_bot(self, is_rlbot):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_RLBOT_KEY,
                                             is_rlbot, self.overall_index)

    def get_bot_skill(self):
        return self.overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY, self.overall_index)

    def set_bot_skill(self, bot_skill):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                             bot_skill, self.overall_index)

    def load_agent_config(self):
        if self.is_participant_bot() and self.is_participant_custom_bot():
            agent_config_path = self.get_agent_config_path()
            base_agent_config = BaseAgent.create_agent_configurations()
            if agent_config_path is None:
                self.agent_config = base_agent_config
                return

            base_agent_config.parse_file(agent_config_path)
            bot_module = base_agent_config.get(BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY)
            base_import = get_base_import_package(os.path.dirname(agent_config_path))
            self.agent_class = import_agent(base_import + '.' + bot_module)
            self.agent_config = self.agent_class.create_agent_configurations()
            self.agent_config.parse_file(agent_config_path)

    def load_config(self, overall_config_file, overall_index):
        self.overall_config = overall_config_file
        self.overall_index = overall_index
        self.load_agent_config()

    def load_agent_from_path(self, agent_file_path):
        module = get_base_import_package(agent_file_path)
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
