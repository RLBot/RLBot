from itertools import count, filterfalse


class IndexManager:
    """
    Handles the indices for agents, some useful methods for handling the overall indices
    """

    def __init__(self, size):
        self.numbers = set()
        self.size = size

    def get_new_index(self):
        """
        Gets the next available index and marks it as in use.
        :return:  An index that is not currently in use
        """
        free_index = next(filterfalse(self.numbers.__contains__, count(0, 1)))
        self.numbers.add(free_index)
        return free_index

    def use_index(self, index):
        self.numbers.add(index)

    def free_index(self, index):
        """
        Tells this manager that the passed in index is now free to reuse.
        :param index: The index that is now free to reuse.
        """
        self.numbers.remove(index)

    def has_free_slots(self):
        """
        Checks if there is a free value smaller than self.size
        :return: True if there is a free value, False if not
        """
        return next(filterfalse(self.numbers.__contains__, count(1))) < self.size
