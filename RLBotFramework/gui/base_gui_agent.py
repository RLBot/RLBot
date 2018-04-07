import os
from PyQt5.QtCore import QTimer
from RLBotFramework.utils.class_importer import import_agent
from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, LOOKS_CONFIG_KEY
from RLBotFramework.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, \
    PARTICIPANT_BOT_SKILL_KEY, PARTICIPANT_TYPE_KEY, PARTICIPANT_TEAM, get_bot_config_bundle, BotConfigBundle


class BaseGuiAgent:
    config_object = None  # The config that is
    overall_config = None  # The config that is shared by all agent frames.
    config_bundle = None

    def __init__(self, overall_index, team_i=None):
        """
        Creates a new agent frame, loads config data if needed.
        :param overall_index: An optional value if the overall index of this agent is already specified.
        :return: an instance of BaseAgentFrame
        """
        self.overall_index = overall_index
        self.load_config(self.overall_config, overall_index)

        self.agent_config_path = None
        self.loadout_config_path = None
        self.loadout_preset = ""
        self.agent_preset = ""
        self.ingame_name = "Atba (" + str(overall_index) + ")"  # TODO: Change to use config's ingame name

        if team_i is not None:
            self.team_index = team_i
            self.set_team(team_i)

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

        pass
        # looks_path = config_bundle.get_absolute_path(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
        # self.looks_config = BaseAgent.create_looks_configurations()
        # self.looks_config.parse_file(looks_path)

    def load_config(self, overall_config_file, overall_index):
        """Loads the config data into the agent"""
        self.overall_config = overall_config_file
        self.overall_index = overall_index
        self.load_agent_configs()
        self.load_fields_from_config()

    def load_fields_from_config(self):
        pass

    def get_config(self):

        return self.overall_index, self.config_bundle, self.looks_config

    def remove(self):
        """
        Removes the agent. Called by the GUI.
        """
        pass

    def __repr__(self):
        print(self.agent_class, 'dsdfsfsdfsd')
        return '%s (%s, %s)' % (self.__class__.__name__, self.agent_class.__name__, self.overall_index)

    def __str__(self):
        return '%s (%s)' % (self.ingame_name, self.__class__.__name__)  # TODO fix this up again

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
        return self.overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                            self.overall_index)

    def set_bot_skill(self, bot_skill):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                             bot_skill, self.overall_index)

    def get_team(self):
        return self.overall_config.getint(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, self.overall_index)

    def set_team(self, team_i):
        # sets team to team_i, where 0 is blue, 1 is orange
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, team_i,
                                             self.overall_index)
