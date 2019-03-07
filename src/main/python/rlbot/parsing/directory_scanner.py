import glob
import os
from configparser import NoSectionError, MissingSectionHeaderError, NoOptionError, ParsingError
from typing import Set

from rlbot.parsing.bot_config_bundle import BotConfigBundle, get_bot_config_bundle


def scan_directory_for_bot_configs(root_dir) -> Set[BotConfigBundle]:
    """
    Recursively scans a directory for all valid bot configs.
    :param root_dir: Directory to scan.
    :return: The set of bot configs that were found.
    """

    configs = set()

    for filename in glob.iglob(os.path.join(root_dir, '**/*.cfg'), recursive=True):
        try:
            bundle = get_bot_config_bundle(filename)
            configs.add(bundle)
        except (NoSectionError, MissingSectionHeaderError, NoOptionError, AttributeError, ParsingError, FileNotFoundError):
            pass

    return configs
