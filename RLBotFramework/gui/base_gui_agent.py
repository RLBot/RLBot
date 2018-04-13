import os
from RLBotFramework.agents.base_agent import BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, BOT_NAME_KEY
from RLBotFramework.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, \
    PARTICIPANT_BOT_SKILL_KEY, PARTICIPANT_TYPE_KEY, PARTICIPANT_TEAM, get_bot_config_bundle, BotConfigBundle


class BaseGuiAgent:
    overall_config = None  # The config that is shared by all agent frames.

    def __init__(self, overall_index, team_i=None, loadout_preset=None, agent_preset=None):
        """
        Creates a class containing the info needed to extract by the GUI
        :param overall_index: An optional value if the overall index of this agent is already specified.
        :return: an instance of BaseAgentFrame
        """
        self.overall_index = overall_index

        self.agent_config_path = None
        self.loadout_config_path = None
        self.loadout_preset = loadout_preset
        self.agent_preset = agent_preset
        self.ingame_name = agent_preset.config.get(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY) if agent_preset is not None \
            else None

        if team_i is not None:
            self.team_index = team_i
            self.set_team(team_i)

    def get_configs(self):
        """
        :return: A tuple in the shape of (overall index, agent config, loadout config)
        """
        agent_config = self.agent_preset.config.copy()
        agent_config.set_value(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, self.ingame_name)

        return self.overall_index, agent_config, self.loadout_preset.config

    def set_name(self, name):
        self.ingame_name = name

    def get_name(self):
        return self.ingame_name

    def set_loadout_preset(self, loadout_preset):
        self.loadout_preset = loadout_preset

    def get_loadout_preset(self):
        return self.loadout_preset

    def set_agent_preset(self, agent_preset):
        self.agent_preset = agent_preset
        self.ingame_name = agent_preset.config.get(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY)

    def get_agent_preset(self):
        return self.agent_preset

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
