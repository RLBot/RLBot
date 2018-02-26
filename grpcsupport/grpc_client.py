import grpc
import time
from . import proto_converter
from .protobuf import game_data_pb2_grpc
from agents.base_agent import BaseAgent


def make_grpc_agent(server_address):
    """
        parameters:
            server_address - grpc target string. example: 'localhost:34865'
        returns:
            A RLBot Agent class which forwards the game_tick_packet to the
            grpc server and returns its response.

        For an example use of this, see: agents/java_demo
    """

    class GrpcForwardingAgent(BaseAgent):
        def __init__(self, name, team, index):
            super().__init__(name, team, index)
            self.stub = None
            self.connected = False
            self.init_protobuf()

        def init_protobuf(self):
            try:
                print("Connecting to grpc server: " + server_address)
                channel = grpc.insecure_channel(server_address)
                self.stub = game_data_pb2_grpc.BotStub(channel)
            except Exception as e:
                print("Exception when trying to connect to grpc server: " + str(e))
                pass

        def get_output_vector(self, game_tick_packet):

            proto = proto_converter.convert_game_tick(game_tick_packet, self.index)

            try:
                controller_state = self.stub.GetControllerState(proto, timeout=1)

                if not self.connected:
                    print("Connected to grpc server successfully!")
                    self.connected = True

                return [
                    controller_state.throttle,
                    controller_state.steer,
                    controller_state.pitch,
                    controller_state.yaw,
                    controller_state.roll,
                    controller_state.jump,
                    controller_state.boost,
                    controller_state.handbrake
                ]
            except Exception as e:
                print("Exception when calling grpc server: " + str(e))
                print("Will try again in a few seconds...")
                self.connected = False
                time.sleep(4)

                return [0, 0, 0, 0, 0, 0, 0, 0]  # No motion

    return GrpcForwardingAgent
