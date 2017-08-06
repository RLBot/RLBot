from ctypes import *
from ctypes.wintypes import *

import realTimeDisplay
import time
import ReadWriteMem
import PlayHelper
import array
import AlwaysTowardsBallAgent

OpenProcess = windll.kernel32.OpenProcess
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF

rwm = ReadWriteMem.ReadWriteMem()
pid = rwm.GetProcessIdByName("RocketLeague.exe")
rocketLeagueBaseAddress = rwm.GetBaseAddress(pid)

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

agent1 = AlwaysTowardsBallAgent.agent("blue")
agent2 = AlwaysTowardsBallAgent.agent("orange")

rtd = realTimeDisplay.real_time_display()
rtd.build_initial_window(agent1.get_bot_name(), agent2.get_bot_name())

ph = PlayHelper.play_helper()
addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)

blueScore = None
orangeScore = None
blueDemo = None
orangeDemo = None

time.sleep(3) # Sleep 3 second before starting to give me time to set things up
for i in range(8000):
    values = ph.GetValueVector(processHandle, addresses)
	
    rtd.UpdateDisplay(values) # Update display first because we might sleep if score or demo
    
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
        time.sleep(15) # Sleep 15 seconds for goal and replay then ping for correct values
        addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)
        while (ph.ping_refreshed_pointers(processHandle, addresses)):
            time.sleep(0.5)
            addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)

    if (not orangeScore == values[1][1]):
        print("Orange has scored! Waiting for ball and players to reset")
        orangeScore = values[1][1]
        time.sleep(15) # Sleep 15 seconds for goal and replay then ping for correct values
        addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)
        while (ph.ping_refreshed_pointers(processHandle, addresses)):
            time.sleep(0.5)
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
    
    output1 = agent1.get_output_vector(values)
    output2 = agent2.get_output_vector(values)
    ph.update_controllers(output1, output2)
    rtd.UpdateKeyPresses(output1, output2)
                            
    time.sleep(0.05) # Sleep for a set interval

ph.release_keys() # Release all the buttons so your computer isn't messed up

CloseHandle(processHandle)