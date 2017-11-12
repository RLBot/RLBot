import ctypes
import mmap

MAX_PLAYERS = 10
MAX_NAME_LENGTH = 32
SHARED_MEMORY_TAG = 'Local\\RLBotInput'


class PlayerConfiguration(ctypes.Structure):
    _fields_ = [("bBot", ctypes.c_bool),
                ("bRLBotControlled", ctypes.c_bool),
                ("fBotSkill", ctypes.c_float),
                ("iPlayerIndex", ctypes.c_int),
                ("wName", ctypes.c_wchar * MAX_NAME_LENGTH),
                ("ucTeam", ctypes.c_ubyte),
                ("ucTeamColorID", ctypes.c_ubyte),
                ("ucCustomColorID", ctypes.c_ubyte),
                ("iCarID", ctypes.c_int),
                ("iDecalID", ctypes.c_int),
                ("iWheelsID", ctypes.c_int),
                ("iBoostID", ctypes.c_int),
                ("iAntennaID", ctypes.c_int),
                ("iHatID", ctypes.c_int),
                ("iPaintFinish1ID", ctypes.c_int),
                ("iPaintFinish2ID", ctypes.c_int),
                ("iEngineAudioID", ctypes.c_int),
                ("iTrailsID", ctypes.c_int),
                ("iGoalExplosionID", ctypes.c_int)]


class PlayerInput(ctypes.Structure):
    _fields_ = [("lock", ctypes.c_long),
                ("fThrottle", ctypes.c_float),
                ("fSteer", ctypes.c_float),
                ("fPitch", ctypes.c_float),
                ("fYaw", ctypes.c_float),
                ("fRoll", ctypes.c_float),
                ("bJump", ctypes.c_bool),
                ("bBoost", ctypes.c_bool),
                ("bHandbrake", ctypes.c_bool)]


class GameInputPacket(ctypes.Structure):
    _fields_ = [("bStartMatch", ctypes.c_bool),
                ("sPlayerConfiguration", PlayerConfiguration * MAX_PLAYERS),
                ("sPlayerInput", PlayerInput * MAX_PLAYERS),
                ("iNumPlayers", ctypes.c_int)]


def print_game_input_packet(gameInputPacket):
    print("PRINTING GAME INPUT PACKET")
    print_struct(gameInputPacket)

    # Print all player configurations
    for i in range(MAX_PLAYERS):
        print("PRINTING PLAYER CONFIGURATION " + str(i))
        print_struct(gameInputPacket.sPlayerConfiguration[i])

    # Print all player configurations
    for i in range(MAX_PLAYERS):
        print("PRINTING PLAYER INPUT " + str(i))
        print_struct(gameInputPacket.sPlayerInput[i])


def print_struct(cStructure):
    for field in cStructure._fields_:
        print((field[0], getattr(cStructure, field[0])))


# Running this file will read from shared memory and display contents
if __name__ == '__main__':
    # Open anonymous shared memory for entire GameInputPacket
    buff = mmap.mmap(-1, ctypes.sizeof(GameInputPacket), SHARED_MEMORY_TAG)

    # Map buffer to ctypes structure
    gameInputPacket = GameInputPacket.from_buffer(buff)

    # gameInputPacket.sPlayerInput[5].fYaw = 1.7 # Example Write

    # Print struct
    print_game_input_packet(gameInputPacket)
