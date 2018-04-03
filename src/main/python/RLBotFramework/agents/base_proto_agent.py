from RLBotFramework.agents.base_agent import BaseAgent
from protobuf import game_data_pb2


class BaseProtoAgent(BaseAgent):
    """
    Extend this class if you want to get your game data in protobuf format.
    """
    def get_output_proto(self, game_tick_proto):
        controller_state = game_data_pb2.ControllerState()
        return controller_state
