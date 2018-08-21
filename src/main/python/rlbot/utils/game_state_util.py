import flatbuffers
from rlbot.messages.flat import Float, RotatorPartial, Vector3Partial, DesiredPhysics, DesiredGameState, DesiredCarState, DesiredBallState

from rlbot.utils.logging_utils import get_logger

logger = get_logger("game state")
class Rotator:

    def __init__(self, pitch=None, yaw=None, roll=None):
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

    def convert_to_flat(self, builder=None):
        if builder is None:
            builder = flatbuffers.Builder(0)
        logger.info(("Builder offset:", builder.Offset()))
        pitch_offset = None if self.pitch is None else Float.CreateFloat(builder, self.pitch)
        yaw_offset = None if self.yaw is None else Float.CreateFloat(builder, self.yaw)
        roll_offset = None if self.roll is None else Float.CreateFloat(builder, self.roll)
        logger.info(("Offsets of items:", pitch_offset, yaw_offset, roll_offset))
        logger.info(("New builder offset:", builder.Offset()))

        # Make sure to check if they are not all none, if so just stop
        RotatorPartial.RotatorPartialStart(builder)
        if pitch_offset is not None:
            logger.info(builder.Offset())
            RotatorPartial.RotatorPartialAddPitch(builder, pitch_offset)
        if yaw_offset is not None:
            RotatorPartial.RotatorPartialAddYaw(builder, yaw_offset)
        if roll_offset is not None:
            RotatorPartial.RotatorPartialAddRoll(builder, roll_offset)
        return RotatorPartial.RotatorPartialEnd(builder), builder


class Vector3:

    def __init__(self, x=None, y=None, z=None):
        self.x = x
        self.y = y
        self.z = z

    def convert_to_flat(self, builder=None):
        if builder is None:
            builder = flatbuffers.Builder(0)
        x_offset = None if self.x is None else Float.CreateFloat(builder, self.x)
        y_offset = None if self.y is None else Float.CreateFloat(builder, self.y)
        z_offset = None if self.z is None else Float.CreateFloat(builder, self.z)
        logger.info((x_offset, y_offset, z_offset))

        # Make sure to check if they are not all none, if so just stop
        Vector3Partial.Vector3PartialStart(builder)
        if x_offset is not None:
            Vector3Partial.Vector3PartialAddX(builder, x_offset)
        if y_offset is not None:
            Vector3Partial.Vector3PartialAddY(builder, y_offset)
        if z_offset is not None:
            Vector3Partial.Vector3PartialAddZ(builder, z_offset)
        return Vector3Partial.Vector3PartialEnd(builder), builder


class Physics:

    def __init__(self, location: Vector3=None, rotation: Rotator=None, velocity: Vector3=None, angular_velocity: Vector3=None):
        self.location = location
        self.rotation = rotation
        self.velocity = velocity
        self.angular_velocity = angular_velocity

    def convert_to_flat(self, builder=None):
        if builder is None:
            builder = flatbuffers.Builder(0)
        location_offset = None if self.location is None else self.location.convert_to_flat(builder)[0]
        logger.info(location_offset)
        rotation_offset = None if self.rotation is None else self.rotation.convert_to_flat(builder)[0]
        velocity_offset = None if self.velocity is None else self.velocity.convert_to_flat(builder)[0]
        angular_velocity_offset = None if self.angular_velocity is None else self.angular_velocity.convert_to_flat(builder)[0]

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
        return DesiredPhysics.DesiredPhysicsEnd(builder), builder


class BallState:

    def __init__(self, physics: Physics=None):
        self.physics = physics

    def convert_to_flat(self, builder=None):
        if builder is None:
            builder = flatbuffers.Builder(0)
        physics_offset = None if self.physics is None else self.physics.convert_to_flat(builder)[0]

        if physics_offset is not None:
            # unsure if the start and end should be there
            DesiredBallState.DesiredBallStateStart(builder)
            DesiredBallState.DesiredBallStateAddPhysics(builder, physics_offset)
            return DesiredBallState.DesiredBallStateEnd(builder), builder
        else:
            return None, builder  # Might be a dirty way but the None also gets caught by 'offset is not None'


class CarState:

    def __init__(self, physics: Physics=None):
        self.physics = physics

    def convert_to_flat(self, builder=None):
        if builder is None:
            builder = flatbuffers.Builder(0)
        physics_offset = None if self.physics is None else self.physics.convert_to_flat(builder)[0]

        if physics_offset is not None:
            # unsure if the start and end should be there
            DesiredCarState.DesiredCarStateStart(builder)
            DesiredCarState.DesiredCarStateAddPhysics(builder, physics_offset)
            return DesiredCarState.DesiredCarStateEnd(builder), builder
        else:
            return None, builder  # Might be a dirty way but the None also gets caught by 'offset is not None'


class GameState:

    def __init__(self, ball: BallState=None, cars=None):
        self.ball = ball
        self.cars = cars

    def convert_to_flat(self, builder=None):
        if builder is None:
            builder = flatbuffers.Builder(0)
        ball_offset = None if self.ball is None else self.ball.convert_to_flat(builder)[0]

        car_offsets = []
        if self.cars is not None and (isinstance(self.cars, list) or isinstance(self.cars, tuple)):
            for i in reversed(range(0, len(self.cars))):
                car_offset = self.cars[i].convert_to_flat(builder)[0]
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
        DesiredGameState.DesiredGameStateAddBallState(builder, ball_offset)
        if car_list_offset is not None:
            DesiredGameState.DesiredGameStateAddCarStates(builder, car_list_offset)

        return DesiredGameState.DesiredGameStateEnd(builder), builder


