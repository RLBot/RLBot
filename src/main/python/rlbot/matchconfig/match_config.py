from pathlib import Path
from enum import Enum
from random import randint
from typing import List, Dict

from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle
from rlbot.parsing.agent_config_parser import load_bot_appearance
from rlbot.parsing.match_settings_config_parser import boost_amount_mutator_types, map_types, game_mode_types, \
    match_length_types, max_score_types, overtime_mutator_types, series_length_mutator_types, game_speed_mutator_types, \
    ball_max_speed_mutator_types, ball_type_mutator_types, ball_weight_mutator_types, ball_size_mutator_types, \
    ball_bounciness_mutator_types, rumble_mutator_types, boost_strength_mutator_types, gravity_mutator_types, \
    demolish_mutator_types, respawn_time_mutator_types, existing_match_behavior_types
from rlbot.utils.structures.start_match_structures import MatchSettings, PlayerConfiguration, MutatorSettings


class Team(Enum):
    BLUE = 0
    ORANGE = 1


class PlayerConfig:
    """
    Represents configuration for a player (could be a bot, a human, etc).
    Encompasses everything, including loadout, behavior, etc.

    Knows how to translate itself into the PlayerConfiguration ctypes class.
    """

    def __init__(self):
        self.bot: bool = None
        self.rlbot_controlled: bool = None
        self.bot_skill: float = None
        self.human_index: int = None
        self.name: str = None
        self.team: int = None
        self.config_path: str = None  # Required only if rlbot_controlled is true
        self.loadout_config: LoadoutConfig = None

    @staticmethod  # TODO: in Python 3.7 we can remove the quotes from the return type.
    def bot_config(player_config_path: Path, team: Team) -> 'PlayerConfig':
        """
        A function to cover the common case of creating a config for a bot.
        """
        bot_config = PlayerConfig()
        bot_config.bot = True
        bot_config.rlbot_controlled = True
        bot_config.team = team.value
        bot_config.config_path = str(player_config_path.absolute())  # TODO: Refactor to use Path's
        config_bundle = get_bot_config_bundle(bot_config.config_path)
        bot_config.name = config_bundle.name
        bot_config.loadout_config = load_bot_appearance(config_bundle.get_looks_config(), bot_config.team)
        return bot_config

    def write(self, player_configuration: PlayerConfiguration, name_dict: dict):
        player_configuration.bot = self.bot
        player_configuration.rlbot_controlled = self.rlbot_controlled
        player_configuration.bot_skill = self.bot_skill or 0
        player_configuration.human_index = self.human_index or 0
        player_configuration.name = get_sanitized_bot_name(name_dict, self.name)
        player_configuration.team = self.team
        player_configuration.spawn_id = randint(1, 65535)

        if self.loadout_config:
            self.loadout_config.write(player_configuration)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


def index_or_zero(types, value):
    if value is None:
        return 0
    return types.index(value)


class MutatorConfig:
    """
    Represent mutator configuration, e.g. match length, boost amount, etc.

    Knows how to translate itself into the MutatorSettings ctypes class.
    """

    def __init__(self):
        self.match_length: str = None
        self.max_score: str = None
        self.overtime: str = None
        self.series_length: str = None
        self.game_speed: str = None
        self.ball_max_speed: str = None
        self.ball_type: str = None
        self.ball_weight: str = None
        self.ball_size: str = None
        self.ball_bounciness: str = None
        self.boost_amount: str = None
        self.rumble: str = None
        self.boost_strength: str = None
        self.gravity: str = None
        self.demolish: str = None
        self.respawn_time: str = None

    def write(self, mutator_settings: MutatorSettings):
        mutator_settings.match_length = index_or_zero(match_length_types, self.match_length)
        mutator_settings.max_score = index_or_zero(max_score_types, self.max_score)
        mutator_settings.overtime_option = index_or_zero(overtime_mutator_types, self.overtime)
        mutator_settings.series_length_option = index_or_zero(series_length_mutator_types, self.series_length)
        mutator_settings.game_speed_option = index_or_zero(game_speed_mutator_types, self.game_speed)
        mutator_settings.ball_max_speed_option = index_or_zero(ball_max_speed_mutator_types, self.ball_max_speed)
        mutator_settings.ball_type_option = index_or_zero(ball_type_mutator_types, self.ball_type)
        mutator_settings.ball_weight_option = index_or_zero(ball_weight_mutator_types, self.ball_weight)
        mutator_settings.ball_size_option = index_or_zero(ball_size_mutator_types, self.ball_size)
        mutator_settings.ball_bounciness_option = index_or_zero(ball_bounciness_mutator_types, self.ball_bounciness)
        mutator_settings.boost_amount_option = index_or_zero(boost_amount_mutator_types, self.boost_amount)
        mutator_settings.rumble_option = index_or_zero(rumble_mutator_types, self.rumble)
        mutator_settings.boost_strength_option = index_or_zero(boost_strength_mutator_types, self.boost_strength)
        mutator_settings.gravity_option = index_or_zero(gravity_mutator_types, self.gravity)
        mutator_settings.demolish_option = index_or_zero(demolish_mutator_types, self.demolish)
        mutator_settings.respawn_time_option = index_or_zero(respawn_time_mutator_types, self.respawn_time)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


class ExtensionConfig:
    def __init__(self):
        self.python_file_path: str = None

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


class MatchConfig:
    """
    Represents configuration for an entire match. Includes player config and mutators.
    """

    def __init__(self):
        self.player_configs: List[PlayerConfig] = []
        self.game_mode: str = None
        self.game_map: str = None
        self.skip_replays: bool = None
        self.instant_start: bool = None
        self.mutators: MutatorConfig = None
        self.extension_config: ExtensionConfig = None
        self.existing_match_behavior: str = None
        self.enable_lockstep: bool = None
        self.networking_role: str = None
        self.network_address: str = None

    @property
    def num_players(self):
        return len(self.player_configs)

    # TODO: retire the MatchSettings object and just build a flatbuffer here instead.
    def create_match_settings(self) -> MatchSettings:
        match_settings = MatchSettings()
        name_dict = {}
        for index, player_config in enumerate(self.player_configs):
            player_config.write(match_settings.player_configuration[index], name_dict)
        match_settings.num_players = self.num_players
        match_settings.game_mode = game_mode_types.index(self.game_mode)
        match_settings.game_map = map_types.index(self.game_map)
        match_settings.skip_replays = self.skip_replays
        match_settings.instant_start = self.instant_start
        match_settings.existing_match_behavior = index_or_zero(existing_match_behavior_types, self.existing_match_behavior)
        match_settings.enable_lockstep = self.enable_lockstep

        self.mutators.write(match_settings.mutator_settings)

        return match_settings

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


def get_sanitized_bot_name(dict: Dict[str, int], name: str) -> str:
    """
    Cut off at 31 characters and handle duplicates.
    :param dict: Holds the list of names for duplicates
    :param name: The name that is being sanitized
    :return: A sanitized version of the name
    """
    if name not in dict:
        new_name = name[:31]  # Make sure name does not exceed 31 characters
        dict[name] = 1
    else:
        count = dict[name]
        new_name = name[:27] + "(" + str(count + 1) + ")"  # Truncate at 27 because we can have up to '(10)' appended
        assert new_name not in dict  # TODO: Fix collision between ["foo", "foo", "foo(1)"]
        dict[name] = count + 1

    return new_name
