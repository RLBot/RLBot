import tkinter as tk
from tkinter import ttk

from configparser import RawConfigParser
import os

from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY, LOADOUT_MODULE_KEY
from RLBotFramework.utils.class_importer import import_agent, get_base_import_package
from RLBotFramework.utils.rlbot_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY,\
    PARTICIPANT_TYPE_KEY, PARTICIPANT_BOT_SKILL_KEY


class BaseAgentFrame(tk.Frame):

    config_object = None  # The config that is
    overall_config = None  # The config that is shared by all agent frames.
    overall_index = -1  # The index that grabs data from the overall_config
    team_index = -1  # The index representing what team the agent belongs to.
    parent = None  # The parent frame
    agent_config_path = None  # The config path for the agent config file
    agent_class = None  # The class for the agent
    agent_config = None
    looks_config = None

    def __init__(self, parent, team_index, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.team_index = team_index
        self.parent = parent

    def initialize_widgets(self):
        pass

    def refresh_widgets(self):
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

    def get_participant_type(self):
        return self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TYPE_KEY, self.overall_index)

    def set_participant_type(self, participant_type):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TYPE_KEY,
                                             participant_type, self.overall_index)

    def get_bot_skill(self):
        return self.overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY, self.overall_index)

    def set_bot_skill(self, bot_skill):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                             bot_skill, self.overall_index)

    def load_agent_configs(self, agent_class=None):
        """
        Loads the config specific to the agent.
        This only happens if the frame is for a custom agent otherwise this method is skipped
        :param agent_class: If passed in and there is not a config file this agent is used.
        :return:
        """
        config_path = self.get_agent_config_path()
        agent_cfg = RawConfigParser()
        agent_cfg.read(config_path)
        bot_module = agent_cfg.get(BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY)
        self.agent_class = import_agent(bot_module)
        self.agent_config = self.agent_class.create_agent_configurations()
        self.agent_config.parse_file(agent_cfg)

        looks_path = agent_cfg.get(BOT_CONFIG_MODULE_HEADER, LOADOUT_MODULE_KEY)
        self.looks_config = BaseAgent.create_looks_configurations()
        self.looks_config.parse_file(looks_path)

    def load_config(self, overall_config_file, overall_index):
        """Loads the config data into the agent"""
        self.overall_config = overall_config_file
        self.overall_index = overall_index
        self.load_agent_configs()

    def load_agent_from_path(self, agent_file_path):
        module = get_base_import_package(agent_file_path)
        self.agent_class = import_agent(module)

    def link_variables(self):
        pass

    def get_config(self):
        return self.overall_index, self.agent_config, self.looks_config

    @staticmethod
    def transfer_config_value(config_value, tkinter_var, index=None):
        tkinter_var.set(config_value.get_value(index))
        config_value.set_value(tkinter_var, index)

    @staticmethod
    def grid_custom_options_header(header_frame, header, exceptions=None, row_offset=0, column_offset=0):
        for parameter_index, (parameter_name, parameter) in enumerate(header.values.items()):
            if exceptions is not None and parameter_name in exceptions:
                continue

            ttk.Label(header_frame, text=parameter_name + ":", anchor='e').grid(
                row=parameter_index + row_offset, column=0 + column_offset, sticky="ew")
            big = 20000000
            if parameter.type == int:
                if parameter.value is None:
                    parameter.value = tk.IntVar(value=parameter.default)
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.IntVar(value=parameter.value)
                widget = tk.Spinbox(header_frame, textvariable=parameter.value, from_=0, to=big)
            elif parameter.type == float:
                if parameter.value is None:
                    parameter.value = tk.DoubleVar(value=parameter.default)
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.DoubleVar(value=parameter.value)
                widget = tk.Spinbox(header_frame, textvariable=parameter.value, from_=0, to=big,
                                    increment=.001)
            elif parameter.type == bool:
                if parameter.value is None:
                    parameter.value = tk.BooleanVar()
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.BooleanVar(value=parameter.value)
                widget = ttk.Combobox(header_frame, textvariable=parameter.value, values=(False, True),
                                      state="readonly")
                widget.current(parameter.default)
            elif parameter.type == str:
                if parameter.value is None:
                    parameter.value = tk.StringVar(value=parameter.default)
                elif not isinstance(parameter.value, tk.Variable):
                    parameter.value = tk.StringVar(value=parameter.value)
                widget = ttk.Entry(header_frame, textvariable=parameter.value)
            else:
                widget = ttk.Label("Unknown type")

            widget.grid(row=parameter_index + row_offset, column=1 + column_offset, sticky="ew")
