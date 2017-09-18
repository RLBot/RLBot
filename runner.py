from multiprocessing import Process, Array, Queue, Value

import time
import atexit
import realTimeDisplay
import ReadWriteMem
import PlayHelper
import configparser
import importlib
import cStructure
import ctypes
import mmap
import math
import numpy as np

def convert_new_input_to_old_input(sharedValue):
	
		UU_TO_GAMEVALUES = 50
		
		UCONST_Pi = 3.1415926
		URotation180 = float(32768)
		URotationToRadians = UCONST_Pi / URotation180 
	
		inputs = np.zeros(38)
		scoring = np.zeros(12)
	
		gameTickPacket = sharedValue.GameTickPacket
		
		numCars = gameTickPacket.numCars
		numBoosts = gameTickPacket.numBoosts
		
		team1Blue = (gameTickPacket.CarInfo[0].Team == 0)
		
		if team1Blue:
			blueIndex = 0
			orngIndex = 1
		else:
			blueIndex = 1
			orngIndex = 0
		
		# -------------------------------
		# First convert ball info
		# -------------------------------
		
		# Ball positions
		inputs[2] = gameTickPacket.gameBall.Location.Y / UU_TO_GAMEVALUES
		inputs[7] = gameTickPacket.gameBall.Location.X / UU_TO_GAMEVALUES
		inputs[17] = gameTickPacket.gameBall.Location.Z / UU_TO_GAMEVALUES
		
		# Ball velocities
		inputs[28] = gameTickPacket.gameBall.Velocity.X  / UU_TO_GAMEVALUES
		inputs[29] = gameTickPacket.gameBall.Velocity.Z  / UU_TO_GAMEVALUES
		inputs[30] = gameTickPacket.gameBall.Velocity.Y  / UU_TO_GAMEVALUES
		
		# -------------------------------
		# Now do all scoreboard values
		# -------------------------------
		scoring[0] = gameTickPacket.CarInfo[blueIndex].Score.Goals + gameTickPacket.CarInfo[1].Score.OwnGoals # Blue Scoreboard Score
		scoring[1] = gameTickPacket.CarInfo[orngIndex].Score.Goals + gameTickPacket.CarInfo[0].Score.OwnGoals # Orange Scoreboard Score
		scoring[2] = gameTickPacket.CarInfo[orngIndex].Score.Demolitions # Demos by orange
		scoring[3] = gameTickPacket.CarInfo[blueIndex].Score.Demolitions # Demos by blue
		scoring[4] = gameTickPacket.CarInfo[blueIndex].Score.Score # Blue points
		scoring[5] = gameTickPacket.CarInfo[orngIndex].Score.Score # Orange points
		scoring[6] = gameTickPacket.CarInfo[blueIndex].Score.Goals # Blue Goals
		scoring[7] = gameTickPacket.CarInfo[blueIndex].Score.Saves # Blue Saves
		scoring[8] = gameTickPacket.CarInfo[blueIndex].Score.Shots # Blue Shots
		scoring[9] = gameTickPacket.CarInfo[orngIndex].Score.Goals # Orange Goals
		scoring[10] = gameTickPacket.CarInfo[orngIndex].Score.Saves # Orange Saves
		scoring[11] = gameTickPacket.CarInfo[orngIndex].Score.Shots # Orange Shots
			
		# -------------------------------
		# Now do all car values
		# -------------------------------
		
		# Blue pos
		inputs[1] = gameTickPacket.CarInfo[blueIndex].Location.Y / UU_TO_GAMEVALUES
		inputs[5] = gameTickPacket.CarInfo[blueIndex].Location.X / UU_TO_GAMEVALUES
		inputs[4] = gameTickPacket.CarInfo[blueIndex].Location.Z / UU_TO_GAMEVALUES
		
		# Orange pos
		inputs[3] = gameTickPacket.CarInfo[orngIndex].Location.Y / UU_TO_GAMEVALUES
		inputs[18] = gameTickPacket.CarInfo[orngIndex].Location.X / UU_TO_GAMEVALUES
		inputs[17] = gameTickPacket.CarInfo[orngIndex].Location.Z / UU_TO_GAMEVALUES
		
		# Blue velocity
		inputs[28] = gameTickPacket.CarInfo[blueIndex].Velocity.X / UU_TO_GAMEVALUES
		inputs[29] = gameTickPacket.CarInfo[blueIndex].Velocity.Z / UU_TO_GAMEVALUES
		inputs[30] = gameTickPacket.CarInfo[blueIndex].Velocity.Y / UU_TO_GAMEVALUES
		
		# Orange velocity
		inputs[34] = gameTickPacket.CarInfo[orngIndex].Velocity.X / UU_TO_GAMEVALUES
		inputs[35] = gameTickPacket.CarInfo[orngIndex].Velocity.Z / UU_TO_GAMEVALUES
		inputs[36] = gameTickPacket.CarInfo[orngIndex].Velocity.Y / UU_TO_GAMEVALUES
		
		# Boost
		inputs[0] = gameTickPacket.CarInfo[blueIndex].Boost
		inputs[37] = gameTickPacket.CarInfo[orngIndex].Boost
		
		# Rotations
		bluePitch = float(gameTickPacket.CarInfo[blueIndex].Rotation.Pitch)
		blueYaw = float(gameTickPacket.CarInfo[blueIndex].Rotation.Yaw)
		blueRoll = float(gameTickPacket.CarInfo[blueIndex].Rotation.Roll)
		orngPitch = float(gameTickPacket.CarInfo[orngIndex].Rotation.Pitch)
		orngYaw = float(gameTickPacket.CarInfo[orngIndex].Rotation.Yaw)
		orngRoll = float(gameTickPacket.CarInfo[orngIndex].Rotation.Roll)
		
		# Blue rotations
		inputs[8] = math.cos(bluePitch * URotationToRadians) * math.cos(blueYaw * URotationToRadians) # Rot 1
		inputs[9] = math.sin(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.cos(blueYaw * URotationToRadians) - math.cos(blueRoll * URotationToRadians) * math.sin(blueYaw * URotationToRadians) # Rot2
		inputs[10] = -1 * math.cos(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.cos(blueYaw * URotationToRadians) + math.sin(blueRoll * URotationToRadians) * math.sin(blueYaw * URotationToRadians)  # Rot 3
		inputs[11] = math.cos(bluePitch * URotationToRadians) * math.sin(blueYaw * URotationToRadians) # Rot 4
		inputs[12] = math.sin(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.sin(blueYaw * URotationToRadians) + math.cos(blueRoll * URotationToRadians) * math.cos(blueYaw * URotationToRadians) # Rot5
		inputs[13] = -1 * math.sin(blueRoll * URotationToRadians) * math.cos(bluePitch * URotationToRadians) # Rot 6
		inputs[14] = math.cos(bluePitch * URotationToRadians)# Rot 7
		inputs[15] = math.cos(blueYaw * URotationToRadians) * math.sin(blueRoll * URotationToRadians) - math.cos(blueRoll * URotationToRadians) * math.sin(bluePitch * URotationToRadians) * math.sin(blueYaw * URotationToRadians) # Rot 8
		inputs[16] = math.cos(blueRoll * URotationToRadians) * math.cos(bluePitch * URotationToRadians) # Rot 9
		
		# Orange rot
		inputs[19] = math.cos(orngPitch * URotationToRadians) * math.cos(orngYaw * URotationToRadians) # Rot 1
		inputs[20] = math.sin(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.cos(orngYaw * URotationToRadians) - math.cos(orngRoll * URotationToRadians) * math.sin(orngYaw * URotationToRadians) # Rot2
		inputs[21] = -1 * math.cos(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.cos(orngYaw * URotationToRadians) + math.sin(orngRoll * URotationToRadians) * math.sin(orngYaw * URotationToRadians)  # Rot 3
		inputs[22] = math.cos(orngPitch * URotationToRadians) * math.sin(orngYaw * URotationToRadians) # Rot 4
		inputs[23] = math.sin(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.sin(orngYaw * URotationToRadians) + math.cos(orngRoll * URotationToRadians) * math.cos(orngYaw * URotationToRadians) # Rot5
		inputs[24] = -1 * math.sin(orngRoll * URotationToRadians) * math.cos(orngPitch * URotationToRadians) # Rot 6
		inputs[25] = math.cos(orngPitch * URotationToRadians)# Rot 7
		inputs[26] = math.cos(orngYaw * URotationToRadians) * math.sin(orngRoll * URotationToRadians) - math.cos(orngRoll * URotationToRadians) * math.sin(orngPitch * URotationToRadians) * math.sin(orngYaw * URotationToRadians) # Rot 8
		inputs[27] = math.cos(orngRoll * URotationToRadians) * math.cos(orngPitch * URotationToRadians) # Rot 9
		
		return(inputs,scoring)

def updateInputs(inputs):

	# Open shared memory
	shm = mmap.mmap(0, 1868, "Local\\RLBot")
	
	while(True):
		shm.seek(0) # Move to beginning of shared memory
		ctypes.memmove(ctypes.addressof(inputs.GameTickPacket), shm.read(1868), ctypes.sizeof(inputs.GameTickPacket)) # copy shared memory into struct
		
		time.sleep(0.01)
		
def resetInputs():
	exec(open("resetDevices.py").read())

def runAgent(inputs, team, q):
	# Deep copy inputs?
	config = configparser.RawConfigParser()
	config.read('rlbot.cfg')
	if team == "blue":
		agent1 = importlib.import_module(config.get('Player Configuration', 'p1Agent'))
		agent = agent1.agent("blue")
	else:
		agent2 = importlib.import_module(config.get('Player Configuration', 'p2Agent'))
		agent = agent2.agent("orange")
	while(True):
		output = agent.get_output_vector((inputs))
		try:
			q.put(output)
		except Queue.Full:
			pass
		time.sleep(0.01)
			
if __name__ == '__main__':
	# Make sure input devices are reset to neutral whenever the script terminates
	atexit.register(resetInputs)

	time.sleep(3) # Sleep 3 second before starting to give me time to set things up

	# Read config for agents
	config = configparser.RawConfigParser()
	config.read('rlbot.cfg')
	agent1 = importlib.import_module(config.get('Player Configuration', 'p1Agent'))
	agent2 = importlib.import_module(config.get('Player Configuration', 'p2Agent'))
	agent1Color = config.get('Player Configuration', 'p1Color')
	agent2Color = config.get('Player Configuration', 'p2Color')
	
	gameTickPacket = cStructure.GameTickPacket()
	shm = mmap.mmap(0, 1868, "Local\\RLBot")
	shm.seek(0) # Move to beginning of shared memory
	ctypes.memmove(ctypes.addressof(gameTickPacket), shm.read(1868), ctypes.sizeof(gameTickPacket)) # copy shared memory into struct
	inputs = Value(cStructure.SharedInputs, gameTickPacket)

	q1 = Queue(1)
	q2 = Queue(1)
	
	output1 = [16383, 16383, 32767, 0, 0, 0, 0]
	output2 = [16383, 16383, 32767, 0, 0, 0, 0]
	
	rtd = realTimeDisplay.real_time_display()
	rtd.build_initial_window(agent1.BOT_NAME, agent2.BOT_NAME)
	
	ph = PlayHelper.play_helper()
	
	p1 = Process(target=updateInputs, args=(inputs,))
	p1.start()
	p2 = Process(target=runAgent, args=(inputs, agent1Color, q1))
	p2.start()
	p3 = Process(target=runAgent, args=(inputs, agent2Color, q2))
	p3.start()
	
	while (True):
		updateFlag = False
		
		rtd.UpdateDisplay(convert_new_input_to_old_input(inputs))
		
		try:
			output1 = q1.get()
			updateFlag = True
		except Queue.Empty:
			pass
			
		try:
			output2 = q2.get()
			updateFlag = True
		except Queue.Empty:
			pass
		
		if (updateFlag):
			ph.update_controllers(output1, output2)
		
		rtd.UpdateKeyPresses(output1, output2)
		time.sleep(0.01)