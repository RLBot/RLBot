import math

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_AGENT_HEADER, SimpleControllerState
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.structures.game_data_struct import GameTickPacket, DropshotTileState
from rlbot.utils.structures.quick_chats import QuickChats


class Atba(BaseAgent):
    flip_turning = False
    test_rendering = False
    test_quickchat = False
    test_dropshot = False
    cleared = False

    def get_output(self, game_tick_packet: GameTickPacket) -> SimpleControllerState:
        controller_state = SimpleControllerState()

        ball_location = Vector2(game_tick_packet.game_ball.physics.location.x,
                                game_tick_packet.game_ball.physics.location.y)

        my_car = game_tick_packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_direction = get_car_facing_vector(my_car)
        car_to_ball = ball_location - car_location

        steer_correction_radians = car_direction.correction_to(car_to_ball)

        if steer_correction_radians > 0:
            # Positive radians in the unit circle is a turn to the left.
            turn = -1.0  # Negative value for a turn to the left.
        else:
            turn = 1.0

        if self.flip_turning:
            turn *= -1.0

        if turn == -1.0 and self.test_quickchat:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Information_IGotIt)

        if self.test_rendering:
            self.do_rendering_test(game_tick_packet, my_car)

        if self.test_dropshot:
            self.do_dropshot_tile_test(game_tick_packet)

        controller_state.throttle = 1.0
        controller_state.steer = turn

        return self.convert_output_to_v4([
            1.0,  # throttle
            turn,  # steer
            0.0,  # pitch
            0.0,  # yaw
            0.0,  # roll
            0,  # jump
            0,  # boost
            0  # handbrake
        ])

    def do_rendering_test(self, game_tick_packet, my_car):
        if self.cleared:
            self.renderer.clear_screen()
        else:
            car_render_location = [my_car.physics.location.x, my_car.physics.location.y, my_car.physics.location.z]
            ball_render_location = [game_tick_packet.game_ball.physics.location.x,
                                    game_tick_packet.game_ball.physics.location.y,
                                    game_tick_packet.game_ball.physics.location.z]
            text_render_strX = 'x:' + str(game_tick_packet.game_ball.physics.location.x)

            self.renderer.begin_rendering()
            color = self.renderer.create_color(121, 121, 0, 121)
            color2 = self.renderer.create_color(255, 0, 255, 255)
            self.renderer.draw_line_2d(100, 100, 1000, 500, self.renderer.black())
            self.renderer.draw_rect_2d(0, 0, 50, 50, True, color)
            self.renderer.draw_line_3d((50, 50, 50),
                                       car_render_location, color2).draw_line_2d_3d(100, 100,
                                                                                    car_render_location, color2)
            self.renderer.draw_rect_3d(car_render_location, 100, 100, True, self.renderer.create_color(200, 0, 0, 0))
            self.renderer.draw_string_2d(1000, 500, 10, 10, text_render_strX, self.renderer.white())
            self.renderer.draw_string_3d(ball_render_location, 20, 20, "BALL", self.renderer.black())
            self.renderer.end_rendering()
        if my_car.physics.location.x > 0:
            self.cleared = True
        else:
            self.cleared = False

    def do_dropshot_tile_test(self, game_tick_packet: GameTickPacket):
        num_tiles = game_tick_packet.num_tiles
        self.renderer.begin_rendering(group_id="dropshot")
        self.renderer.draw_string_2d(50, 400, 10, 10, 'num tiles: ' + str(num_tiles), self.renderer.black())
        if num_tiles > 0:
            num_filled = 0
            num_damaged = 0
            num_open = 0
            num_unknown = 0
            for i in range(num_tiles):
                tile = game_tick_packet.dropshot_tiles[i]
                if tile.tile_state == DropshotTileState.UNKNOWN:
                    num_unknown += 1
                if tile.tile_state == DropshotTileState.FILLED:
                    num_filled += 1
                if tile.tile_state == DropshotTileState.DAMAGED:
                    num_damaged += 1
                if tile.tile_state == DropshotTileState.OPEN:
                    num_open += 1

            self.renderer.draw_string_2d(50, 500, 10, 10, 'num filled: ' + str(num_filled), self.renderer.black())
            self.renderer.draw_string_2d(50, 600, 10, 10, 'num damaged: ' + str(num_damaged), self.renderer.black())
            self.renderer.draw_string_2d(50, 700, 10, 10, 'num open: ' + str(num_open), self.renderer.black())
            self.renderer.draw_string_2d(50, 800, 10, 10, 'num unknown: ' + str(num_unknown), self.renderer.black())

        self.renderer.end_rendering()

    def load_config(self, config_header):
        self.flip_turning = config_header.getboolean('flip_turning')
        self.test_rendering = config_header.getboolean('test_rendering')
        self.test_quickchat = config_header.getboolean('test_quickchat')
        self.test_dropshot = config_header.getboolean('test_dropshot')

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('flip_turning', bool, default=False, description='if true bot will turn opposite way')
        params.add_value('test_rendering', bool, default=False, description='if true bot will render random stuff')
        params.add_value('test_quickchat', bool, default=False, description='if true bot will spam quickchats')
        params.add_value('test_dropshot', bool, default=False, description='if true bot will render dropshot info')

class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)

    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction


def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)
