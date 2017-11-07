import proto_converter
import game_data_pb2_grpc
import grpc


class Agent:
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # use self.team to determine what team you are. I will set to "blue" or "orange"
        self.index = index
        self.stub = None
        self.myPort = 34865

        try:
            self.init_protobuf()
        except:
            print("Exception when trying to connect to protobuf server! Make sure the server is running!")
            pass

    def init_protobuf(self):
        print("Connecting to protobuf server on port " + str(self.myPort))
        channel = grpc.insecure_channel('localhost:' + self.myPort)
        self.stub = game_data_pb2_grpc.BotStub(channel)
        print("Connection to server successful!")

    def get_output_vector(self, game_tick_packet):

        player_index = 0 if game_tick_packet.gamecars[
                                0].Team == 'blue' else 1  # TODO: the agent should get told this index explicitly

        proto = proto_converter.convert_game_tick(game_tick_packet, player_index)

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
            print("Will recreate connection...")
            try:
                self.init_protobuf()
            except:
                print("Reinitialization failed")
                pass

            return [16383, 16383, 0, 0, 0, 0, 0]  # No motion
