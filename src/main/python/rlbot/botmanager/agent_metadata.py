from rlbot.botmanager.helper_process_request import HelperProcessRequest


class AgentMetadata:
    """
    This class is used for storing and passing around the information about a single agent.
    TODO: Currently overlaps with the information that `BotManager` has.
    """

    def __init__(self, index: int, name: str, team: int, pids: set,
                 helper_process_request: HelperProcessRequest = None):
        """
        :param index: The player index, i.e. "this is player number <index>".
        :param name: The agent's name.
        :param team: 0 for blue team or 1 for orange team.
        :param pids: A list all the process ids that this bot uses (including the ones inside the python process).
        :param helper_process_request: A helper process which can be shared, e.g. with other bots of the same type.
        """
        self.index = index
        self.name = name
        self.team = team
        self.pids = pids
        self.helper_process_request = helper_process_request
