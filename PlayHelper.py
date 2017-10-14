import pyvjoy

class PlayHelper:
	
    def __init__(self, player_index):
        self.device = pyvjoy.VJoyDevice(player_index + 1)

    def update_controller(self, output):
        self.device.data.wAxisX = output[0]
        self.device.data.wAxisY = output[1]
        self.device.data.wAxisZRot = output[2]
        self.device.data.wAxisZ = output[3]
        self.device.data.lButtons = (1 * output[4]) + (2 * output[5]) + (4 * output[6])

        self.device.data.wAxisXRot = 16383
        self.device.data.wAxisYRot = 16383

        self.device.update() # Send data to vJoy device
