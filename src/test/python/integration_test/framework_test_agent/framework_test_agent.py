from agents.flatBot.flatBot import FlatBot
from integration_test.history import HistoryIO

'''
An integration test bot which writes the packets it gets to disk.
'''


class FrameworkTestAgent(FlatBot):
    last_time = None

    def __init__(self, *args, **kwargs):
        self.historyIO = HistoryIO()
        self.historyIO.clear()
        self.game_tick_flat_binary = None
        super().__init__(*args, **kwargs)

    def set_flatbuffer_binary(self, game_tick_flat_binary):
        self.game_tick_flat_binary = game_tick_flat_binary

    def get_output_flatbuffer(self, game_tick_flatbuffer):
        builder = super().get_output_flatbuffer(game_tick_flatbuffer)
        self.historyIO.append(self.game_tick_flat_binary, builder.Output())
        return builder
