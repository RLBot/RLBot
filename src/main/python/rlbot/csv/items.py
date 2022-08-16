import os
from pathlib import Path


def open_csv():
    """Opens RLBot's items.csv file for reading"""
    return open(os.path.join(Path(os.path.realpath(__file__)).parent, "items.csv"), "r")
