from pathlib import Path
from enum import Enum
from random import randint
from typing import List, Dict

from flatbuffers import Builder
from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.messages.flat.PlayerClass import PlayerClass
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle
from rlbot.parsing.agent_config_parser import load_bot_appearance
from rlbot.parsing.match_settings_config_parser import boost_amount_mutator_types, map_types, game_mode_types, \
    match_length_types, max_score_types, overtime_mutator_types, series_length_mutator_types, game_speed_mutator_types, \
    ball_max_speed_mutator_types, ball_type_mutator_types, ball_weight_mutator_types, ball_size_mutator_types, \
    ball_bounciness_mutator_types, rumble_mutator_types, boost_strength_mutator_types, gravity_mutator_types, \
    demolish_mutator_types, respawn_time_mutator_types, existing_match_behavior_types, game_map_dict
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.start_match_structures import MatchSettings, PlayerConfiguration, MutatorSettings
from rlbot.messages.flat import MatchSettings as MatchSettingsFlat, MutatorSettings as MutatorSettingsFlat, RLBotPlayer, \
    PsyonixBotPlayer, HumanPlayer, PlayerConfiguration as PlayerConfigurationFlat

# We pass messages in flatbuffer format to RLBot.exe. In flatbuffer, a signed int field
# is 32 bit, so it has a max value of 2^31 - 1, in other words 2147483647.
FLATBUFFER_MAX_INT = 2**31 - 1

class Team(Enum):
    BLUE = 0
    ORANGE = 1

class ScriptConfig:
    def __init__(self, config_path):
        self.config_path: str = config_path

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
        self.deduped_name: str = None
        self.team: int = None
        self.config_path: str = None  # Required only if rlbot_controlled is true
        self.loadout_config: LoadoutConfig = None
        self.spawn_id: int = randint(1, FLATBUFFER_MAX_INT)  # Feel free to override this.

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
        self.deduped_name = get_sanitized_bot_name(name_dict, self.name)
        player_configuration.bot = self.bot
        player_configuration.rlbot_controlled = self.rlbot_controlled
        player_configuration.bot_skill = self.bot_skill or 0
        player_configuration.human_index = self.human_index or 0
        player_configuration.name = self.deduped_name
        player_configuration.team = self.team
        player_configuration.spawn_id = self.spawn_id

        if self.loadout_config:
            self.loadout_config.write(player_configuration)

    def write_to_flatbuffer(self, builder: Builder, name_dict: dict):
        self.deduped_name = get_sanitized_bot_name(name_dict, self.name)
        name = builder.CreateString(self.deduped_name)

        if self.loadout_config:
            loadout = self.loadout_config.write_to_flatbuffer(builder)
        else:
            loadout = LoadoutConfig().write_to_flatbuffer(builder)

        if self.bot:
            if self.rlbot_controlled:
                variety = PlayerClass.RLBotPlayer
                RLBotPlayer.RLBotPlayerStart(builder)
                player = RLBotPlayer.RLBotPlayerEnd(builder)
            else:
                variety = PlayerClass.PsyonixBotPlayer
                PsyonixBotPlayer.PsyonixBotPlayerStart(builder)
                PsyonixBotPlayer.PsyonixBotPlayerAddBotSkill(builder, self.bot_skill)
                player = PsyonixBotPlayer.PsyonixBotPlayerEnd(builder)
        else:
            variety = PlayerClass.HumanPlayer
            HumanPlayer.HumanPlayerStart(builder)
            player = HumanPlayer.HumanPlayerEnd(builder)

        PlayerConfigurationFlat.PlayerConfigurationStart(builder)
        PlayerConfigurationFlat.PlayerConfigurationAddName(builder, name)
        PlayerConfigurationFlat.PlayerConfigurationAddLoadout(builder, loadout)
        PlayerConfigurationFlat.PlayerConfigurationAddTeam(builder, self.team)
        PlayerConfigurationFlat.PlayerConfigurationAddVariety(builder, player)
        PlayerConfigurationFlat.PlayerConfigurationAddVarietyType(builder, variety)
        PlayerConfigurationFlat.PlayerConfigurationAddSpawnId(builder, self.spawn_id)
        return PlayerConfigurationFlat.PlayerConfigurationEnd(builder)

    def has_bot_script(self) -> bool:
        return self.rlbot_controlled

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


class EmptyPlayerSlot(PlayerConfig):
    """
    This is useful for keeping a player index empty.
    """
    def write(self, player_configuration: PlayerConfiguration, name_dict: dict):
        # This is a dirty trick. With bot = False and rlbot_controlled = True, we have a "party member bot"
        # which is not supported in RLBot.exe anymore and will just get skipped over. That's what we want.
        player_configuration.bot = False
        player_configuration.rlbot_controlled = True
        player_configuration.spawn_id = -1
        player_configuration.name = ""

    def has_bot_script(self) -> bool:
        return False


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

    def write_to_flatbuffer(self, builder: Builder):
        MutatorSettingsFlat.MutatorSettingsStart(builder)
        MutatorSettingsFlat.MutatorSettingsAddMatchLength(builder, index_or_zero(match_length_types, self.match_length))
        MutatorSettingsFlat.MutatorSettingsAddMaxScore(builder, index_or_zero(max_score_types, self.max_score))
        MutatorSettingsFlat.MutatorSettingsAddOvertimeOption(builder, index_or_zero(overtime_mutator_types, self.overtime))
        MutatorSettingsFlat.MutatorSettingsAddSeriesLengthOption(builder, index_or_zero(series_length_mutator_types, self.series_length))
        MutatorSettingsFlat.MutatorSettingsAddGameSpeedOption(builder, index_or_zero(game_speed_mutator_types, self.game_speed))
        MutatorSettingsFlat.MutatorSettingsAddBallMaxSpeedOption(builder, index_or_zero(ball_max_speed_mutator_types, self.ball_max_speed))
        MutatorSettingsFlat.MutatorSettingsAddBallTypeOption(builder, index_or_zero(ball_type_mutator_types, self.ball_type))
        MutatorSettingsFlat.MutatorSettingsAddBallWeightOption(builder, index_or_zero(ball_weight_mutator_types, self.ball_weight))
        MutatorSettingsFlat.MutatorSettingsAddBallSizeOption(builder, index_or_zero(ball_size_mutator_types, self.ball_size))
        MutatorSettingsFlat.MutatorSettingsAddBallBouncinessOption(builder, index_or_zero(ball_bounciness_mutator_types, self.ball_bounciness))
        MutatorSettingsFlat.MutatorSettingsAddBoostOption(builder, index_or_zero(boost_amount_mutator_types, self.boost_amount))
        MutatorSettingsFlat.MutatorSettingsAddRumbleOption(builder, index_or_zero(rumble_mutator_types, self.rumble))
        MutatorSettingsFlat.MutatorSettingsAddBoostStrengthOption(builder, index_or_zero(boost_strength_mutator_types, self.boost_strength))
        MutatorSettingsFlat.MutatorSettingsAddGravityOption(builder, index_or_zero(gravity_mutator_types, self.gravity))
        MutatorSettingsFlat.MutatorSettingsAddDemolishOption(builder, index_or_zero(demolish_mutator_types, self.demolish))
        MutatorSettingsFlat.MutatorSettingsAddRespawnTimeOption(builder, index_or_zero(respawn_time_mutator_types, self.respawn_time))
        return MutatorSettingsFlat.MutatorSettingsEnd(builder)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    @staticmethod
    def from_mutator_settings_flatbuffer(mutator_settings: MutatorSettingsFlat):
        mc = MutatorConfig()
        mc.match_length = match_length_types[mutator_settings.MatchLength()]
        mc.max_score = max_score_types[mutator_settings.MaxScore()]
        mc.overtime = overtime_mutator_types[mutator_settings.OvertimeOption()]
        mc.series_length = series_length_mutator_types[mutator_settings.SeriesLengthOption()]
        mc.game_speed = game_speed_mutator_types[mutator_settings.GameSpeedOption()]
        mc.ball_max_speed = ball_max_speed_mutator_types[mutator_settings.BallMaxSpeedOption()]
        mc.ball_type = ball_type_mutator_types[mutator_settings.BallTypeOption()]
        mc.ball_weight = ball_weight_mutator_types[mutator_settings.BallWeightOption()]
        mc.ball_size = ball_size_mutator_types[mutator_settings.BallSizeOption()]
        mc.ball_bounciness = ball_bounciness_mutator_types[mutator_settings.BallBouncinessOption()]
        mc.boost_amount = boost_amount_mutator_types[mutator_settings.BoostOption()]
        mc.rumble = rumble_mutator_types[mutator_settings.RumbleOption()]
        mc.boost_strength = boost_strength_mutator_types[mutator_settings.BoostStrengthOption()]
        mc.gravity = gravity_mutator_types[mutator_settings.GravityOption()]
        mc.demolish = demolish_mutator_types[mutator_settings.DemolishOption()]
        mc.respawn_time = respawn_time_mutator_types[mutator_settings.RespawnTimeOption()]
        return mc


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
        self.skip_replays: bool = False
        self.instant_start: bool = False
        self.mutators: MutatorConfig = MutatorConfig()
        self.extension_config: ExtensionConfig = None
        self.existing_match_behavior: str = None
        self.enable_lockstep: bool = False
        self.networking_role: str = None
        self.network_address: str = None
        self.enable_rendering: bool = False
        self.enable_state_setting: bool = False
        self.auto_save_replay: bool = False
        self.script_configs: List[ScriptConfig] = []
        self.logger = get_logger('match_config')

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
        match_settings.game_mode = index_or_zero(game_mode_types, self.game_mode)
        match_settings.game_map = index_or_zero(map_types, self.game_map)
        match_settings.skip_replays = self.skip_replays
        match_settings.instant_start = self.instant_start
        match_settings.existing_match_behavior = index_or_zero(existing_match_behavior_types, self.existing_match_behavior)
        match_settings.enable_lockstep = self.enable_lockstep
        match_settings.enable_rendering = self.enable_rendering
        match_settings.enable_state_setting = self.enable_state_setting
        match_settings.auto_save_replay = self.auto_save_replay

        self.mutators.write(match_settings.mutator_settings)

        return match_settings

    def create_flatbuffer(self) -> Builder:
        builder = Builder(1000)
        name_dict = {}
        player_config_offsets = [pc.write_to_flatbuffer(builder, name_dict) for pc in self.player_configs]
        MatchSettingsFlat.MatchSettingsStartPlayerConfigurationsVector(builder, len(player_config_offsets))
        for i in reversed(range(0, len(player_config_offsets))):
            builder.PrependUOffsetTRelative(player_config_offsets[i])
        player_list_offset = builder.EndVector(len(player_config_offsets))
        mutator_settings_offset = self.mutators.write_to_flatbuffer(builder)

        if self.game_map in game_map_dict:
            upk = game_map_dict[self.game_map]
            map_index = map_types.index(self.game_map)
        else:
            self.logger.info(f"Did not recognize {self.game_map}, hoping it's new or a custom map!")
            upk = self.game_map
            map_index = -1
        upk_offset = builder.CreateString(upk)

        MatchSettingsFlat.MatchSettingsStart(builder)
        MatchSettingsFlat.MatchSettingsAddPlayerConfigurations(builder, player_list_offset)
        MatchSettingsFlat.MatchSettingsAddGameMode(builder, index_or_zero(game_mode_types, self.game_mode))
        MatchSettingsFlat.MatchSettingsAddGameMap(builder, map_index)
        MatchSettingsFlat.MatchSettingsAddGameMapUpk(builder, upk_offset)
        MatchSettingsFlat.MatchSettingsAddSkipReplays(builder, self.skip_replays)
        MatchSettingsFlat.MatchSettingsAddInstantStart(builder, self.instant_start)
        MatchSettingsFlat.MatchSettingsAddMutatorSettings(builder, mutator_settings_offset)
        MatchSettingsFlat.MatchSettingsAddExistingMatchBehavior(builder, index_or_zero(existing_match_behavior_types, self.existing_match_behavior))
        MatchSettingsFlat.MatchSettingsAddEnableLockstep(builder, self.enable_lockstep)
        MatchSettingsFlat.MatchSettingsAddEnableRendering(builder, self.enable_rendering)
        MatchSettingsFlat.MatchSettingsAddEnableStateSetting(builder, self.enable_state_setting)
        MatchSettingsFlat.MatchSettingsAddAutoSaveReplay(builder, self.auto_save_replay)
        ms_offset = MatchSettingsFlat.MatchSettingsEnd(builder)
        builder.Finish(ms_offset)
        return builder

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    @staticmethod
    def from_match_settings_flatbuffer(match_settings: MatchSettingsFlat):
        mc = MatchConfig()
        mc.game_mode = game_mode_types[match_settings.GameMode()]
        mc.game_map = map_types[match_settings.GameMap()]
        mc.mutators = MutatorConfig.from_mutator_settings_flatbuffer(match_settings.MutatorSettings())
        # TODO: player configs
        return mc


def get_sanitized_bot_name(dict: Dict[str, int], name: str) -> str:
    """
    Cut off at 31 characters and handle duplicates.
    :param dict: Holds the list of names for duplicates
    :param name: The name that is being sanitized
    :return: A sanitized version of the name
    """

    # This doesn't work someimtes in continue_and_spawn because it doesn't understand the names already in the match
    # which may be kept if the spawn IDs match. In that case it's the caller's responsibility to figure it out upstream.

    name = name[:31]
    base_name = name
    count = 2
    while name in dict:
        name = f'{base_name[:27]} ({count})'  # Truncate at 27 because we can have up to '(10)' appended
        count += 1
    dict[name] = 1
    return name
