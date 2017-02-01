"""
This file will attempt to train and test the model as the game is being played
"""
from ctypes import *
from ctypes.wintypes import *
import ReadWriteMem
import time
import PlayHelper
import array
import model
import tensorflow as tf
import sys, getopt

# Get arguments for input model or output
argv = sys.argv[1:]
inputmodel = None
try:
    opts, args = getopt.getopt(argv,"hi:",["ifile="])
except getopt.GetoptError:
    print('play.py -i <inputmodel>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('play.py -i <inputmodel>')
        sys.exit()
    elif opt in ("-i", "--ifile"):
        inputmodel = ".\\" + arg + ".ckpt"

OpenProcess = windll.kernel32.OpenProcess
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF
LEARNING_RATE = 1e-1 # Need to fiddle with this to find what works well

rwm = ReadWriteMem.ReadWriteMem()
pid = rwm.GetProcessIdByName("RocketLeague.exe")
rocketLeagueBaseAddress = rwm.GetBaseAddress(pid)

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

# Start session
sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

# Load Model
if inputmodel is not None:
    saver = tf.train.Saver()
    saver.restore(sess, inputmodel) # Restore if model exists

ph = PlayHelper.play_helper()
addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)

blueScore = None
orangeScore = None
blueDemo = None
orangeDemo = None

time.sleep(1) # Sleep 1 second before starting to give me time to set things up
for i in range(6000):
    values = ph.GetValueVector(processHandle, addresses)
    
    output = model.y.eval(feed_dict={model.x: [values[0]], model.keep_prob: 1.0})[0] # Get output vector from model
    
    # Process scoring to see if any new goals or demos
    if (blueScore == None):
        # Need to update values if don't already exist
        blueScore = values[1][0]
        orangeScore = values[1][1]
        blueDemo = values[1][2]
        orangeDemo = values[1][3]

    if (not blueScore == values[1][0]):
        print("Blue has scored! Waiting for ball and players to reset")
        blueScore = values[1][0]
        time.sleep(17.5) # Takes about 14 seconds for goal and replay
        addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)

    if (not orangeScore == values[1][1]):
        print("Orange has scored! Waiting for ball and players to reset")
        orangeScore = values[1][1]
        time.sleep(17.5) # Takes about 14 seconds for goal and replay
        addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)

    if (not blueDemo == values[1][2]):
        print("Orange has scored a demo on blue! Waiting for blue player to reset")
        blueDemo = values[1][2]
        time.sleep(4) # Takes about 3 seconds to respawn for a demo
        addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)

    if (not orangeDemo == values[1][3]):
        print("Blue has scored a demo on orange! Waiting for orange player to reset")
        orangeDemo = values[1][3]
        time.sleep(4) # Takes about 3 seconds to respawn from demo. Even though blue can keep playing, for training I am just sleeping
        addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)
    
    # Use output vector to control button inputs
    #print(values)
    print(output)
    ph.update_keys(output)
                            
    time.sleep(0.05) # Sleep for a set interval

ph.release_keys() # Release all the buttons so your computer isn't messed up

CloseHandle(processHandle)