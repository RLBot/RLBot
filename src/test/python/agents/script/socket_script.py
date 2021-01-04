from rlbot.agents.base_agent import SimpleControllerState
from rlbot.messages.flat.PlayerInputChange import PlayerInputChange
from rlbot.messages.flat.PlayerSpectate import PlayerSpectate
from rlbot.messages.flat.PlayerStatEvent import PlayerStatEvent
from rlbot.socket.socket_manager import SocketRelay


class SampleScript:

    def __init__(self):
        self.socket_relay = SocketRelay()

    def handle_spectate(self, spectate: PlayerSpectate, seconds: float, frame_num: int):
        print(f'Spectating player index {spectate.PlayerIndex()}')
        # Make the bot jump whenever we start spectating them >:)
        controls = SimpleControllerState()
        controls.jump = True
        self.socket_relay.send_player_input(spectate.PlayerIndex(), controls)

    def handle_stat(self, stat: PlayerStatEvent, seconds: float, frame_num: int):
        stat_value = stat.StatType().decode('utf-8')
        print(f'Stat player index {stat.PlayerIndex()}: {stat_value}')

    def input_change(self, change: PlayerInputChange, seconds: float, frame_num: int):
        if change.ControllerState().Jump():
            print(f'Player index {change.PlayerIndex()} is jumping!')

    def run(self):
        self.socket_relay.player_spectate_handlers.append(self.handle_spectate)
        self.socket_relay.player_stat_handlers.append(self.handle_stat)
        self.socket_relay.player_input_change_handlers.append(self.input_change)
        self.socket_relay.connect_and_run(wants_quick_chat=True, wants_game_messages=True, wants_ball_predictions=True)


# You can use this __name__ == '__main__' thing to ensure that the script doesn't start accidentally if you
# merely reference its module from somewhere
if __name__ == '__main__':
    print("Socket script starting...")
    script = SampleScript()
    script.run()
