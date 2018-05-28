import base64
import os
import json
from collections import namedtuple

from rlbot.messages.flat.GameTickPacket import GameTickPacket
from rlbot.messages.flat.PlayerInput import PlayerInput


def read_game_tick_from_buffer(buf):
    packet = GameTickPacket.GetRootAsGameTickPacket(buf, 0)
    return packet


def read_controller_input_from_buffer(buf):
    player_input = PlayerInput.GetRootAsPlayerInput(buf, 0)
    return player_input


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

    def append(self, game_tick_proto, player_input):
        with open(self.file_path, 'a') as f:
            f.write(json.dumps({
                'tick': base64.b64encode(game_tick_proto).decode('ascii'),
                'input': base64.b64encode(player_input).decode('ascii')
            }))
            f.write('\n')

    def get_all_history_items(self):
        history = []
        with open(self.file_path, 'r') as f:

            for line in f:
                data = json.loads(line)

                game_tick_proto_binary = base64.b64decode(data['tick'])
                game_tick_proto = read_game_tick_from_buffer(game_tick_proto_binary)

                player_input_binary = base64.b64decode(data['input'])
                controller_state = read_controller_input_from_buffer(player_input_binary)

                history.append(HistoryItem(game_tick_proto=game_tick_proto, controller_state=controller_state))

        return history
