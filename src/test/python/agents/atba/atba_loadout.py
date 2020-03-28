import random
from pathlib import Path

from rlbot.agents.base_loadout_generator import BaseLoadoutGenerator
from rlbot.matchconfig.loadout_config import LoadoutConfig


class AtbaLoadoutGenerator(BaseLoadoutGenerator):
    def generate_loadout(self, player_index: int, team: int) -> LoadoutConfig:

        # Start with a loadout based on the cfg file in the same directory as this generator
        loadout = self.load_cfg_file(Path('atba_looks.cfg'), team)

        if player_index == 0:
            loadout.antenna_id = 287

        loadout.team_color_id = player_index
        loadout.paint_config.wheels_paint_id = random.choice([1, 2, 4, 5])

        return loadout
