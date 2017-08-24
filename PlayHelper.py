import ReadWriteMem
import array
import time
import pyvjoy

class play_helper:
    
    rwm = ReadWriteMem.ReadWriteMem()
    
    def GetAddressVector(self, processHandle, rocketLeagueBaseAddress):
        addressList = array.array('i',(0,)*41) # Create a tuple with 41 values
        
        addressList[0] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x019FCF34, 0xCC, 0x30, 0x54]) # Blue Boost address (Updated August 5, 2017)
        addressList[1] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x018DB9C4, 0x4, 0x20, 0x44]) # Player z address
        addressList[2] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x018DB9C4, 0x8, 0x20, 0x44]) # Ball z address
        addressList[3] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x018DB9C4, 0x0, 0x20, 0x44]) # Bot (orange) z address

        self.verifyPlayerPointers(processHandle, addressList) # Still need to deal with demolitions being wacky pointers but that can be done later if possible

        addressList[4] = addressList[1] + 4 # Player y address
        addressList[5] = addressList[1] - 4 # Player x address
        addressList[6] = addressList[2] + 4 # Ball y address
        addressList[7] = addressList[2] - 4 # Ball x address
        addressList[8] = addressList[4] + 8 # Player rot1
        addressList[9] = addressList[8] + 4 # Player rot2
        addressList[10] = addressList[9] + 4 # Player rot3
        addressList[11] = addressList[10] + 8 # Player rot4
        addressList[12] = addressList[11] + 4 # Player rot5
        addressList[13] = addressList[12] + 4 # Player rot6
        addressList[14] = addressList[13] + 8 # Player rot7
        addressList[15] = addressList[14] + 4 # Player rot8
        addressList[16] = addressList[15] + 4 # Player rot9
        addressList[17] = addressList[3] + 4 # Bot y address (orange)
        addressList[18] = addressList[3] - 4 # Bot x address
        addressList[19] = addressList[17] + 8 # Bot rot1
        addressList[20] = addressList[19] + 4 # Bot rot2
        addressList[21] = addressList[20] + 4 # Bot rot3
        addressList[22] = addressList[21] + 8 # Bot rot4
        addressList[23] = addressList[22] + 4 # Bot rot5
        addressList[24] = addressList[23] + 4 # Bot rot6
        addressList[25] = addressList[24] + 8 # Bot rot7
        addressList[26] = addressList[25] + 4 # Bot rot8
        addressList[27] = addressList[26] + 4 # Bot rot9
        addressList[28] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x019A3BA0, 0x8, 0x228, 0x20C]) # Blue score address
        addressList[29] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x019A3BA0, 0x10, 0x228, 0x20C]) # Orange score address
        addressList[30] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x019A3BA0, 0x8, 0x310]) # Blue "Score" address
        addressList[31] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x019A3BA0, 0x10, 0x310]) # Orange "Score" address
        addressList[32] = addressList[30] + 4 # Blue goals
        addressList[33] = addressList[32] + 12 # Blue saves
        addressList[34] = addressList[32] + 16 # Blue shots
        addressList[35] = addressList[31] + 4 # Orange goals
        addressList[36] = addressList[35] + 12 # Orange saves
        addressList[37] = addressList[35] + 16 # Orange shots
        addressList[38] = addressList[37] + 4 # Demos by orange
        addressList[39] = addressList[34] + 4 # Demos by blue
        addressList[40] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x0192F0A4, 0x688, 0x8, 0x30C]) # Orange Boost address

        return addressList

    def getKey(self, item):
        return item[1]

    def verifyPlayerPointers(self, processHandle, addressVect):
        # So after a goal, we have pointers to blue, white, orange, but not necessarily that correct order. Check values and reorganize.
        tupleList = [(addressVect[1],self.rwm.ReadFloatFromAddress(processHandle, addressVect[1])), (addressVect[2],self.rwm.ReadFloatFromAddress(processHandle, addressVect[2])), (addressVect[3],self.rwm.ReadFloatFromAddress(processHandle, addressVect[3]))]
        sortedList = sorted(tupleList, key=self.getKey)
        # Now assign
        addressVect[1] = sortedList[0][0]
        addressVect[2] = sortedList[1][0]
        addressVect[3] = sortedList[2][0]

    def ping_refreshed_pointers(self, processHandle, addressVect):
        # Make sure pointers after goal are pointing to z values that make sense
        tupleList = [(addressVect[1],self.rwm.ReadFloatFromAddress(processHandle, addressVect[1])), (addressVect[2],self.rwm.ReadFloatFromAddress(processHandle, addressVect[2])), (addressVect[3],self.rwm.ReadFloatFromAddress(processHandle, addressVect[3]))]
        sortedList = sorted(tupleList, key=self.getKey)
        value1 = sortedList[0][1]
        value2 = sortedList[1][1]
        value3 = sortedList[2][1]
        if (value1 < -100 or value1 > -30):
            print("Ping failed blue z value check")
            return True
        if (value2 < -5 or value2 > 5):
            print("Ping failed ball z value check")
            return True
        if (value3 < 30 or value3 > 100):
            print("Ping failed orng z value check")
            return True

        # Check boost values are reset
        if (not float(self.rwm.ReadIntFromAddress(processHandle, addressVect[0])) == 33):
            print("Ping failed blue boost check")
            return True
        if (not float(self.rwm.ReadIntFromAddress(processHandle, addressVect[40])) == 33):
            print("Ping failed orange boost check")
            return True

        return False

    def GetValueVector(self, processHandle, addressVect):
        neuralInputs = array.array('f',(0,)*38) # Create a tuple with 38 float values
        scoring = array.array('f',(0,)*12) # Create a tuple with 12 float values
        # Need to read 28 values for neural inputs and calculate 9 velocities
         
        # Boost is an int so different case
        neuralInputs[0] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[0]))
        neuralInputs[37] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[40]))
        for i in range(1,28):
            neuralInputs[i] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[i])

        neuralInputs[28] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[1] + 268) # x
        neuralInputs[29] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[1] + 276) # "y"
        neuralInputs[30] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[1] + 272) # "z"
        neuralInputs[31] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[2] + 268) # x
        neuralInputs[32] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[2] + 276) # "y"
        neuralInputs[33] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[2] + 272) # "z"
        neuralInputs[34] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[3] + 268) # x
        neuralInputs[35] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[3] + 276) # "y"
        neuralInputs[36] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[3] + 272) # "z"
        
        # Also create tuple of scoring changes/demos so I can know when reset is necessary
        scoring[0] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[28])) # Blue Score
        scoring[1] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[29])) # Orange Score
        scoring[2] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[38])) # Demos on blue
        scoring[3] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[39])) # Demos on orange
		
		# Now fill in the other scoring values
        for i in range(30,38):
            scoring[i - 26] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[i]))

        return neuralInputs, scoring

    def reset_contollers(self):
        p1 = pyvjoy.VJoyDevice(1)
        p2 = pyvjoy.VJoyDevice(2)

        p1.data.wAxisX = 16383
        p1.data.wAxisY = 16383
        p1.data.wAxisYRot = 16383
        p1.data.wAxisXRot = 16383
        p1.data.wAxisZ = 0
        p1.data.wAxisZRot = 0
        p1.data.lButtons = 0

        p2.data.wAxisX = 16383
        p2.data.wAxisY = 16383
        p2.data.wAxisYRot = 16383
        p2.data.wAxisXRot = 16383
        p2.data.wAxisZ = 0
        p2.data.wAxisZRot = 0
        p2.data.lButtons = 0

        #send data to vJoy device
        p1.update()
        p2.update()
        
    def update_controllers(self, output1, output2):
        # Update controller buttons for both players

        # TODO: Sanitize input players give
        p1 = pyvjoy.VJoyDevice(1)
        p2 = pyvjoy.VJoyDevice(2)

        p1.data.wAxisX = output1[0]
        p2.data.wAxisX = output2[0]

        p1.data.wAxisY = output1[1]
        p2.data.wAxisY = output2[1]

        p1.data.wAxisZRot = output1[2]
        p2.data.wAxisZRot = output2[2]

        p1.data.wAxisZ = output1[3]
        p2.data.wAxisZ = output2[3]

        p1.data.lButtons = (1 * output1[4]) + (2 * output1[5]) + (4 * output1[6])
        p2.data.lButtons = (1 * output2[4]) + (2 * output2[5]) + (4 * output2[6])

        p1.data.wAxisXRot = 16383
        p2.data.wAxisXRot = 16383

        p1.data.wAxisYRot = 16383
        p2.data.wAxisYRot = 16383

        #send data to vJoy device
        p1.update()
        p2.update()
