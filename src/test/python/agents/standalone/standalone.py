from rlbot.agents.base_agent import SimpleControllerState
from rlbot.agents.standalone.standalone_bot import StandaloneBot, run_bot

from rlbot.utils.structures.game_data_struct import GameTickPacket


class StandaloneTest(StandaloneBot):

    def get_output(self, game_tick_packet: GameTickPacket) -> SimpleControllerState:
        controller_state = SimpleControllerState()
        controller_state.throttle = 1
        controller_state.boost = True
        controller_state.steer = -1 if int(game_tick_packet.game_info.seconds_elapsed) % 2 == 0 else 1
        self.renderer.draw_line_3d((0, 0, 50), (0, 0, 2000), self.renderer.orange())
        return controller_state


if __name__ == '__main__':
    run_bot(StandaloneTest)
