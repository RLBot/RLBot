import ctypes
import math

from rlbot.utils.structures import game_data_struct
from rlbot.utils.structures.game_data_struct import MAX_BOOSTS
from rlbot.utils.structures.start_match_structures import MAX_NAME_LENGTH, MAX_PLAYERS

UNREAL_ROT_PER_RADIAN = 32768 / math.pi


class Vector3(ctypes.Structure):
    _fields_ = [("X", ctypes.c_float),
                ("Y", ctypes.c_float),
                ("Z", ctypes.c_float)]


class Rotator(ctypes.Structure):
    _fields_ = [("Pitch", ctypes.c_int),
                ("Yaw", ctypes.c_int),
                ("Roll", ctypes.c_int)]


class Touch(ctypes.Structure):
    _fields_ = [("wPlayerName", ctypes.c_wchar * MAX_NAME_LENGTH),
                ("fTimeSeconds", ctypes.c_float),
                ("sHitLocation", Vector3),
                ("sHitNormal", Vector3)]


class ScoreInfo(ctypes.Structure):
    _fields_ = [("Score", ctypes.c_int),
                ("Goals", ctypes.c_int),
                ("OwnGoals", ctypes.c_int),
                ("Assists", ctypes.c_int),
                ("Saves", ctypes.c_int),
                ("Shots", ctypes.c_int),
                ("Demolitions", ctypes.c_int)]


class PlayerInfo(ctypes.Structure):
    _fields_ = [("Location", Vector3),
                ("Rotation", Rotator),
                ("Velocity", Vector3),
                ("AngularVelocity", Vector3),
                ("Score", ScoreInfo),
                ("bDemolished", ctypes.c_bool),
                # True if your wheels are on the ground, the wall, or the ceiling. False if you're midair or turtling.
                ("bOnGround", ctypes.c_bool),
                ("bSuperSonic", ctypes.c_bool),
                ("bBot", ctypes.c_bool),
                # True if the player has jumped. Falling off the ceiling / driving off the goal post does not count.
                ("bJumped", ctypes.c_bool),
                # True if player has double jumped. False does not mean you have a jump remaining, because the
                # aerial timer can run out, and that doesn't affect this flag.
                ("bDoubleJumped", ctypes.c_bool),
                ("wName", ctypes.c_wchar * MAX_NAME_LENGTH),
                ("Team", ctypes.c_ubyte),
                ("Boost", ctypes.c_int)]


class BallInfo(ctypes.Structure):
    _fields_ = [("Location", Vector3),
                ("Rotation", Rotator),
                ("Velocity", Vector3),
                ("AngularVelocity", Vector3),
                ("Acceleration", Vector3),
                ("LatestTouch", Touch)]


class BoostInfo(ctypes.Structure):
    _fields_ = [("Location", Vector3),
                ("bActive", ctypes.c_bool),
                ("Timer", ctypes.c_float)]


class GameInfo(ctypes.Structure):
    _fields_ = [("TimeSeconds", ctypes.c_float),
                ("GameTimeRemaining", ctypes.c_float),
                ("bOverTime", ctypes.c_bool),
                ("bUnlimitedTime", ctypes.c_bool),
                # True when cars are allowed to move, and during the pause menu. False during replays.
                ("bRoundActive", ctypes.c_bool),
                # Only false during a kickoff, when the car is allowed to move, and the ball has not been hit,
                # and the game clock has not started yet. If both players sit still, game clock will eventually
                # start and this will become true.
                ("bBallHasBeenHit", ctypes.c_bool),
                # Turns true after final replay, the moment the 'winner' screen appears. Remains true during next match
                # countdown. Turns false again the moment the 'choose team' screen appears.
                ("bMatchEnded", ctypes.c_bool)]


# On the c++ side this struct has a long at the beginning for locking.
# This flag is removed from this struct so it isn't visible to users.
class GameTickPacket(ctypes.Structure):
    _fields_ = [("gamecars", PlayerInfo * MAX_PLAYERS),
                ("numCars", ctypes.c_int),
                ("gameBoosts", BoostInfo * MAX_BOOSTS),
                ("numBoosts", ctypes.c_int),
                ("gameball", BallInfo),
                ("gameInfo", GameInfo)]


def convert_to_legacy_v3(
        game_tick_packet: game_data_struct.GameTickPacket,
        field_info_packet: game_data_struct.FieldInfoPacket = None):
    """
    Returns a legacy packet from v3
    :param game_tick_packet a game tick packet in the v4 struct format.
    :param field_info_packet a field info packet in the v4 struct format. Optional. If this is not supplied,
    none of the boost locations will be filled in.
    """
    legacy_packet = GameTickPacket()

    legacy_packet.numBoosts = game_tick_packet.num_boost
    legacy_packet.numCars = game_tick_packet.num_cars

    for i in range(game_tick_packet.num_cars):
        convert_player_info(legacy_packet.gamecars[i], game_tick_packet.game_cars[i])

    for i in range(game_tick_packet.num_boost):
        convert_boost_info(legacy_packet.gameBoosts[i], game_tick_packet.game_boosts[i])
        if field_info_packet is not None:
            convert_vector(legacy_packet.gameBoosts[i].Location, field_info_packet.boost_pads[i].location)

    convert_ball_info(legacy_packet.gameball, game_tick_packet.game_ball)

    convert_game_info(legacy_packet.gameInfo, game_tick_packet.game_info)

    return legacy_packet


def convert_game_info(legacy_game_info, game_info):
    legacy_game_info.TimeSeconds = game_info.seconds_elapsed
    legacy_game_info.GameTimeRemaining = game_info.game_time_remaining
    legacy_game_info.bOverTime = game_info.is_overtime
    legacy_game_info.bUnlimitedTime = game_info.is_unlimited_time
    legacy_game_info.bRoundActive = game_info.is_round_active
    legacy_game_info.bBallHasBeenHit = not game_info.is_kickoff_pause
    legacy_game_info.bMatchEnded = game_info.is_match_ended


def convert_player_info(legacy_player_info, player_info):
    convert_vector(legacy_player_info.Location, player_info.physics.location)
    convert_rotator(legacy_player_info.Rotation, player_info.physics.rotation)
    convert_vector(legacy_player_info.Velocity, player_info.physics.velocity)
    convert_vector(legacy_player_info.AngularVelocity, player_info.physics.angular_velocity)

    # score
    legacy_player_info.Score.Score = player_info.score_info.score
    legacy_player_info.Score.Goals = player_info.score_info.goals
    legacy_player_info.Score.Saves = player_info.score_info.saves
    legacy_player_info.Score.Shots = player_info.score_info.shots
    legacy_player_info.Score.Assists = player_info.score_info.assists
    legacy_player_info.Score.OwnGoals = player_info.score_info.own_goals
    legacy_player_info.Score.Demolitions = player_info.score_info.demolitions

    legacy_player_info.bDemolished = player_info.is_demolished
    legacy_player_info.bOnGround = player_info.has_wheel_contact
    legacy_player_info.bSuperSonic = player_info.is_super_sonic
    legacy_player_info.bBot = player_info.is_bot
    legacy_player_info.bJumped = player_info.jumped
    legacy_player_info.bDoubleJumped = player_info.double_jumped
    legacy_player_info.wName = player_info.name
    legacy_player_info.Team = player_info.team
    legacy_player_info.Boost = player_info.boost


def convert_ball_info(legacy_ball_info, ball_info):
    convert_vector(legacy_ball_info.Location, ball_info.physics.location)
    convert_rotator(legacy_ball_info.Rotation, ball_info.physics.rotation)
    convert_vector(legacy_ball_info.Velocity, ball_info.physics.velocity)
    convert_vector(legacy_ball_info.AngularVelocity, ball_info.physics.angular_velocity)
    legacy_ball_info.LatestTouch.wPlayerName = ball_info.latest_touch.player_name
    legacy_ball_info.LatestTouch.fTimeSeconds = ball_info.latest_touch.time_seconds
    convert_vector(legacy_ball_info.LatestTouch.sHitLocation, ball_info.latest_touch.hit_location)
    convert_vector(legacy_ball_info.LatestTouch.sHitNormal, ball_info.latest_touch.hit_normal)


def convert_boost_info(legacy_boost_info, boost_info):
    legacy_boost_info.bActive = boost_info.is_active
    legacy_boost_info.Timer = boost_info.timer


def convert_vector(legacy_vector, vector):
    legacy_vector.X = vector.x
    legacy_vector.Y = vector.y
    legacy_vector.Z = vector.z


def convert_rotator(legacy_rotator, rotator):
    legacy_rotator.Pitch = int(rotator.pitch * UNREAL_ROT_PER_RADIAN)
    legacy_rotator.Yaw = int(rotator.yaw * UNREAL_ROT_PER_RADIAN)
    legacy_rotator.Roll = int(rotator.roll * UNREAL_ROT_PER_RADIAN)
