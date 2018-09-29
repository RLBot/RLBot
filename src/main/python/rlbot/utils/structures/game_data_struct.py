import ctypes
import math

from rlbot.utils.structures.start_match_structures import MAX_NAME_LENGTH, MAX_PLAYERS

from rlbot.utils.structures.utils import create_enum_object

MAX_BOOSTS = 50
MAX_TILES = 200
MAX_GOALS = 200


class Vector3(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)]


# Note: this is now expressed in radians (it used to be unreal rotation units).
class Rotator(ctypes.Structure):
    _fields_ = [("pitch", ctypes.c_float),
                ("yaw", ctypes.c_float),
                ("roll", ctypes.c_float)]


class Physics(ctypes.Structure):
    _fields_ = [("location", Vector3),
                ("rotation", Rotator),
                ("velocity", Vector3),
                ("angular_velocity", Vector3)]


class Touch(ctypes.Structure):
    _fields_ = [("player_name", ctypes.c_wchar * MAX_NAME_LENGTH),
                ("time_seconds", ctypes.c_float),
                ("hit_location", Vector3),
                ("hit_normal", Vector3)]


class ScoreInfo(ctypes.Structure):
    _fields_ = [("score", ctypes.c_int),
                ("goals", ctypes.c_int),
                ("own_goals", ctypes.c_int),
                ("assists", ctypes.c_int),
                ("saves", ctypes.c_int),
                ("shots", ctypes.c_int),
                ("demolitions", ctypes.c_int)]


class PlayerInfo(ctypes.Structure):
    _fields_ = [("physics", Physics),
                ("score_info", ScoreInfo),
                ("is_demolished", ctypes.c_bool),
                # True if your wheels are on the ground, the wall, or the ceiling. False if you're midair or turtling.
                ("has_wheel_contact", ctypes.c_bool),
                ("is_super_sonic", ctypes.c_bool),
                ("is_bot", ctypes.c_bool),
                # True if the player has jumped. Falling off the ceiling / driving off the goal post does not count.
                ("jumped", ctypes.c_bool),
                # True if player has double jumped. False does not mean you have a jump remaining, because the
                # aerial timer can run out, and that doesn't affect this flag.
                ("double_jumped", ctypes.c_bool),
                ("name", ctypes.c_wchar * MAX_NAME_LENGTH),
                ("team", ctypes.c_ubyte),
                ("boost", ctypes.c_int)]


class DropShotInfo(ctypes.Structure):
    _fields_ = [("absorbed_force", ctypes.c_float),
                ("damage_index", ctypes.c_int),
                ("force_accum_recent", ctypes.c_float)]


class BallInfo(ctypes.Structure):
    _fields_ = [("physics", Physics),
                ("latest_touch", Touch),
                ("drop_shot_info", DropShotInfo)]


class BoostPadState(ctypes.Structure):
    _fields_ = [("is_active", ctypes.c_bool),
                ("timer", ctypes.c_float)]

class TileInfo(ctypes.Structure):
    _fields_ = [("tile_state", ctypes.c_int)]


class GameInfo(ctypes.Structure):
    _fields_ = [("seconds_elapsed", ctypes.c_float),
                ("game_time_remaining", ctypes.c_float),
                ("is_overtime", ctypes.c_bool),
                ("is_unlimited_time", ctypes.c_bool),
                # True when cars are allowed to move, and during the pause menu. False during replays.
                ("is_round_active", ctypes.c_bool),
                # Only false during a kickoff, when the car is allowed to move, and the ball has not been hit,
                # and the game clock has not started yet. If both players sit still, game clock will eventually
                # start and this will become true.
                ("is_kickoff_pause", ctypes.c_bool),
                # Turns true after final replay, the moment the 'winner' screen appears. Remains true during next match
                # countdown. Turns false again the moment the 'choose team' screen appears.
                ("is_match_ended", ctypes.c_bool)]

# On the c++ side this struct has a long at the beginning for locking.  This flag is removed from this struct so it isn't visible to users.
class GameTickPacket(ctypes.Structure):
    _fields_ = [("game_cars", PlayerInfo * MAX_PLAYERS),
                ("num_cars", ctypes.c_int),
                ("game_boosts", BoostPadState * MAX_BOOSTS),
                ("num_boost", ctypes.c_int),
                ("game_ball", BallInfo),
                ("game_info", GameInfo),
                ("dropshot_tiles", TileInfo * MAX_TILES),
                ("num_tiles", ctypes.c_int)]


class BoostPad(ctypes.Structure):
    _fields_ = [("location", Vector3),
                ("is_full_boost", ctypes.c_bool)]


class GoalInfo(ctypes.Structure):
    _fields_ = [("team_num", ctypes.c_ubyte),
                ("location", Vector3),
                ("direction", Vector3)]


class FieldInfoPacket(ctypes.Structure):
    _fields_ = [("boost_pads", BoostPad * MAX_BOOSTS),
                ("num_boosts", ctypes.c_int),
                ("goals", GoalInfo * MAX_GOALS),
                ("num_goals", ctypes.c_int)]


# Helps us return raw bytes from protobuf functions.
class ByteBuffer(ctypes.Structure):
    _fields_ = [("ptr", ctypes.c_void_p),
                ("size", ctypes.c_int)]


# This negates all x and y values for balls and cars and rotates yaw 180 degrees.
def rotate_game_tick_packet_boost_omitted(game_tick_packet):
    # Negate all x,y values for ball
    game_tick_packet.game_ball.physics.location.x = -1 * game_tick_packet.game_ball.physics.location.x
    game_tick_packet.game_ball.physics.location.y = -1 * game_tick_packet.game_ball.physics.location.y
    game_tick_packet.game_ball.physics.velocity.x = -1 * game_tick_packet.game_ball.physics.velocity.x
    game_tick_packet.game_ball.physics.velocity.y = -1 * game_tick_packet.game_ball.physics.velocity.y
    # Angular velocity is stored on global axis so negating on x and y does make sense!
    game_tick_packet.game_ball.physics.angular_velocity.x = -1 * game_tick_packet.game_ball.physics.angular_velocity.x
    game_tick_packet.game_ball.physics.angular_velocity.y = -1 * game_tick_packet.game_ball.physics.angular_velocity.y

    # ball touch data
    game_tick_packet.game_ball.latest_touch.hit_location.x = -1 * game_tick_packet.game_ball.latest_touch.hit_location.x
    game_tick_packet.game_ball.latest_touch.hit_location.y = -1 * game_tick_packet.game_ball.latest_touch.hit_location.y
    game_tick_packet.game_ball.latest_touch.hit_normal.x = -1 * game_tick_packet.game_ball.latest_touch.hit_normal.x
    game_tick_packet.game_ball.latest_touch.hit_normal.y = -1 * game_tick_packet.game_ball.latest_touch.hit_normal.y

    # Rotate yaw 180 degrees is all that is necessary.
    ball_yaw = game_tick_packet.game_ball.physics.rotation.yaw
    game_tick_packet.game_ball.physics.rotation.yaw = ball_yaw + math.pi if ball_yaw < 0 else ball_yaw - math.pi

    for i in range(game_tick_packet.num_cars):
        game_tick_packet.game_cars[i].physics.location.x = -1 * game_tick_packet.game_cars[i].physics.location.x
        game_tick_packet.game_cars[i].physics.location.y = -1 * game_tick_packet.game_cars[i].physics.location.y
        game_tick_packet.game_cars[i].physics.velocity.x = -1 * game_tick_packet.game_cars[i].physics.velocity.x
        game_tick_packet.game_cars[i].physics.velocity.y = -1 * game_tick_packet.game_cars[i].physics.velocity.y
        game_tick_packet.game_cars[i].physics.angular_velocity.x = -1 * game_tick_packet.game_cars[i].physics.angular_velocity.x
        game_tick_packet.game_cars[i].physics.angular_velocity.y = -1 * game_tick_packet.game_cars[i].physics.angular_velocity.y

        car_yaw = game_tick_packet.game_cars[i].physics.rotation.yaw
        game_tick_packet.game_cars[i].physics.rotation.yaw = car_yaw + math.pi if car_yaw < 0 else car_yaw - math.pi


DropshotTileState = create_enum_object(["UNKNOWN",
                                        "FILLED",
                                        "DAMAGED",
                                        "OPEN"])
