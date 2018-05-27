from RLBotFramework.botmanager.helper_process_request import HelperProcessRequest


class AgentMetadata:
    def __init__(self, index: int, name: str, team: int, pids: set,
                 helper_process_request: HelperProcessRequest = None):
        self.index = index
        self.name = name
        self.team = team
        self.pids = pids
        self.helper_process_request = helper_process_request
