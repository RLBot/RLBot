from typing import List

from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.parsing.match_settings_config_parser import boost_amount_mutator_types, map_types, game_mode_types, \
    match_length_types, max_score_types, overtime_mutator_types, series_length_mutator_types, game_speed_mutator_types, \
    ball_max_speed_mutator_types, ball_type_mutator_types, ball_weight_mutator_types, ball_size_mutator_types, \
    ball_bounciness_mutator_types, rumble_mutator_types, boost_strength_mutator_types, gravity_mutator_types, \
    demolish_mutator_types, respawn_time_mutator_types
from rlbot.utils.structures.start_match_structures import MatchSettings, PlayerConfiguration, MutatorSettings


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

    def write(self, player_configuration: PlayerConfiguration, name_dict: dict):
        player_configuration.bot = self.bot
        player_configuration.rlbot_controlled = self.rlbot_controlled
        player_configuration.bot_skill = self.bot_skill or 0
        player_configuration.human_index = self.human_index or 0
        player_configuration.name = get_sanitized_bot_name(name_dict, self.name)
        player_configuration.team = self.team

        if self.loadout_config:
            self.loadout_config.write(player_configuration)


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
        mutator_settings.match_length = self.index_or_zero(match_length_types, self.match_length)
        mutator_settings.max_score = self.index_or_zero(max_score_types, self.max_score)
        mutator_settings.overtime_option = self.index_or_zero(overtime_mutator_types, self.overtime)
        mutator_settings.series_length_option = self.index_or_zero(series_length_mutator_types, self.series_length)
        mutator_settings.game_speed_option = self.index_or_zero(game_speed_mutator_types, self.game_speed)
        mutator_settings.ball_max_speed_option = self.index_or_zero(ball_max_speed_mutator_types, self.ball_max_speed)
        mutator_settings.ball_type_option = self.index_or_zero(ball_type_mutator_types, self.ball_type)
        mutator_settings.ball_weight_option = self.index_or_zero(ball_weight_mutator_types, self.ball_weight)
        mutator_settings.ball_size_option = self.index_or_zero(ball_size_mutator_types, self.ball_size)
        mutator_settings.ball_bounciness_option = self.index_or_zero(ball_bounciness_mutator_types, self.ball_bounciness)
        mutator_settings.boost_amount_option = self.index_or_zero(boost_amount_mutator_types, self.boost_amount)
        mutator_settings.rumble_option = self.index_or_zero(rumble_mutator_types, self.rumble)
        mutator_settings.boost_strength_option = self.index_or_zero(boost_strength_mutator_types, self.boost_strength)
        mutator_settings.gravity_option = self.index_or_zero(gravity_mutator_types, self.gravity)
        mutator_settings.demolish_option = self.index_or_zero(demolish_mutator_types, self.demolish)
        mutator_settings.respawn_time_option = self.index_or_zero(respawn_time_mutator_types, self.respawn_time)

    @staticmethod
    def index_or_zero(types, value):
        if value is None:
            return 0
        return types.index(value)


class ExtensionConfig:
    def __init__(self):
        self.python_file_path: str = None


class MatchConfig:
    """
    Represents configuration for an entire match. Includes player config and mutators.
    """

    def __init__(self):
        self.player_configs: List[PlayerConfig] = []
        self.num_players: int = None
        self.game_mode: str = None
        self.game_map: str = None
        self.skip_replays: bool = None
        self.instant_start: bool = None
        self.mutators: MutatorConfig = None
        self.extension_config: ExtensionConfig = None

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

        self.mutators.write(match_settings.mutator_settings)

        return match_settings


def get_sanitized_bot_name(dict, name):
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
        dict[name] = count + 1

    return new_name