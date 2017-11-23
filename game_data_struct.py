import ctypes
import mmap

MAX_PLAYERS = 10
MAX_NAME_LENGTH = 32
MAX_BOOSTS = 50
SHARED_MEMORY_TAG = 'Local\\RLBotOutput'


class Vector3(ctypes.Structure):
    _fields_ = [("X", ctypes.c_float),
                ("Y", ctypes.c_float),
                ("Z", ctypes.c_float)]


class Rotator(ctypes.Structure):
    _fields_ = [("Pitch", ctypes.c_int),
                ("Yaw", ctypes.c_int),
                ("Roll", ctypes.c_int)]


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
                ("Acceleration", Vector3)]


class BoostInfo(ctypes.Structure):
    _fields_ = [("Location", Vector3),
                ("bActive", ctypes.c_bool),
                ("Timer", ctypes.c_int)]


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


# On the c++ side this struct has a long at the beginning for locking.  This flag is removed from this struct so it isn't visible to users.
class GameTickPacket(ctypes.Structure):
    _fields_ = [("gamecars", PlayerInfo * MAX_PLAYERS),
                ("numCars", ctypes.c_int),
                ("gameBoosts", BoostInfo * MAX_BOOSTS),
                ("numBoosts", ctypes.c_int),
                ("gameball", BallInfo),
                ("gameInfo", GameInfo)]


# Fully matching c++ struct
class GameTickPacketWithLock(ctypes.Structure):
    _fields_ = [("lock", ctypes.c_long),
                ("gamecars", PlayerInfo * MAX_PLAYERS),
                ("numCars", ctypes.c_int),
                ("gameBoosts", BoostInfo * MAX_BOOSTS),
                ("numBoosts", ctypes.c_int),
                ("gameball", BallInfo),
                ("gameInfo", GameInfo)]


def print_vector_3(vector):
    print("(X,Y,Z): " + str(round(vector.X, 2)) + "," + str(round(vector.Y, 2)) + "," + str(round(vector.Z, 2)))


def print_rotator(rotator):
    print("(Pitch,Yaw,Roll): " + str(rotator.Pitch) + "," + str(rotator.Yaw) + "," + str(rotator.Roll))


def print_score_info(scoreInfo):
    print("Score:       " + str(scoreInfo.Score))
    print("Goals:       " + str(scoreInfo.Goals))
    print("OwnGoals:    " + str(scoreInfo.OwnGoals))
    print("Assists:     " + str(scoreInfo.Assists))
    print("Saves:       " + str(scoreInfo.Saves))
    print("Shots:       " + str(scoreInfo.Shots))
    print("Demolitions: " + str(scoreInfo.Demolitions))


def print_player_info(index, playerInfo):
    print("Car " + str(index))
    print("Name: " + str(playerInfo.wName))
    print("Team: " + str(playerInfo.Team))
    print("Bot: " + str(playerInfo.bBot))
    print("Location:")
    print_vector_3(playerInfo.Location)
    print("Rotation:")
    print_rotator(playerInfo.Rotation)
    print("Velocity:")
    print_vector_3(playerInfo.Velocity)
    print("Angular Velocity:")
    print_vector_3(playerInfo.AngularVelocity)
    print("SuperSonic: " + str(playerInfo.bSuperSonic))
    print("Demolished: " + str(playerInfo.bDemolished))
    print("Boost: " + str(playerInfo.Boost))
    print("Score Info: ")
    print_score_info(playerInfo.Score)


def print_ball_info(ballInfo):
    print("Location:")
    print_vector_3(ballInfo.Location)
    print("Rotation:")
    print_rotator(ballInfo.Rotation)
    print("Velocity:")
    print_vector_3(ballInfo.Velocity)
    print("Angular Velocity:")
    print_vector_3(ballInfo.AngularVelocity)
    print("Acceleration:")
    print_vector_3(ballInfo.Acceleration)


def print_boost_info(index, boostInfo):
    print("Boost Pad " + str(index))
    print("Location:")
    print_vector_3(boostInfo.Location)
    print("Active: " + str(boostInfo.bActive))
    print("Timer: " + str(boostInfo.Timer))


def print_game_info(gameInfo):
    print("Seconds: " + str(gameInfo.TimeSeconds))
    print("Game Time Remaining: " + str(gameInfo.GameTimeRemaining))
    print("Overtime: " + str(gameInfo.bOverTime))


def print_game_tick_packet_with_lock(gameTickPacket):
    print("Lock: " + str(gameTickPacket.lock))
    print("NumCars: " + str(gameTickPacket.numCars))
    print("NumBoosts: " + str(gameTickPacket.numBoosts))
    print()
    print_game_info(gameTickPacket.gameInfo)
    print()
    print("Ball Info:")
    print_ball_info(gameTickPacket.gameball)

    for i in range(gameTickPacket.numCars):
        print()
        print_player_info(i, gameTickPacket.gamecars[i])

    for i in range(gameTickPacket.numBoosts):
        print()
        print_boost_info(i, gameTickPacket.gameBoosts[i])


# Running this file will read from shared memory and display contents
if __name__ == '__main__':
    # Open anonymous shared memory for entire GameInputPacket
    buff = mmap.mmap(-1, ctypes.sizeof(GameTickPacketWithLock), SHARED_MEMORY_TAG)

    # Map buffer to ctypes structure
    gameOutputPacket = GameTickPacketWithLock.from_buffer(buff)

    # gameOutputPacket.numCars = 10 # Example write
    # gameOutputPacket.numBoosts = 50 # Example write

    # Print struct
    print_game_tick_packet_with_lock(gameOutputPacket)
