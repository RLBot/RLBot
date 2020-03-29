from pathlib import Path

from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.parsing.agent_config_parser import create_looks_configurations, load_bot_appearance


class BaseLoadoutGenerator:

    def __init__(self, base_directory: Path):
        self.base_directory = base_directory

    def generate_loadout(self, player_index: int, team: int) -> LoadoutConfig:
        raise NotImplementedError("You need to override the generate_loadout function!")

    def load_cfg_file(self, file_path: Path, team: int) -> LoadoutConfig:
        file = self.base_directory / Path(file_path)
        config_object = create_looks_configurations().parse_file(file)
        return load_bot_appearance(config_object, team)
