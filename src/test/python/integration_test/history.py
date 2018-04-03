from collections import namedtuple
from RLBotFramework.grpcsupport.protobuf import game_data_pb2
import os

# I/O adapted from https://www.datadoghq.com/blog/engineering/protobuf-parsing-in-python/
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
def write_proto_to_file(proto, f):
    f.write(_VarintBytes(proto.ByteSize()))
    f.write(proto.SerializeToString())
def read_proto_from_buffer(proto_class, buffer, offset):
    msg_len, offset = _DecodeVarint32(buffer, offset)
    msg_buf = buffer[offset:offset+msg_len]
    offset += msg_len
    proto = proto_class()
    proto.ParseFromString(msg_buf)
    return proto, offset


HistoryItem = namedtuple('HistoryItem', 'game_tick_proto controller_state')

class HistoryIO():

    # Reads and writes stuff to disk.

    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'history.pb.bin')
        self.file_path = file_path

    def clear(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def append(self, game_tick_proto, controller_state):
        assert isinstance(game_tick_proto, game_data_pb2.GameTickPacket)
        assert isinstance(controller_state, game_data_pb2.ControllerState)
        with open(self.file_path, 'ab') as f:
            write_proto_to_file(game_tick_proto, f)
            write_proto_to_file(controller_state, f)

    def get_all_history_items(self):
        history = []
        with open(self.file_path, 'rb') as f:
            buf = f.read()
            n = 0  # our position in the file.
            while n < len(buf):
                game_tick_proto, n = read_proto_from_buffer(game_data_pb2.GameTickPacket, buf, n)
                controller_state, n = read_proto_from_buffer(game_data_pb2.ControllerState, buf, n)
                history.append(HistoryItem(game_tick_proto=game_tick_proto, controller_state=controller_state))
        return history
