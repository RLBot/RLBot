from multiprocessing import Process, Queue, Value

import time
import atexit
import PlayHelper
import configparser
import importlib
import cStructure
import ctypes
import mmap
import math

def updateInputs(player1_inputs, player2_inputs, display_inputs, p1_is_locked, p2_is_locked):

	# I think performance here is good enough that it would not be improved by running 2 update processes concurrently. So updates for both inputs are done serial in this process.

	REFRESH_IN_PROGRESS = 1

	# Open shared memory
	shm = mmap.mmap(0, 2004, "Local\\RLBot")
	# This lock ensures that a read cannot start while the dll is writing to shared memory.
	lock = ctypes.c_long(0)
	
	while(True):
	
		# First copy blueInputs
		shm.seek(0) # Move to beginning of shared memory
		ctypes.memmove(ctypes.addressof(lock), shm.read(4), ctypes.sizeof(lock)) # dll uses InterlockedExchange so this read will return the correct value!
		
		if (lock.value != REFRESH_IN_PROGRESS):
			if (not p1_is_locked.value):
				p1_is_locked.value = 1 # Lock
				ctypes.memmove(ctypes.addressof(player1_inputs.GameTickPacket), shm.read(2000), ctypes.sizeof(player1_inputs.GameTickPacket)) # copy shared memory into struct
				p1_is_locked.value = 0 # Unlock
		
		# Now copy orngInputs
		shm.seek(0)
		ctypes.memmove(ctypes.addressof(lock), shm.read(4), ctypes.sizeof(lock)) # dll uses InterlockedExchange so this read will return the correct value!
		
		if (lock.value != REFRESH_IN_PROGRESS):
			if (not p2_is_locked.value):
				p2_is_locked.value = 1 # Lock
				ctypes.memmove(ctypes.addressof(player2_inputs.GameTickPacket), shm.read(2000), ctypes.sizeof(player2_inputs.GameTickPacket)) # copy shared memory into struct
				p2_is_locked.value = 0 # Unlock
				
		# Now refresh display
		shm.seek(0) # Move to beginning of shared memory
		ctypes.memmove(ctypes.addressof(lock), shm.read(4), ctypes.sizeof(lock)) # dll uses InterlockedExchange so this read will return the correct value!
		
		if (lock.value != REFRESH_IN_PROGRESS):
			ctypes.memmove(ctypes.addressof(display_inputs.GameTickPacket), shm.read(2000), ctypes.sizeof(display_inputs.GameTickPacket)) # copy shared memory into struct
		
		time.sleep(0.005) # Sleep time half of agent sleep time
		
def resetInputs():
	exec(open("resetDevices.py").read())

def runAgent(inputs, team, q, is_locked, player_index):
	config = configparser.RawConfigParser()
	config.read('rlbot.cfg')
	config_key = 'p1Agent' if player_index == 0 else 'p2Agent'
	agent_module = importlib.import_module(config.get('Player Configuration', config_key))
	agent = agent_module.agent(team)

	ph = PlayHelper.PlayHelper(player_index)

	while(True):
		if(not is_locked.value):
			is_locked.value = 1
			output = agent.get_output_vector(inputs)
			ph.update_controller(output)
			is_locked.value = 0
			if (not q.full()):
				q.put(output)  # Put it in the queue so the GUI thread can fetch it

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
	
	player1GameTickPacket = cStructure.GameTickPacket()
	player2GameTickPacket = cStructure.GameTickPacket()
	displayGameTickPacket = cStructure.GameTickPacket()

	player1Inputs = Value(cStructure.SharedInputs, player1GameTickPacket)
	player2Inputs = Value(cStructure.SharedInputs, player2GameTickPacket)
	displayInputs = Value(cStructure.SharedInputs, displayGameTickPacket)
	
	player1IsLocked = Value('i', 0)
	player2IsLocked = Value('i', 0)

	q1 = Queue(1)
	q2 = Queue(1)
	
	output1 = [16383, 16383, 32767, 0, 0, 0, 0]
	output2 = [16383, 16383, 32767, 0, 0, 0, 0]
	
	rtd = importlib.import_module("displays." + config.get('RLBot Configuration', 'display')).real_time_display()
	rtd.build_initial_window(agent1.BOT_NAME, agent2.BOT_NAME)

	
	p1 = Process(target=updateInputs, args=(player1Inputs, player2Inputs, displayInputs, player1IsLocked, player2IsLocked))
	p1.start()
	p2 = Process(target=runAgent, args=(player1Inputs, agent1Color, q1, player1IsLocked, 0))
	p2.start()
	p3 = Process(target=runAgent, args=(player2Inputs, agent2Color, q2, player2IsLocked, 1))
	p3.start()
	
	while (True):
		rtd.UpdateDisplay(displayInputs)
		
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
		
		rtd.UpdateKeyPresses(output1, output2)
		time.sleep(0.01)