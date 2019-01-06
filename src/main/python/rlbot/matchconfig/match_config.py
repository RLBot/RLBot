from typing import List

from rlbot.parsing.agent_config_parser import BotConfigBundle, get_sanitized_bot_name, get_looks_config, \
    write_bot_appearance
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
        self.config_bundle: BotConfigBundle = None  # Required only if rlbot_controlled is true

    def write(self, player_configuration: PlayerConfiguration, name_dict: dict):
        player_configuration.bot = self.bot
        player_configuration.rlbot_controlled = self.rlbot_controlled
        player_configuration.bot_skill = self.bot_skill
        player_configuration.human_index = self.human_index
        player_configuration.name = get_sanitized_bot_name(name_dict, self.name)
        player_configuration.team = self.team

        if self.config_bundle:
            looks_config = get_looks_config(self.config_bundle)
            write_bot_appearance(looks_config, self.team, player_configuration)


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
        mutator_settings.match_length = match_length_types.index(self.match_length)
        mutator_settings.max_score = max_score_types.index(self.max_score)
        mutator_settings.overtime_option = overtime_mutator_types.index(self.overtime)
        mutator_settings.series_length_option = series_length_mutator_types.index(self.series_length)
        mutator_settings.game_speed_option = game_speed_mutator_types.index(self.game_speed)
        mutator_settings.ball_max_speed_option = ball_max_speed_mutator_types.index(self.ball_max_speed)
        mutator_settings.ball_type_option = ball_type_mutator_types.index(self.ball_type)
        mutator_settings.ball_weight_option = ball_weight_mutator_types.index(self.ball_weight)
        mutator_settings.ball_size_option = ball_size_mutator_types.index(self.ball_size)
        mutator_settings.ball_bounciness_option = ball_bounciness_mutator_types.index(self.ball_bounciness)
        mutator_settings.boost_amount_option = boost_amount_mutator_types.index(self.boost_amount)
        mutator_settings.rumble_option = rumble_mutator_types.index(self.rumble)
        mutator_settings.boost_strength_option = boost_strength_mutator_types.index(self.boost_strength)
        mutator_settings.gravity_option = gravity_mutator_types.index(self.gravity)
        mutator_settings.demolish_option = demolish_mutator_types.index(self.demolish)
        mutator_settings.respawn_time_option = respawn_time_mutator_types.index(self.respawn_time)


class MatchConfig:
    """
    Represents configuration for an entire match. Includes player config and mutators.
    """

    def __init__(self):
        self.player_configs: List[PlayerConfig] = None
        self.num_players: int = None
        self.game_mode: str = None
        self.game_map: str = None
        self.mutators: MutatorConfig = None

    def create_match_settings(self) -> MatchSettings:
        match_settings = MatchSettings()
        name_dict = {}
        for index, player_config in enumerate(self.player_configs):
            player_config.write(match_settings.player_configuration[index], name_dict)
        match_settings.num_players = self.num_players
        match_settings.game_mode = game_mode_types.index(self.game_mode)
        match_settings.game_map = map_types.index(self.game_map)

        self.mutators.write(match_settings.mutator_settings)

        return match_settings
