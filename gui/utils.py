from tkinter.filedialog import askopenfilename

import os


def get_file(filetypes=None, title=None):
    """Grabs a file always opening at the base directory of this repo."""
    return askopenfilename(
        initialdir=os.path.dirname(os.path.realpath(__file__)),
        filetypes=filetypes,
        title=title)
