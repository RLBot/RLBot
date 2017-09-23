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
import numpy as np

def updateInputs(inputs):

	# Open shared memory
	shm = mmap.mmap(0, 2000, "Local\\RLBot")
	
	while(True):
		shm.seek(0) # Move to beginning of shared memory
		ctypes.memmove(ctypes.addressof(inputs.GameTickPacket), shm.read(2000), ctypes.sizeof(inputs.GameTickPacket)) # copy shared memory into struct
		
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
	
	rtd = importlib.import_module("displays." + config.get('RLBot Configuration', 'display')).real_time_display()
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
		
		rtd.UpdateDisplay(inputs)
		
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