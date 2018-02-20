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


class IndexManager:
    def get_new_index(self):
        """
        Gets the next available index and marks it as in use.
        :return:  An index that is not currently in use
        """
        return -1

    def free_index(self, index):
        """
        Tells this manager that the passed in index is now free to reuse.
        :param index: The index that is now free to reuse.
        """
        pass
