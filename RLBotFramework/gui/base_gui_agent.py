import os

from RLBotFramework.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, LOOKS_CONFIG_KEY
from RLBotFramework.utils.class_importer import import_agent
from RLBotFramework.utils.rlbot_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, \
    PARTICIPANT_BOT_KEY, PARTICIPANT_RLBOT_KEY, PARTICIPANT_BOT_SKILL_KEY, get_bot_config_bundle, BotConfigBundle
from RLBotFramework.utils.rlbot_config_parser import get_team

class BaseGuiAgent:
    config_object = None  # The config that is
    overall_config = None  # The config that is shared by all agent frames.
    overall_index = -1  # The index that grabs data from the overall_config
    team_index = -1  # The index representing what team the agent belongs to.
    agent_config_path = None  # The config path for the agent config file
    agent_config = None
    looks_config = None
    config_bundle = None

    def __init__(self, overall_index):
        """
        Creates a new agent frame, loads config data if needed.
        :param overall_index: An optional value if the overall index of this agent is already specified.
        :return: an instance of BaseAgentFrame
        """
        self.overall_index = overall_index
        self.load_config(self.overall_config, overall_index)

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
        return 'BaseGuiAgent (%s, %s)' % (self.agent_class.__name__, self.overall_index)

    def get_agent_config_path(self):
        return os.path.realpath(self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER,
                                                        PARTICIPANT_CONFIG_KEY, self.overall_index))

    def set_agent_config_path(self, config_path):
        self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY,
                                      config_path, self.overall_index)

    def is_participant_bot(self):
        return self.overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_KEY,
                                              self.overall_index)

    def set_is_participant_bot(self, is_bot):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_KEY,
                                             is_bot, self.overall_index)

    def is_participant_custom_bot(self):
        return self.overall_config.getboolean(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_RLBOT_KEY,
                                              self.overall_index)

    def set_is_participant_custom_bot(self, is_rlbot):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_RLBOT_KEY,
                                             is_rlbot, self.overall_index)

    def get_bot_skill(self):
        return self.overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                            self.overall_index)

    def set_bot_skill(self, bot_skill):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                             bot_skill, self.overall_index)

    def get_team_is_blue(self):
        print(self.overall_index)
        team_index = get_team(self.overall_config, self.overall_index)
        return team_index == 0