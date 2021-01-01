import hashlib
from pathlib import Path

from rlbot import gateway_util
from rlbot.agents.standalone.standalone_bot_config import StandaloneBotConfig
from rlbot.matchconfig.match_config import PlayerConfig, MatchConfig, MutatorConfig, FLATBUFFER_MAX_INT
from rlbot.parsing.bot_config_bundle import BotConfigBundle
from rlbot.setup_manager import SetupManager


class TestSpawner:
    def __init__(self, python_file: Path, standalone_bot_config: StandaloneBotConfig, bundle: BotConfigBundle):
        self.python_file = python_file
        self.standalone_bot_config = standalone_bot_config
        self.bundle = bundle
        self.player_config: PlayerConfig = None
        self.setup_manager: SetupManager = None
        self.spawn_id = self.create_spawn_id()
        self.player_index = standalone_bot_config.player_index or 0
        self.team = standalone_bot_config.team or 0
        self.name = self.get_bot_name()

    def get_bot_name(self) -> str:
        if self.bundle is not None:
            return self.bundle.name
        if self.standalone_bot_config.name is not None:
            print(
                f'Spawning your bot with the name {self.standalone_bot_config.name} because no config path was provided!')
            return self.standalone_bot_config.name
        print(f'Spawning your bot with the name {self.python_file.name} because no config path was provided!')
        return self.python_file.name

    def create_spawn_id(self):
        """
        We want a spawn id unique to the python file which will be stable across re-runs.
        """
        hash = hashlib.sha1(str(self.python_file).encode('utf-8'))
        number_form = int(hash.hexdigest(), 16)
        return number_form % FLATBUFFER_MAX_INT

    def create_player_config(self, config_path: str) -> PlayerConfig:
        player_config = PlayerConfig()
        player_config.bot = True
        player_config.rlbot_controlled = True
        player_config.bot_skill = 1
        player_config.human_index = 0
        player_config.name = self.name
        player_config.team = 0
        player_config.config_path = config_path
        player_config.spawn_id = self.spawn_id
        return player_config

    def build_match_config(self, player_config_path: str):
        if self.player_config is None:
            self.player_config = self.create_player_config(player_config_path)

        match_config = MatchConfig()
        match_config.player_configs = [self.player_config]
        match_config.game_mode = 'Soccer'
        match_config.game_map = 'DFHStadium'
        match_config.existing_match_behavior = 'Continue And Spawn'
        match_config.mutators = MutatorConfig()
        match_config.enable_state_setting = True
        match_config.enable_rendering = True
        return match_config

    def spawn_bot(self):
        config_path = None
        if self.bundle is not None:
            config_path = self.bundle.config_path

        match_config = self.build_match_config(config_path)

        if self.setup_manager is None:
            self.setup_manager = SetupManager()

            rlbot_gateway_process, _ = gateway_util.find_existing_process()
            if rlbot_gateway_process is None:
                # RLBot.exe is not running yet, we should use the Restart behavior.
                # That avoids a situation where dead cars start piling up when
                # RLBot.exe gets killed and re-launched over and over and lacks context
                # to clean up previous cars.
                match_config.existing_match_behavior = 'Restart'

            self.setup_manager.connect_to_game()

        self.setup_manager.load_match_config(match_config)
        self.setup_manager.start_match()
