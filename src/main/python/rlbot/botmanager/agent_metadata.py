from rlbot.botmanager.helper_process_request import HelperProcessRequest


class AgentMetadata:
    """
    This class is used for storing and passing around the information about a single agent.
    TODO: Currently overlaps with the information that `BotManager` has.
    """

    def __init__(self, index: int, name: str, team: int, pids: set,
                 helper_process_request: HelperProcessRequest = None):
        """
        :param index: The player index, i.e. "this is player number <index>". Will be passed to the bot's constructor.
        :param name: name which will be passed to the bot's constructor. Will probably be displayed in-game.
        :param team: 0 for blue team or 1 for orange team. Will be passed to the bot's constructor.
        :param pids: A list all the process ids that this bot uses (including the ones inside the python process).
        :param helper_process_request: A helper process which can be shared, e.g. with other bots of the same type.
        """
        self.index = index
        self.name = name
        self.team = team
        self.pids = pids
        self.helper_process_request = helper_process_request
