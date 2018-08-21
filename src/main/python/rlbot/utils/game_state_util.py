import flatbuffers
from rlbot.messages.flat import Float, RotatorPartial, Vector3Partial, DesiredPhysics, DesiredGameState, \
    DesiredCarState, DesiredBallState

from rlbot.utils.logging_utils import get_logger

logger = get_logger("game state")


class Rotator:

    def __init__(self, pitch=None, yaw=None, roll=None):
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

    def convert_to_flat(self, builder):

        # Make sure to check if they are not all none, if so just stop
        RotatorPartial.RotatorPartialStart(builder)
        if self.pitch is not None:
            RotatorPartial.RotatorPartialAddPitch(builder, Float.CreateFloat(builder, self.pitch))
        if self.yaw is not None:
            RotatorPartial.RotatorPartialAddYaw(builder, Float.CreateFloat(builder, self.yaw))
        if self.roll is not None:
            RotatorPartial.RotatorPartialAddRoll(builder, Float.CreateFloat(builder, self.roll))
        return RotatorPartial.RotatorPartialEnd(builder)


class Vector3:

    def __init__(self, x=None, y=None, z=None):
        self.x = x
        self.y = y
        self.z = z

    def convert_to_flat(self, builder):

        # Make sure to check if they are not all none, if so just stop
        Vector3Partial.Vector3PartialStart(builder)
        if self.x is not None:
            Vector3Partial.Vector3PartialAddX(builder, Float.CreateFloat(builder, self.x))
        if self.y is not None:
            Vector3Partial.Vector3PartialAddY(builder, Float.CreateFloat(builder, self.y))
        if self.z is not None:
            Vector3Partial.Vector3PartialAddZ(builder, Float.CreateFloat(builder, self.z))
        return Vector3Partial.Vector3PartialEnd(builder)


class Physics:

    def __init__(self, location: Vector3 = None, rotation: Rotator = None, velocity: Vector3 = None,
                 angular_velocity: Vector3 = None):
        self.location = location
        self.rotation = rotation
        self.velocity = velocity
        self.angular_velocity = angular_velocity

    def convert_to_flat(self, builder):
        location_offset = None if self.location is None else self.location.convert_to_flat(builder)
        logger.info(location_offset)
        rotation_offset = None if self.rotation is None else self.rotation.convert_to_flat(builder)
        velocity_offset = None if self.velocity is None else self.velocity.convert_to_flat(builder)
        angular_velocity_offset = None if self.angular_velocity is None else self.angular_velocity.convert_to_flat(
            builder)

        # Make sure to check if they are not all none, if so just stop
        DesiredPhysics.DesiredPhysicsStart(builder)
        if location_offset is not None:
            DesiredPhysics.DesiredPhysicsAddLocation(builder, location_offset)
        if rotation_offset is not None:
            DesiredPhysics.DesiredPhysicsAddRotation(builder, rotation_offset)
        if velocity_offset is not None:
            DesiredPhysics.DesiredPhysicsAddVelocity(builder, velocity_offset)
        if angular_velocity_offset is not None:
            DesiredPhysics.DesiredPhysicsAddAngularVelocity(builder, angular_velocity_offset)
        return DesiredPhysics.DesiredPhysicsEnd(builder)


class BallState:

    def __init__(self, physics: Physics = None):
        self.physics = physics

    def convert_to_flat(self, builder):
        physics_offset = None if self.physics is None else self.physics.convert_to_flat(builder)

        if physics_offset is not None:
            # unsure if the start and end should be there
            DesiredBallState.DesiredBallStateStart(builder)
            DesiredBallState.DesiredBallStateAddPhysics(builder, physics_offset)
            return DesiredBallState.DesiredBallStateEnd(builder)
        else:
            return None  # Might be a dirty way but the None also gets caught by 'offset is not None'


class CarState:

    def __init__(self, physics: Physics = None):
        self.physics = physics

    def convert_to_flat(self, builder):

        physics_offset = None if self.physics is None else self.physics.convert_to_flat(builder)

        if physics_offset is not None:
            # unsure if the start and end should be there
            DesiredCarState.DesiredCarStateStart(builder)
            DesiredCarState.DesiredCarStateAddPhysics(builder, physics_offset)
            return DesiredCarState.DesiredCarStateEnd(builder)
        else:
            return None  # Might be a dirty way but the None also gets caught by 'offset is not None'


class GameState:

    def __init__(self, ball: BallState = None, cars=None):
        self.ball = ball
        self.cars = cars

    def convert_to_flat(self, builder=None):
        if builder is None:
            builder = flatbuffers.Builder(0)
        ball_offset = None if self.ball is None else self.ball.convert_to_flat(builder)

        car_offsets = []
        if self.cars is not None and (isinstance(self.cars, list) or isinstance(self.cars, tuple)):
            for i in reversed(range(0, len(self.cars))):
                car_offset = self.cars[i].convert_to_flat(builder)
                if car_offset is not None:
                    car_offsets.append(car_offset)

        car_list_offset = None
        if len(car_offsets) > 0:
            DesiredGameState.DesiredGameStateStartCarStatesVector(builder, len(car_offsets))
            for i in reversed(range(0, len(car_offsets))):
                builder.PrependUOffsetTRelative(car_offsets[i])
            car_list_offset = builder.EndVector(len(car_offsets))
            print(len(car_offsets))

        # IDK if order is right over here
        DesiredGameState.DesiredGameStateStart(builder)
        if ball_offset is not None:
            DesiredGameState.DesiredGameStateAddBallState(builder, ball_offset)
        if car_list_offset is not None:
            DesiredGameState.DesiredGameStateAddCarStates(builder, car_list_offset)

        return DesiredGameState.DesiredGameStateEnd(builder)
