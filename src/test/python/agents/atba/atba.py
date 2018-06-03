import math

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_AGENT_HEADER
from rlbot.utils.structures.quick_chats import QuickChats
from rlbot.parsing.custom_config import ConfigObject

URotationToRadians = math.pi / float(32768)


class Atba(BaseAgent):
    flip_turning = False
    cleared = False

    def get_output_vector(self, game_tick_packet):

        ball_location = Vector2(game_tick_packet.game_ball.physics.location.x,
                                game_tick_packet.game_ball.physics.location.y)

        my_car = game_tick_packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_direction = get_car_facing_vector(my_car)
        car_to_ball = ball_location - car_location

        steer_correction_radians = car_direction.correction_to(car_to_ball)

        if steer_correction_radians > 0:
            # Positive radians in the unit circle is a turn to the left.
            turn = -1.0 # Negative value for a turn to the left.
        else:
            turn = 1.0

        if self.flip_turning:
            self.flip_turning = not self.flip_turning
            turn *= -1.0

        if turn == -1.0:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Information_IGotIt)

        car_render_location = [my_car.physics.location.x, my_car.physics.location.y, my_car.physics.location.z]
        ball_render_location = [game_tick_packet.game_ball.physics.location.x,
                                game_tick_packet.game_ball.physics.location.y,
                                game_tick_packet.game_ball.physics.location.z]
        text_render_strX = 'x:' + str(game_tick_packet.game_ball.physics.location.x)
        if not self.cleared:
            self.renderer.begin_rendering()
            color = self.renderer.create_color(121, 121, 0, 121)
            color2 = self.renderer.create_color(255, 0, 255, 255)
            self.renderer.draw_line_2d(100, 100, 1000, 500, self.renderer.black())
            self.renderer.draw_rect_2d(0, 0, 1000, 1000, True, color)
            self.renderer.draw_line_3d((50, 50, 50),
                                       car_render_location, color2).draw_line_2d_3d(100, 100,
                                                                                    car_render_location, color2)
            self.renderer.draw_rect_3d(car_render_location, 100, 100, True, self.renderer.create_color(200, 0, 0, 0))
            self.renderer.draw_string_2d(1000, 500, 10, 10, text_render_strX, self.renderer.white())
            self.renderer.draw_string_3d(ball_render_location, 20, 20, "BALL", self.renderer.black())
            self.renderer.end_rendering()
        if self.cleared:
            self.renderer.clear_screen()

        if my_car.physics.location.x > 0:
            self.cleared = True
        else:
            self.cleared = False

        return [
            1.0,  # throttle
            turn,  # steer
            0.0,  # pitch
            0.0,  # yaw
            0.0,  # roll
            0,  # jump
            0,  # boost
            0  # handbrake
        ]

    def load_config(self, config_header):
        self.flip_turning = config_header.getboolean('flip_turning')

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        config.get_header(BOT_CONFIG_AGENT_HEADER).add_value('flip_turning', bool, default=False,
                                                             description='if true bot will turn opposite way')


class Vector2:
    def __init__(self, x=0, y=0):
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

    facing_x = math.cos(pitch * URotationToRadians) * math.cos(yaw * URotationToRadians)
    facing_y = math.cos(pitch * URotationToRadians) * math.sin(yaw * URotationToRadians)

    return Vector2(facing_x, facing_y)
