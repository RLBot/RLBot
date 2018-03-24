import os
import tkinter as tk
from tkinter import ttk

from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, LOOKS_CONFIG_KEY
from RLBotFramework.utils.class_importer import import_agent
from RLBotFramework.utils.rlbot_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, \
    PARTICIPANT_BOT_KEY, PARTICIPANT_RLBOT_KEY, PARTICIPANT_BOT_SKILL_KEY, get_bot_config_bundle, BotConfigBundle


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
    config_bundle = None

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

    def load_agent_configs(self):
        """
        Loads the config specific to the agent.
        This only happens if the frame is for a custom agent otherwise this method is skipped
        :param agent_class: If passed in and there is not a config file this agent is used.
        :return:
        """

        config_bundle = get_bot_config_bundle(self.get_agent_config_path())
        python_file = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY)
        self.agent_class = import_agent(python_file).get_loaded_class()

        self.agent_config = self.agent_class.create_agent_configurations()
        self.agent_config.parse_file(config_bundle.config_obj)
        self.config_bundle = BotConfigBundle(config_bundle.config_directory, self.agent_config)

        looks_path = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
        self.looks_config = BaseAgent.create_looks_configurations()
        self.looks_config.parse_file(looks_path)

    def load_config(self, overall_config_file, overall_index):
        """Loads the config data into the agent"""
        self.overall_config = overall_config_file
        self.overall_index = overall_index
        self.load_agent_configs()
        self.load_fields_from_config()

    def write_fields_to_config(self):
        pass

    def load_fields_from_config(self):
        pass

    def get_config(self):
        self.write_fields_to_config()
        return self.overall_index, self.config_bundle, self.looks_config

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
