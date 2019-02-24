class HelperProcessRequest:
    """
    This class allows agents to express their need for a helper process that may be shared with other agents.
    """

    def __init__(self, python_file_path: str, key: str, executable: str = None, options: dict = None):
        """
        :param python_file_path: The file that should be loaded and inspected for a subclass of BotHelperProcess.
        :param key: A key used to control the mapping of helper processes to bots. For example, you could set
        something like 'myBotType-team1' in order to get one shared helper process per team.
        :param executable: A path to an executable that should be run as a separate process
        :param options: A dict with arbitrary options that will be passed through to the helper process.
        """
        self.python_file_path = python_file_path
        self.key = key
        self.executable = executable
        self.options = options
