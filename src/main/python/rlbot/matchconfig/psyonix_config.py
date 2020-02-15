import random
from pathlib import Path

from rlbot.matchconfig.match_config import PlayerConfig
from rlbot.parsing.agent_config_parser import load_bot_appearance, create_looks_configurations

PSYONIX_PRESET_DIRECTORY = Path(__file__).parent / "psyonix_presets"
PSYONIX_PRESET_LIST = list(PSYONIX_PRESET_DIRECTORY.glob("*.cfg"))
random.shuffle(PSYONIX_PRESET_LIST)


def set_random_psyonix_bot_preset(player: PlayerConfig):
    """
    Sets the name and loadout to a randomly selected psyonix bot preset.
    """
    loadout_file = PSYONIX_PRESET_LIST[0]
    PSYONIX_PRESET_LIST.append(PSYONIX_PRESET_LIST.pop(0))  # Move preset to the end of the list.
    loadout_config = create_looks_configurations().parse_file(loadout_file)
    player.loadout_config = load_bot_appearance(loadout_config, player.team)
    player.name = loadout_file.name.split("_")[1].title()
    player.name = ["Rookie ", "Pro ", ""][min(int(abs(player.bot_skill) * 3), 2)] + player.name
