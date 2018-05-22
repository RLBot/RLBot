import os

from RLBotFramework.agents.base_agent import BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY
from RLBotFramework.gui.presets import AgentPreset, LoadoutPreset
from RLBotFramework.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, \
    PARTICIPANT_BOT_SKILL_KEY, PARTICIPANT_TYPE_KEY, PARTICIPANT_TEAM


class Agent:
    overall_config = None

    def __init__(self, overall_index: int, loadout_preset: LoadoutPreset=None, agent_preset: AgentPreset=None):
        self.overall_index = overall_index
        self.loadout_preset = loadout_preset
        self.agent_preset = agent_preset
        if agent_preset is not None:
            self.ingame_name = agent_preset.config.get(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY)
        else:
            self.ingame_name = None

    # Below here the getters and setters
    def get_configs(self):
        """
        :return: overall index, agent config, loadout config in that order
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