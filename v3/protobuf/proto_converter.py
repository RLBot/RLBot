import game_data_pb2
import math

to_radians_conversion = math.PI / 32768

def convert_game_tick(game_tick_packet, player_index):

    proto = game_data_pb2.GameTickPacket()

    for i in range(game_tick_packet.numCars):
        game_tick_player = game_tick_packet.gamecars[i]
        player = proto.players.add()
        convert_player_info(game_tick_player, player)

    proto.player_index = player_index

    for i in range(game_tick_packet.numBoosts):
        game_tick_boost = game_tick_packet.gameBoosts[i]
        boost = proto.boost_pads.add()
        convert_boost_pad(game_tick_boost, boost)

    proto.ball = convert_ball(game_tick_packet.gameball)
    proto.game_info = convert_game_info(game_tick_packet.gameInfo)


def convert_ball(ball):
    proto_ball = game_data_pb2.BallInfo()
    proto_ball.location = convert_vector3(ball.Location)
    proto_ball.rotation = convert_rotator(ball.Rotation)
    proto_ball.velocity = convert_vector3(ball.Velocity)
    proto_ball.angular_velocity = convert_rotator(ball.AngularVelocity)
    proto_ball.acceleration = convert_vector3(ball.Acceleration)
    return proto_ball

def convert_game_info(gameInfo):
    proto_info = game_data_pb2.GameInfo()
    proto_info.seconds_elapsed = gameInfo.TimeSeconds
    proto_info.game_time_remaining = gameInfo.GameTimeRemaining
    proto_info.is_overtime = gameInfo.bOverTime
    proto_info.is_unlimited_time = gameInfo.bUnlimitedTime
    proto_info.is_round_active = gameInfo.bRoundActive
    proto_info.is_kickoff_pause = not gameInfo.bBallHasBeenHit
    proto_info.is_match_ended = gameInfo.bMatchEnded
    return proto_info

def convert_vector3(vector3):
    proto_vec = game_data_pb2.Vector3()
    proto_vec.x = vector3.X
    proto_vec.y = vector3.Y
    proto_vec.z = vector3.Z
    return proto_vec

def convert_rotator(rotator):
    proto_rot = game_data_pb2.Rotator()
    proto_rot.pitch = rotator.Pitch * to_radians_conversion
    proto_rot.yaw = rotator.Yaw * to_radians_conversion
    proto_rot.roll = rotator.Roll * to_radians_conversion
    return proto_rot

def convert_score_info(info):
    proto_score = game_data_pb2.ScoreInfo()
    proto_score.score = info.Score
    proto_score.goals = info.Goals
    proto_score.own_goals = info.OwnGoals
    proto_score.assists = info.Assists
    proto_score.saves = info.Saves
    proto_score.shots = info.Shots
    proto_score.demolitions = info.Demolitions
    return proto_score

def convert_player_info(tick_info, proto_info):
    proto_info.location = convert_vector3(tick_info.Location)
    proto_info.rotation = convert_rotator(tick_info.Rotation)
    proto_info.velocity = convert_vector3(tick_info.Velocity)
    proto_info.angular_velocity = convert_rotator(tick_info.AngularVelocity)
    proto_info.score_info = convert_score_info(tick_info.ScoreInfo)
    proto_info.is_demolished = tick_info.bDemolished
    proto_info.is_midair = not tick_info.bOnGround
    proto_info.is_supersonic = tick_info.bSuperSonic
    proto_info.is_bot = tick_info.bBot
    proto_info.jumped = tick_info.bJumped
    proto_info.double_jumped = tick_info.bDoubleJumped
    proto_info.name = tick_info.wName
    proto_info.team = tick_info.Team
    proto_info.boost = tick_info.Boost
    return proto_info

def convert_boost_pad(tick_boost, proto_boost):
    proto_boost.location = convert_vector3(tick_boost.Location)
    proto_boost.is_active = tick_boost.bActive
    proto_boost.timer = tick_boost.Timer
    return proto_boost
