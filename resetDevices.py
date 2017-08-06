import pyvjoy
import time

#Pythonic API, item-at-a-time

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
