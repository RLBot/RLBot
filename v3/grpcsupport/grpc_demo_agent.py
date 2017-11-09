from . import proto_converter
from .protobuf import game_data_pb2_grpc
import grpc
import time

####################################################################################################
# To run this agent successfully, you need to have grpc_demo_server.py running at the same time!
####################################################################################################

class Agent:
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # use self.team to determine what team you are. I will set to "blue" or "orange"
        self.index = index
        self.stub = None
        self.myPort = '34865'

        try:
            self.init_protobuf()
        except Exception as e:
            print("Exception when trying to connect to protobuf server: " + str(e))
            pass

    def init_protobuf(self):
        print("Connecting to protobuf server on port " + self.myPort + '...')
        channel = grpc.insecure_channel('localhost:' + self.myPort)
        self.stub = game_data_pb2_grpc.BotStub(channel)
        grpc.channel_ready_future(channel).result()
        print("Connection to server successful!")

    def get_output_vector(self, game_tick_packet):

        proto = proto_converter.convert_game_tick(game_tick_packet, self.index)

        try:
            controller_state = self.stub.GetControllerState(proto)
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
            print("Exception when calling protobuf server: " + str(e))
            print("Will recreate connection in a few seconds...")
            time.sleep(4)
            try:
                self.init_protobuf()
            except Exception as e:
                print("Reinitialization failed: " + str(e))
                pass

            return [0, 0, 0, 0, 0, 0, 0, 0]  # No motion
