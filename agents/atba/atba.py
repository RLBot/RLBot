import math

from agents.base_agent import BaseAgent

URotationToRadians = math.pi / float(32768)


class Atba(BaseAgent):
    flip_turning = False

    def get_output_vector(self, game_tick_packet):

        ball_location = Vector2(game_tick_packet.gameball.Location.X, game_tick_packet.gameball.Location.Y)

        my_car = game_tick_packet.gamecars[self.index]
        car_location = Vector2(my_car.Location.X, my_car.Location.Y)
        car_direction = get_car_facing_vector(my_car)
        car_to_ball = ball_location - car_location

        steer_correction_radians = car_direction.correction_to(car_to_ball)

        if steer_correction_radians > 0:
            # Positive radians in the unit circle is a turn to the left.
            turn = -1.0 # Negative value for a turn to the left.
        else:
            turn = 1.0

        if self.flip_turning:
            turn *= -1.0

        return [
            1.0, # throttle
            turn, #steer
            0.0, # pitch
            0.0, # yaw
            0.0, # roll
            0, # jump
            0, # boost
            0  # handbrake
        ]

    def load_config(self, config_object):
        self.flip_turning = config_object.getbool('atba', 'flip_turning')

    @staticmethod
    def create_agent_configurations():
        config = super().create_agent_configurations()
        config.add_header_name('atba').add_value('flip_turning', bool, default=False,
                                                 description='if true bot will turn opposite way')
        return config

class Vector2:
    def __init__(self, x = 0, y = 0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2( self.x + val.x, self.y + val.y)

    def __sub__(self,val):
        return Vector2( self.x - val.x, self.y - val.y)

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

    pitch = float(car.Rotation.Pitch)
    yaw = float(car.Rotation.Yaw)

    facing_x = math.cos(pitch * URotationToRadians) * math.cos(yaw * URotationToRadians)
    facing_y = math.cos(pitch * URotationToRadians) * math.sin(yaw * URotationToRadians)

    return Vector2(facing_x, facing_y)
