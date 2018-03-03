import grpc
import time
import msvcrt
import psutil
from . import proto_converter
from .protobuf import game_data_pb2_grpc


def make_grpc_agent(address, port):
    """
        parameters:
            address - address for grpc connection. example: `localhost`
            port - port for grpc connection. example: 34865
        returns:
            A RLBot Agent class which forwards the game_tick_packet to the
            grpc server and returns its response.

        For an example use of this, see: agents/java_demo
    """
    server_address = address + ':' + str(port)

    class GrpcForwardingAgent:
        def __init__(self, name, team, index):
            self.name = name
            self.team = team  # use self.team to determine what team you are. I will set to "blue" or "orange"
            self.index = index
            self.stub = None
            self.connected = False

            try:
                self.init_protobuf()
            except Exception as e:
                print("Exception when trying to connect to grpc server: " + str(e))
                pass

        def get_extra_pids(self):
            while True:
                if msvcrt.kbhit():
                    return []
                for proc in psutil.process_iter():
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            print('gRPC server for {} appears to have pid {}'.format(self.name, proc.pid))
                            return [proc.pid]
                time.sleep(1)

        def init_protobuf(self):
            print("Connecting to grpc server: " + server_address)
            channel = grpc.insecure_channel(server_address)
            self.stub = game_data_pb2_grpc.BotStub(channel)

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
