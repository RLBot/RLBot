import os

from rlbot.agents.base_agent import BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY
from rlbot.gui.presets import AgentPreset, LoadoutPreset
from rlbot.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY, \
    PARTICIPANT_BOT_SKILL_KEY, PARTICIPANT_TYPE_KEY, PARTICIPANT_TEAM, PARTICIPANT_LOADOUT_CONFIG_KEY, \
    BOT_CONFIG_LOADOUT_HEADER
from rlbot.parsing.bot_config_bundle import BotConfigBundle


class GUIAgent:
    """
    Holds all info for an agent stored in the GUI, also contains some methods to set values more easily
    """
    overall_config = None

    def __init__(self, overall_index: int, loadout_preset: LoadoutPreset = None, agent_preset: AgentPreset = None):
        self.overall_index = overall_index
        self.loadout_preset = loadout_preset
        self.agent_preset = agent_preset
        if loadout_preset is not None:
            self.ingame_name = loadout_preset.config.get(BOT_CONFIG_LOADOUT_HEADER, BOT_NAME_KEY)
        else:
            self.ingame_name = None

    # Below here the getters and setters
    def get_configs(self):
        """
        :return: overall index, agent config, loadout config in that order
        """
        loadout_config = self.loadout_preset.config.copy()

        config_path = None
        if self.agent_preset.config_path is not None:  # Might be none if preset was never saved to disk.
            config_path = os.path.dirname(self.agent_preset.config_path)
        config = self.agent_preset.config.copy()
        config.set_value(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, self.ingame_name)
        config_bundle = BotConfigBundle(config_path, config, os.path.basename(self.agent_preset.config_path))

        return self.overall_index, config_bundle, loadout_config

    def set_name(self, name):
        self.ingame_name = name

    def get_name(self):
        return self.ingame_name

    def set_loadout_preset(self, loadout_preset: LoadoutPreset):
        self.loadout_preset = loadout_preset
        self.set_loadout_config_path(loadout_preset.config_path)

    def get_loadout_preset(self):
        return self.loadout_preset

    def set_agent_preset(self, agent_preset: AgentPreset):
        self.agent_preset = agent_preset
        self.set_agent_config_path(agent_preset.config_path)

    def get_agent_preset(self):
        return self.agent_preset

    def get_agent_config_path(self):
        path = self.overall_config.getpath(PARTICIPANT_CONFIGURATION_HEADER,
                                           PARTICIPANT_CONFIG_KEY, self.overall_index)

        if path is None:
            return None
        return os.path.realpath(path)

    def set_agent_config_path(self, config_path: str):
        # Use relative path in config
        if os.path.isabs(config_path):
            config_path = os.path.relpath(config_path, self.overall_config.config_directory)
        self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_CONFIG_KEY,
                                      config_path, self.overall_index)

    def get_loadout_config_path(self):
        return os.path.realpath(self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER,
                                                        PARTICIPANT_LOADOUT_CONFIG_KEY, self.overall_index))

    def set_loadout_config_path(self, config_path: str):
        # If using own loudout, we set loadout value in the overall_config to None
        if config_path == self.agent_preset.looks_path:
            config_path = "None"
        self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY,
                                      config_path, self.overall_index)

    def get_participant_type(self):
        return self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TYPE_KEY, self.overall_index)

    def set_participant_type(self, participant_type: str):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TYPE_KEY,
                                             participant_type, self.overall_index)

    def get_bot_skill(self):
        return self.overall_config.getfloat(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                            self.overall_index)

    def set_bot_skill(self, bot_skill: float):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_BOT_SKILL_KEY,
                                             bot_skill, self.overall_index)

    def get_team(self):
        return self.overall_config.getint(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, self.overall_index)

    def set_team(self, team_i: int):
        return self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_TEAM, team_i,
                                             self.overall_index)
