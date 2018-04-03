import os
from PyQt5.QtCore import QTimer

from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, LOOKS_CONFIG_KEY
from RLBotFramework.utils.class_importer import import_agent
from RLBotFramework.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, \
    PARTICIPANT_BOT_SKILL_KEY, PARTICIPANT_TYPE_KEY, PARTICIPANT_TEAM, get_bot_config_bundle, BotConfigBundle


class BaseGuiAgent:
    config_object = None  # The config that is
    overall_config = None  # The config that is shared by all agent frames.
    # overall_index = -1  # The index that grabs data from the overall_config
    # team_index = -1  # The index representing what team the agent belongs to.
    agent_config = None
    looks_config = None
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

        if team_i is not None:
            self.team_index = team_i
            self.set_team(team_i)

    def save_agent_config(self):
        def save():
            if not os.path.exists(self.agent_config_path):
                return
            with open(self.agent_config_path, "w") as f:
                f.write(str(self.agent_config))
        if self.save_agent_timer is None:
            self.save_agent_timer = QTimer()
            self.save_agent_timer.timeout.connect(save)
        self.save_agent_timer.start(5)  # Time-out for timer over here

    def save_loadout_config(self):
        def save():
            if not os.path.exists(self.loadout_config_path):
                return
            with open(self.loadout_config_path, "w") as f:
                f.write(str(self.looks_config))
        if self.save_loadout_timer is None:
            self.save_loadout_timer = QTimer()
            self.save_loadout_timer.timeout.connect(save)
        self.save_loadout_timer.start(5)  # Time-out for timer over here

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

    # TODO: The below 3 functions need  to be updated (i think a get_agent_config that returns a dict would be good)
    def write_fields_to_config(self):
        pass

    def load_fields_from_config(self):
        pass

    def get_config(self):
        self.write_fields_to_config()
        return self.overall_index, self.config_bundle, self.looks_config

    def remove(self):
        """
        Removes the agent. Called by the GUI.
        """
        pass

    def __repr__(self):
        return '%s (%s, %s)' % (self.__class__.__name__, self.agent_class.__name__, self.overall_index)

    def __str__(self):
        return '%s (%s)' % (self.agent_class.__name__, self.overall_index)

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

    def get_team_is_blue(self):
        team_index = self.overall_config.getint(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM,
                                                self.overall_index)
        return team_index == 0

    def set_team(self, team_i):
        # sets team to team_i, where 0 is blue, 1 is orange
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, team_i,
                                             self.overall_index)
