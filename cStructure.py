import struct
import ctypes
import json

maxBoosts = 50
maxCars = 10

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
                ("bSuperSonic", ctypes.c_bool),
                ("bBot", ctypes.c_bool),
				("PlayerID", ctypes.c_int),
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
                ("bOverTime", ctypes.c_bool)]

# On the c++ side this struct has a long at the beginning for locking.  This flag is removed from this struct so it isn't visible to users.
class GameTickPacket(ctypes.Structure):
	_fields_ = [("gamecars", PlayerInfo * maxCars),
                ("numCars", ctypes.c_int),
                ("gameBoosts", BoostInfo * maxBoosts),
				("numBoosts", ctypes.c_int),
                ("gameball", BallInfo),
				("gameInfo", GameInfo)]
				
class SharedInputs(ctypes.Structure):
	_fields_ = [("GameTickPacket", GameTickPacket)]
				
def printVector3(vector):
	print("(X,Y,Z): " + str(round(vector.X,2)) + "," + str(round(vector.Y,2)) + "," + str(round(vector.Z,2)))
	
def printRotator(rotator):
	print("(Pitch,Yaw,Roll): " + str(rotator.Pitch) + "," + str(rotator.Yaw) + "," + str(rotator.Roll))
	
def printScoreInfo(scoreInfo):
	print("Score:       " + str(scoreInfo.Score))
	print("Goals:       " + str(scoreInfo.Goals))
	print("OwnGoals:    " + str(scoreInfo.OwnGoals))
	print("Assists:     " + str(scoreInfo.Assists))
	print("Saves:       " + str(scoreInfo.Saves))
	print("Shots:       " + str(scoreInfo.Shots))
	print("Demolitions: " + str(scoreInfo.Demolitions))
	
def printPlayerInfo(index, playerInfo):
	print("Car " + str(index))
	print("PlayerID: " + str(playerInfo.PlayerID))
	print("Team: " + str(playerInfo.Team))
	print("Bot: " + str(playerInfo.bBot))
	print("Location:")
	printVector3(playerInfo.Location)
	print("Rotation:")
	printRotator(playerInfo.Rotation)
	print("Velocity:")
	printVector3(playerInfo.Velocity)
	print("Angular Velocity:")
	printVector3(playerInfo.AngularVelocity)
	print("SuperSonic: " + str(playerInfo.bSuperSonic))
	print("Demolished: " + str(playerInfo.bDemolished))
	print("Boost: " + str(playerInfo.Boost))
	print("Score Info: ")
	printScoreInfo(playerInfo.Score)
	
def printBallInfo(ballInfo):
	print("Location:")
	printVector3(ballInfo.Location)
	print("Rotation:")
	printRotator(ballInfo.Rotation)
	print("Velocity:")
	printVector3(ballInfo.Velocity)
	print("Angular Velocity:")
	printVector3(ballInfo.AngularVelocity)
	print("Acceleration:")
	printVector3(ballInfo.Acceleration)
	
def printBoostInfo(index, boostInfo):
	print("Boost Pad " + str(index))
	print("Location:")
	printVector3(boostInfo.Location)
	print("Active: " + str(boostInfo.bActive))
	print("Timer: " + str(boostInfo.Timer))
	
def printGameInfo(gameInfo):
	print("Seconds: " + str(gameInfo.TimeSeconds))
	print("Game Time Remaining: " + str(gameInfo.GameTimeRemaining))
	print("Overtime: " + str(gameInfo.bOverTime))
	
def printGameTickPacket(gameTickPacket):
	print("NumCars: " +  str(gameTickPacket.numCars))
	print("NumBoosts: " +  str(gameTickPacket.numBoosts))
	print()
	printGameInfo(gameTickPacket.gameInfo)
	print()
	print("Ball Info:")
	printBallInfo(gameTickPacket.gameball)
	
	for i in range(gameTickPacket.numCars):
		print()
		printPlayerInfo(i, gameTickPacket.gamecars[i])
	
	for i in range(gameTickPacket.numBoosts):
		print()
		printBoostInfo(i, gameTickPacket.gameBoosts[i])

def gameTickPacketToJson(gameTickPacket):
    return json.dumps(gameTickPacketToDict(gameTickPacket))

def gameTickPacketToDict(gameTickPacket):
    result = {}

    def getdict(struct):
        result = {}
        def get_value(value):
            if (type(value) not in [int, float, bool]) and not bool(value):
                # it's a null pointer
                value = None
            elif hasattr(value, "_length_") and hasattr(value, "_type_"):
                # Probably an array
                #print value
                value = get_array(value)
            elif hasattr(value, "_fields_"):
                # Probably another struct
                value = getdict(value)
            return value
        def get_array(array):
            ar = []
            for value in array:
                value = get_value(value)
                ar.append(value)
            return ar
        for f  in struct._fields_:
            field = f[0]
            value = getattr(struct, field)
            # if the type is not a primitive and it evaluates to False ...
            value = get_value(value)
            result[field] = value
        return result

    result['gamecars'] = []
    result['numCars'] = gameTickPacket.numCars
    for i in range(gameTickPacket.numCars):
        result['gamecars'].append(getdict(gameTickPacket.gamecars[i]))

    result['gameBoosts'] = []
    result['numBoosts'] = gameTickPacket.numBoosts
    for i in range(gameTickPacket.numBoosts):
        result['gameBoosts'].append(getdict(gameTickPacket.gameBoosts[i]))

    result['gameball'] = getdict(gameTickPacket.gameball)
    result['gameInfo'] = getdict(gameTickPacket.gameInfo)
    return result
