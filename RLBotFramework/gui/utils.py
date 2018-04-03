from tkinter.filedialog import askopenfilename

from itertools import count, filterfalse

from RLBotFramework.utils.class_importer import get_base_repo_path


def get_file(filetypes=None, title=None):
    """Grabs a file always opening at the base directory of this repo."""
    return askopenfilename(
        initialdir=get_base_repo_path(),
        filetypes=filetypes,
        title=title)


class IndexManager:

    # TODO: Update to use new base_gui
    def __init__(self, size):
        self.numbers = set()
        self.size = size
        self.not_filled_commands = list()
        self.filled_commands = list()

    def get_new_index(self):
        """
        Gets the next available index and marks it as in use.
        :return:  An index that is not currently in use
        """
        free_index = next(filterfalse(self.numbers.__contains__, count(0, 1)))
        if free_index >= self.size - 1:
            for method in self.filled_commands:
                method()
        self.numbers.add(free_index)
        return free_index

    def mark_used(self, index):
        self.numbers.add(index)

    def free_index(self, index):
        """
        Tells this manager that the passed in index is now free to reuse.
        :param index: The index that is now free to reuse.
        """
        if len(self.numbers) == self.size:
            for method in self.not_filled_commands:
                method()

        self.numbers.remove(index)

    def has_free_slots(self):
        return next(filterfalse(self.numbers.__contains__, count(1))) < self.size
