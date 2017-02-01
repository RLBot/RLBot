import ReadWriteMem
import array
import time
import SendKeys

class play_helper:
    
    W_CODE = 0x11
    A_CODE = 0x1E
    S_CODE = 0x1F
    D_CODE = 0x20
    LSHIFT_CODE = 0x2A
    J_CODE = 0x24
    K_CODE = 0x25
    
    rwm = ReadWriteMem.ReadWriteMem()
    
    timeStamp = None
    x = None
    y = None
    z = None
    ballx = None
    bally = None
    ballz = None
    botx = None
    boty = None
    botz = None
    
    # Key presses
    W = False
    A = False
    S = False
    D = False
    LSHIFT = False
    J = False
    K = False
    
    
    def GetAddressVector(self, processHandle, rocketLeagueBaseAddress):
        addressList = array.array('i',(0,)*42) # Create a tuple with 42 values
        
        addressList[0]= self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x017379B8, 0x34, 0x294, 0x1CC, 0x1AC, 0x144]) # Boost address (Need to update these for v1.27)
        addressList[1] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x016D50A8, 0x4, 0x54, 0x18, 0xF0, 0x44]) # Player z address
        addressList[2] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x0160D4F4, 0x8, 0x20, 0x44]) # Ball z address
        addressList[3] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x01731340, 0x114, 0x14, 0x1BC, 0xF0, 0x44]) # Bot (orange) z address
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
        addressList[17] = addressList[3] + 4 # Bot y address
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
        addressList[28] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x016D5090, 0x8, 0x318, 0x130, 0x0, 0x1F0]) # Blue score address
        addressList[29] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x01732F00, 0x178, 0x84, 0x28, 0x84, 0x1F0]) # Orange score address
        addressList[30] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x016D5084, 0xF8, 0x8, 0x28, 0x5B4, 0x2F4]) # Blue "Score" address
        addressList[31] = self.rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x016D5090, 0x10, 0xA8, 0x1E4, 0x35C, 0x2F4]) # Orange "Score" address
        addressList[32] = addressList[30] + 4 # Blue goals
        addressList[33] = addressList[32] + 8 # Blue assists
        addressList[34] = addressList[32] + 12 # Blue saves
        addressList[35] = addressList[32] + 16 # Blue shots
        addressList[36] = addressList[31] + 4 # Orange goals
        addressList[37] = addressList[36] + 8 # Orange assists
        addressList[38] = addressList[36] + 12 # Orange saves
        addressList[39] = addressList[36] + 16 # Orange shots
        addressList[40] = addressList[39] + 4 # Demos by orange
        addressList[41] = addressList[35] + 4 # Demos by blue

        return addressList
        
    def GetValueVector(self, processHandle, addressVect):
        neuralInputs = array.array('f',(0,)*43) # Create a tuple with 43 float values
        scoring = array.array('f',(0,)*4) # Create a tuple with 4 float values
        # scoring = modify this with what I want to return for scoring function
        # Need to read 28 values for neural inputs and calculate 9 velocities and 6 relative positions
         
        # Boost is an int so different case
        neuralInputs[0] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[0]))
        for i in range(1,28):
            neuralInputs[i] = self.rwm.ReadFloatFromAddress(processHandle, addressVect[i])
        
        if (self.timeStamp == None):
            # Need to set values for first time reading
            self.timeStamp = time.time()
            self.x = neuralInputs[5]
            self.y = neuralInputs[4]
            self.z = neuralInputs[1]
            self.ballx = neuralInputs[7]
            self.bally = neuralInputs[6]
            self.ballz = neuralInputs[2]
            self.botx = neuralInputs[18]
            self.boty = neuralInputs[17]
            self.botz = neuralInputs[3]

        # Calculate velocities
        curTime = time.time() # Shouldn't really matter where I put this so long as it is equally spaced apart
        timeDiff = curTime - self.timeStamp
        if (timeDiff == 0):
            timeDiff = 1
        neuralInputs[28] = (neuralInputs[5] - self.x) / timeDiff
        neuralInputs[29] = (neuralInputs[4] - self.y) / timeDiff
        neuralInputs[30] = (neuralInputs[1] - self.z) / timeDiff
        neuralInputs[31] = (neuralInputs[7] - self.ballx) / timeDiff
        neuralInputs[32] = (neuralInputs[6] - self.bally) / timeDiff
        neuralInputs[33] = (neuralInputs[2] - self.ballz) / timeDiff
        neuralInputs[34] = (neuralInputs[18] - self.botx) / timeDiff
        neuralInputs[35] = (neuralInputs[17] - self.boty) / timeDiff
        neuralInputs[36] = (neuralInputs[3] - self.botz) / timeDiff

        # Calculate relative positions
        neuralInputs[37] = neuralInputs[7] - neuralInputs[5] # Relative x position to ball
        neuralInputs[38] = neuralInputs[6] - neuralInputs[4] # Relative y position to ball
        neuralInputs[39] = neuralInputs[2] - neuralInputs[1] # Relative z position to ball
        neuralInputs[40] = neuralInputs[18] - neuralInputs[5] # Relative x position to bot
        neuralInputs[41] = neuralInputs[17] - neuralInputs[4] # Relative y position to bot
        neuralInputs[42] = neuralInputs[3] - neuralInputs[1] # Relative z position to bot
        
        # Also create tuple of scoring changes/demos so I can know when reset is necessary
        scoring[0] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[28])) # Blue Score
        scoring[1] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[29])) # Orange Score
        scoring[2] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[40])) # Demos on blue
        scoring[3] = float(self.rwm.ReadIntFromAddress(processHandle, addressVect[41])) # Demos on orange

        # Now update to old values
        self.timeStamp = curTime
        self.x = neuralInputs[5]
        self.y = neuralInputs[4]
        self.z = neuralInputs[1]
        self.ballx = neuralInputs[7]
        self.bally = neuralInputs[6]
        self.ballz = neuralInputs[2]
        self.botx = neuralInputs[18]
        self.boty = neuralInputs[17]
        self.botz = neuralInputs[3]

        return neuralInputs, scoring
        
    def update_keys(self, output):
        # Need to press keys that need to be pressed and aren't already pressed
        # Need to unpress keys that are pressed and need to be unpressed
        
        # If output[0] < -1 decelerate, > 1 accelerate, otherwise don't move
        if output[0] < -1.0:
            if (not self.S):
                SendKeys.PressKey(self.S_CODE)
                self.S = True
            if (self.W):
                SendKeys.ReleaseKey(self.W_CODE)
                self.W = False
        elif output[0] > 1.0:
            if (not self.W):
                SendKeys.PressKey(self.W_CODE)
                self.W = True
            if (self.S):
                SendKeys.ReleaseKey(self.S_CODE)
                self.S = False
        else:
            if (self.W):
                SendKeys.ReleaseKey(self.W_CODE)
                self.W = False
            if (self.S):
                SendKeys.ReleaseKey(self.S_CODE)
                self.S = False
                
        # output[1], check for left, none, right
        if output[1] < -1.0:
            if (not self.A):
                SendKeys.PressKey(self.A_CODE)
                self.A = True
            if (self.D):
                SendKeys.ReleaseKey(self.D_CODE)
                self.D = False
        elif output[1] > 1.0:
            if (not self.D):
                SendKeys.PressKey(self.D_CODE)
                self.D = True
            if (self.A):
                SendKeys.ReleaseKey(self.A_CODE)
                self.A = False
        else:
            if (self.D):
                SendKeys.ReleaseKey(self.D_CODE)
                self.D = False
            if (self.A):
                SendKeys.ReleaseKey(self.A_CODE)
                self.A = False
                
        # output[2], dift key off/on
        if output[2] < 0.0:
            if (self.LSHIFT):
                SendKeys.ReleaseKey(self.LSHIFT_CODE)
                self.LSHIFT = False
        else:
            if (not self.LSHIFT):
                SendKeys.PressKey(self.LSHIFT_CODE)
                self.LSHIFT = True
                
        # output[3], boost key off/on
        if output[3] < 0.0:
            if (self.J):
                SendKeys.ReleaseKey(self.J_CODE)
                self.J = False
        else:
            if (not self.J):
                SendKeys.PressKey(self.J_CODE)
                self.J = True
                
        # output[4], jump key off/on
        if output[4] < 0.0:
            if (self.K):
                SendKeys.ReleaseKey(self.K_CODE)
                self.K = False
        else:
            if (not self.K):
                SendKeys.PressKey(self.K_CODE)
                self.K = True
                
    def release_keys(self):
        # Make sure to unpress all keys when done
        if (self.W):
            SendKeys.ReleaseKey(self.W_CODE)
        if (self.A):
            SendKeys.ReleaseKey(self.A_CODE)
        if (self.S):
            SendKeys.ReleaseKey(self.S_CODE)
        if (self.D):
            SendKeys.ReleaseKey(self.D_CODE)
        if (self.LSHIFT):
            SendKeys.ReleaseKey(self.LSHIFT_CODE)
        if (self.J):
            SendKeys.ReleaseKey(self.J_CODE)
        if (self.K):
            SendKeys.ReleaseKey(self.K_CODE)
        
'''

Some original code here in case I made mistakes

# Find beginning pointers to structures
boostAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x01738774, 0xB4, 0x294, 0x1CC, 0x1AC, 0x14C])
zAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x01732220, 0x114, 0xC, 0x1BC, 0xF0, 0x44]) # improved z position (must refolow path after every car reset (goal/overtime)
ballzAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x016E88B4, 0x90, 0xC, 0x10, 0xF0, 0x44])
blueScoreAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x0166A648, 0x5B4, 0x28, 0x3C, 0x5DC, 0x1F0])
orngScoreAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x01733DE0, 0x104, 0x2A0, 0x20C, 0x1F0])
blueRLScoreAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x01733DE0, 0x110, 0x10, 0x268, 0x0, 0x2F4])
orngRLScoreAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x0166793C, 0x654, 0x28, 0x3C, 0x668, 0x2F4])
orngZAddress = rwm.GetFinalAddress(processHandle, rocketLeagueBaseAddress, [0x01732220, 0x114, 0x14, 0x1BC, 0xF0, 0x44]) # improved z position (must refolow path after every car reset (goal/overtime)

# Get other memory locations
yAddress = zAddress + 4
xAddress = zAddress - 4
ballyAddress = ballzAddress + 4
ballxAddress = ballzAddress - 4
rot1 = yAddress + 8
rot2 = rot1 + 4
rot3 = rot2 + 4
rot4 = rot3 + 8
rot5 = rot4 + 4
rot6 = rot5 + 4
rot7 = rot6 + 8
rot8 = rot7 + 4
rot9 = rot8 + 4
blueGoals = blueRLScoreAddress + 4 # If only do 1v1s this is same as blueScoreAddress
blueAssists = blueGoals + 8 # If I only do 1v1s I will never use this
blueSaves = blueGoals + 12
blueShots = blueGoals + 16
orngGoals = orngRLScoreAddress + 4 # If only do 1v1s this is same as blueScoreAddress
orngAssists = orngGoals + 8 # If I only do 1v1s I will never use this
orngSaves = orngGoals + 12
orngShots = orngGoals + 16
orngYAddress = orngZAddress + 4
orngXAddress = orngZAddress - 4
orngRot1 = orngYAddress + 8
orngRot2 = orngRot1 + 4
orngRot3 = orngRot2 + 4
orngRot4 = orngRot3 + 8
orngRot5 = orngRot4 + 4
orngRot6 = orngRot5 + 4
orngRot7 = orngRot6 + 8
orngRot8 = orngRot7 + 4
orngRot9 = orngRot8 + 4
'''