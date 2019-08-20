class IncrementingInteger:
    """
    Keeps track of an integer value as it gets incremented.
    """

    def __init__(self, initial_val: int):
        self.value = initial_val

    def increment(self):
        val = self.value
        self.value += 1
        return val
