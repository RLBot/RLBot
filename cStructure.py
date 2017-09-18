import struct
import ctypes

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
				
class CarInfo(ctypes.Structure):
	_fields_ = [("Location", Vector3),
                ("Rotation", Rotator),
                ("Velocity", Vector3),
				("Score", ScoreInfo),
                ("SuperSonic", ctypes.c_bool),
                ("Bot", ctypes.c_bool),
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
                ("Active", ctypes.c_bool),
                ("Timer", ctypes.c_int)]
				
class GameTickPacket(ctypes.Structure):
	_fields_ = [("CarInfo", CarInfo * maxCars),
                ("numCars", ctypes.c_int),
                ("BoostInfo", BoostInfo * maxBoosts),
				("numBoosts", ctypes.c_int),
                ("gameBall", BallInfo)]
				
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
	
def printCarInfo(index, carInfo):
	print("Car " + str(index))
	print("PlayerID: " + str(carInfo.PlayerID))
	print("Team: " + str(carInfo.Team))
	print("Bot: " + str(carInfo.Bot))
	print("Location:")
	printVector3(carInfo.Location)
	print("Rotation:")
	printRotator(carInfo.Rotation)
	print("Velocity:")
	printVector3(carInfo.Velocity)
	print("SuperSonic: " + str(carInfo.SuperSonic))
	print("Boost: " + str(carInfo.Boost))
	print("Score Info: ")
	printScoreInfo(carInfo.Score)
	
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
	print("Active: " + str(boostInfo.Active))
	print("Timer: " + str(boostInfo.Timer))
	
def printGameTickPacket(gameTickPacket):
	print("NumCars: " +  str(gameTickPacket.numCars))
	print("NumBoosts: " +  str(gameTickPacket.numBoosts))
	print()
	print("Ball Info:")
	printBallInfo(gameTickPacket.gameBall)
	
	for i in range(gameTickPacket.numCars):
		print()
		printCarInfo(i, gameTickPacket.CarInfo[i])
	
	for i in range(gameTickPacket.numBoosts):
		print()
		printBoostInfo(i, gameTickPacket.BoostInfo[i])