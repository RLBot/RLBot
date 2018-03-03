import tkinter as tk

import os

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

    def load_agent_config(self, agent_class=None):
        """
        Loads the config specific to the agent.
        This only happens if the frame is for a custom agent otherwise this method is skipped
        :param agent_class: If passed in and there is not a config file this agent is used.
        :return:
        """
        if self.is_participant_bot() and self.is_participant_custom_bot():
            agent_config_path = self.get_agent_config_path()
            base_agent_config = BaseAgent.create_agent_configurations()
            if agent_config_path is None:
                if agent_class is not None:
                    self.agent_class = agent_class
                    self.agent_config = self.agent_class.create_agent_configurations()
                else:
                    self.agent_config = base_agent_config
            else:
                base_agent_config.parse_file(agent_config_path)
                bot_module = base_agent_config.get(BOT_CONFIG_MODULE_HEADER, AGENT_MODULE_KEY)
                base_import = get_base_import_package(os.path.dirname(agent_config_path))
                self.agent_class = import_agent(base_import + '.' + bot_module)
                self.agent_config = self.agent_class.create_agent_configurations()
                self.agent_config.parse_file(agent_config_path)

    def load_config(self, overall_config_file, overall_index):
        """Loads the config data into the agent"""
        self.overall_config = overall_config_file
        self.overall_index = overall_index
        self.load_agent_config()
        self.link_variables()

    def load_agent_from_path(self, agent_file_path):
        module = get_base_import_package(agent_file_path)
        self.agent_class = import_agent(module)

    def link_variables(self):
        pass

    def get_config(self):
        return self.overall_index, self.agent_config
