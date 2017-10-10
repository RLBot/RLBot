import time
import pyvjoy
import configparser

class play_helper:
	
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read('rlbot.cfg')
        self.p1Enabled = ("True" == config.get('Player Configuration', 'p1Enabled'))
        self.p2Enabled = ("True" == config.get('Player Configuration', 'p2Enabled'))
        if (self.p1Enabled):
            self.p1 = pyvjoy.VJoyDevice(1)
        if (self.p2Enabled):
            self.p2 = pyvjoy.VJoyDevice(2)

    def reset_contollers(self):
        if (self.p1Enabled):
            p1 = pyvjoy.VJoyDevice(1)
            p1.data.wAxisX = 16383
            p1.data.wAxisY = 16383
            p1.data.wAxisYRot = 16383
            p1.data.wAxisXRot = 16383
            p1.data.wAxisZ = 0
            p1.data.wAxisZRot = 0
            p1.data.lButtons = 0
            #send data to vJoy device
            p1.update()

        if (self.p2Enabled):
            p2 = pyvjoy.VJoyDevice(2)
            p2.data.wAxisX = 16383
            p2.data.wAxisY = 16383
            p2.data.wAxisYRot = 16383
            p2.data.wAxisXRot = 16383
            p2.data.wAxisZ = 0
            p2.data.wAxisZRot = 0
            p2.data.lButtons = 0
            p2.update()

        
    def update_controllers(self, output1, output2):
        # Update controller buttons for both players

        if (self.p1Enabled):
            self.p1.data.wAxisX = output1[0]
            self.p1.data.wAxisY = output1[1]
            self.p1.data.wAxisZRot = output1[2]
            self.p1.data.wAxisZ = output1[3]
            self.p1.data.lButtons = (1 * output1[4]) + (2 * output1[5]) + (4 * output1[6])
            self.p1.data.wAxisXRot = 16383
            self.p1.data.wAxisYRot = 16383
            #send data to vJoy device
            self.p1.update()

        if (self.p2Enabled):
            self.p2.data.wAxisX = output2[0]
            self.p2.data.wAxisY = output2[1]
            self.p2.data.wAxisZRot = output2[2]
            self.p2.data.wAxisZ = output2[3]
            self.p2.data.lButtons = (1 * output2[4]) + (2 * output2[5]) + (4 * output2[6])
            self.p2.data.wAxisXRot = 16383
            self.p2.data.wAxisYRot = 16383
            self.p2.update()
