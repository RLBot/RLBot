import pyvjoy
import time

#Pythonic API, item-at-a-time

p2 = pyvjoy.VJoyDevice(2)

time.sleep(3)

p2.data.lButtons = 128
p2.update()

time.sleep(1)

p2.data.lButtons = 0
p2.update()
