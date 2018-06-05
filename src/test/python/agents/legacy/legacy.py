import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

URotationToRadians = math.pi / float(32768)


class Legacy(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.field_info = None

    def get_output(self, game_tick_packet: GameTickPacket) -> SimpleControllerState:
        controller_state = SimpleControllerState()

        if self.field_info is None or self.field_info.num_boosts == 0:
            self.field_info = self.get_field_info()

        # testing that conversion works
        legacy = self.convert_packet_to_v3(game_tick_packet, self.field_info)

        ball_location = Vector2(legacy.gameball.Location.X,
                                legacy.gameball.Location.Y)

        my_car = legacy.gamecars[self.index]
        car_location = Vector2(my_car.Location.X, my_car.Location.Y)
        car_direction = get_car_facing_vector(my_car)
        car_to_ball = ball_location - car_location

        steer_correction_radians = car_direction.correction_to(car_to_ball)

        if steer_correction_radians > 0:
            # Positive radians in the unit circle is a turn to the left.
            turn = -1.0  # Negative value for a turn to the left.
        else:
            turn = 1.0

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
    pitch = float(car.Rotation.Pitch)
    yaw = float(car.Rotation.Yaw)

    facing_x = math.cos(pitch * URotationToRadians) * math.cos(yaw * URotationToRadians)
    facing_y = math.cos(pitch * URotationToRadians) * math.sin(yaw * URotationToRadians)

    return Vector2(facing_x, facing_y)
