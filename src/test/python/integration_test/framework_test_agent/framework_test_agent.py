from agents.protoBot.protoBot import ProtoAtba
from integration_test.history import HistoryIO

# from quicktracer import trace

'''
An integration test bot
'''

def is_close(x, target, margin):
    return abs(x-target) <= margin


class FrameworkTestAgent(ProtoAtba):
    last_time = None

    def __init__(self, *args, **kwargs):
        self.historyIO = HistoryIO()
        self.historyIO.clear()
        super().__init__(*args, **kwargs)

    def get_output_proto(self, game_tick_proto):
        # now = game_tick_proto.game_info.seconds_elapsed
        # if self.last_time is not None:
        #     trace(now - self.last_time)
        #     pass
        # self.last_time = now

        controller_state = super().get_output_proto(game_tick_proto)
        self.historyIO.append(game_tick_proto, controller_state)
        return controller_state
