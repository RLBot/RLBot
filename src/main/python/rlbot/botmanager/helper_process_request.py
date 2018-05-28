class HelperProcessRequest:
    """
    This class allows agents to express their need for a helper process that may be shared with other agents.
    """

    def __init__(self, python_file_path: str, key: str):
        """
        :param python_file_path: The file that should be loaded and inspected for a subclass of BotHelperProcess.
        :param key: A key used to control the mapping of helper processes to bots. For example, you could set
        something like 'myBotType-team1' in order to get one shared helper process per team.
        """
        self.python_file_path = python_file_path
        self.key = key
