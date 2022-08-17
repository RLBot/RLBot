import os
from pathlib import Path


def get_items_path() -> Path:
    """Returns the path to RLBot's items.csv file for reading"""
    return Path(os.path.join(Path(os.path.realpath(__file__)).parent, "items.csv"))
