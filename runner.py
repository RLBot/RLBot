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

def updateInputs(blueInputs, orngInputs, displayInputs, blueIsLocked, orngIsLocked):

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
			if (not blueIsLocked.value):
				blueIsLocked.value = 1 # Lock
				ctypes.memmove(ctypes.addressof(blueInputs.GameTickPacket), shm.read(2000), ctypes.sizeof(blueInputs.GameTickPacket)) # copy shared memory into struct
				blueIsLocked.value = 0 # Unlock
		
		# Now copy orngInputs
		shm.seek(0)
		ctypes.memmove(ctypes.addressof(lock), shm.read(4), ctypes.sizeof(lock)) # dll uses InterlockedExchange so this read will return the correct value!
		
		if (lock.value != REFRESH_IN_PROGRESS):
			if (not orngIsLocked.value):
				orngIsLocked.value = 1 # Lock
				ctypes.memmove(ctypes.addressof(orngInputs.GameTickPacket), shm.read(2000), ctypes.sizeof(orngInputs.GameTickPacket)) # copy shared memory into struct
				orngIsLocked.value = 0 # Unlock
				
		# Now refresh display
		shm.seek(0) # Move to beginning of shared memory
		ctypes.memmove(ctypes.addressof(lock), shm.read(4), ctypes.sizeof(lock)) # dll uses InterlockedExchange so this read will return the correct value!
		
		if (lock.value != REFRESH_IN_PROGRESS):
			ctypes.memmove(ctypes.addressof(displayInputs.GameTickPacket), shm.read(2000), ctypes.sizeof(displayInputs.GameTickPacket)) # copy shared memory into struct
		
		time.sleep(0.005) # Sleep time half of agent sleep time
		
def resetInputs():
	exec(open("resetDevices.py").read())

def runAgent(inputs, team, q, isLocked):
	config = configparser.RawConfigParser()
	config.read('rlbot.cfg')
	if team == "blue":
		agent1 = importlib.import_module(config.get('Player Configuration', 'p1Agent'))
		agent = agent1.agent("blue")
	else:
		agent2 = importlib.import_module(config.get('Player Configuration', 'p2Agent'))
		agent = agent2.agent("orange")
	while(True):
		if(not isLocked.value):
			isLocked.value = 1
			output = agent.get_output_vector(inputs)
			isLocked.value = 0
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
	
	blueGameTickPacket = cStructure.GameTickPacket()
	orngGameTickPacket = cStructure.GameTickPacket()
	displayGameTickPacket = cStructure.GameTickPacket()

	blueInputs = Value(cStructure.SharedInputs, blueGameTickPacket)
	orngInputs = Value(cStructure.SharedInputs, orngGameTickPacket)
	displayInputs = Value(cStructure.SharedInputs, displayGameTickPacket)
	
	blueIsLocked = Value('i', 0)
	orngIsLocked = Value('i', 0)

	q1 = Queue(1)
	q2 = Queue(1)
	
	output1 = [16383, 16383, 32767, 0, 0, 0, 0]
	output2 = [16383, 16383, 32767, 0, 0, 0, 0]
	
	rtd = importlib.import_module("displays." + config.get('RLBot Configuration', 'display')).real_time_display()
	rtd.build_initial_window(agent1.BOT_NAME, agent2.BOT_NAME)
	
	ph = PlayHelper.play_helper()
	
	p1 = Process(target=updateInputs, args=(blueInputs, orngInputs, displayInputs, blueIsLocked, orngIsLocked))
	p1.start()
	p2 = Process(target=runAgent, args=(blueInputs, agent1Color, q1, blueIsLocked))
	p2.start()
	p3 = Process(target=runAgent, args=(blueInputs, agent2Color, q2, orngIsLocked))
	p3.start()
	
	while (True):
		updateFlag = False
		
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
		
		if (updateFlag):
			ph.update_controllers(output1, output2)
		
		rtd.UpdateKeyPresses(output1, output2)
		time.sleep(0.01)