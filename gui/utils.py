from tkinter.filedialog import askopenfilename

import os


def get_file(filetypes=None, title=None):
    """Grabs a file always opening at the base directory of this repo."""
    return askopenfilename(
        initialdir=get_base_repo_path(),
        filetypes=filetypes,
        title=title)


def get_base_repo_path():
    """Gets the path of the RLBot directory"""
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
