from ctypes import *
from ctypes.wintypes import *
import ReadWriteMem
import time
import PlayHelper
import array
import xbox

OpenProcess = windll.kernel32.OpenProcess
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF
LEARNING_RATE = 1e-4 # Need to fiddle with this to find what works well

rwm = ReadWriteMem.ReadWriteMem()
pid = rwm.GetProcessIdByName("RocketLeague.exe")
rocketLeagueBaseAddress = rwm.GetBaseAddress(pid)

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

ph = PlayHelper.play_helper()
addresses = ph.GetAddressVector(processHandle,rocketLeagueBaseAddress)

blueScore = None
orangeScore = None
blueDemo = None
orangeDemo = None

# make / open outfiles
x_file = open('x.csv', 'a')
y_file = open('y.csv', 'a')        

time.sleep(1) # Wait 1 second before starting

# 6000 readings / 20 = 300 seconds = 5 minutes of recording
for i in range(5000):
    # Get data values from game
    values = ph.GetValueVector(processHandle, addresses)
    
    # Get xbox output vector used
    output = xbox.get_xbox_output()
    
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
    
    # Append to csv file
    x_file.write(','.join(map(str,values[0])) + '\n' ) # Write a line to csv file
    y_file.write(','.join(map(str,output)) + '\n' ) # Write a line to csv file
    # print(values)
    # print(output)
                            
    time.sleep(0.05) # Sleep for a set interval (Play around with this time a lot)

CloseHandle(processHandle)
x_file.close()
y_file.close()