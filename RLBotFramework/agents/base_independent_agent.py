from RLBotFramework.agents.base_agent import BaseAgent
from RLBotFramework.grpcsupport.protobuf import game_data_pb2


class BaseIndependentAgent(BaseAgent):
    """
    Extend this class if you want to manage calling the dll yourself.
    """

    def run_independently(self):
        raise NotImplementedError
