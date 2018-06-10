import math

from rlbot.agents.base_flatbuffer_agent import BaseFlatbufferAgent
from rlbot.agents.base_flatbuffer_agent import SimpleControllerState
from rlbot.messages.flat import GameTickPacket


class FlatBot(BaseFlatbufferAgent):
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        controller_state = SimpleControllerState()

        if packet.Ball() is None:  # This happens during replays
            return controller_state

        ball_location = Vector2(packet.Ball().Physics().Location().X(), packet.Ball().Physics().Location().Y())

        my_car = packet.Players(self.index)
        car_location = Vector2(my_car.Physics().Location().X(), my_car.Physics().Location().Y())
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

        return controller_state


class Vector2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)

    def __str__(self):
        return '({:0.2f}, {:0.2f})'.format(self.x, self.y)

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
    pitch = car.Physics().Rotation().Pitch()
    yaw = car.Physics().Rotation().Yaw()

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)
