from inputs import get_gamepad  # pip install inputs
from rlbot.agents.base_agent import SimpleControllerState
import threading

def deadzone(normalized_axis):
    if abs(normalized_axis) < 0.1: return 0.0
    return normalized_axis

class ControllerInput:
    def __init__(self):
        self._gas_pedal = 0.0
        self._brake_pedal = 0.0

        self._left_stick_x = 0.0
        self._left_stick_y = 0.0

        self._right_stick_x = 0.0
        self._right_stick_y = 0.0

        self._north = 0
        self._east = 0
        self._south = 0
        self._west = 0

        self._hat_x = 0
        self._hat_y = 0

        self._tl = 0
        self._tr = 0

        self._thumb_l = 0
        self._thumb_r = 0

        self._select = 0
        self._start = 0


    @property
    def throttle(self):
        return self._gas_pedal - self._brake_pedal

    @property
    def steer(self):
        return self._left_stick_x

    @property
    def roll(self):
        return self._left_stick_x if self.aerial_control else 0.0

    @property
    def yaw(self):
        return 0.0 if self.aerial_control else self._left_stick_x

    @property
    def pitch(self):
        return self._left_stick_y

    @property
    def jump(self):
        return self._south

    @property
    def boost(self):
        return self._east

    @property
    def handbrake(self):
        return self._west 

    @property
    def aerial_control(self):
        return self._tr

    def get_output(self):
        output = SimpleControllerState()

        output.throttle = self.throttle
        output.steer = self.steer
        output.pitch = self.pitch
        output.yaw = self.yaw
        output.roll = self.roll
        output.jump = self.jump
        output.boost = self.boost
        output.handbrake = self.handbrake

        return output

    def main_poll_loop(self):
        while 1:
            events = get_gamepad()  # Blocking
            for event in events:
                #print(repr((event.ev_type, event.code, event.state)))
                if False: pass
                elif event.ev_type=='Absolute' and event.code=='ABS_RZ': self._gas_pedal = deadzone(event.state / 255.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_Z': self._brake_pedal = deadzone(event.state / 255.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_X': self._left_stick_x = deadzone(event.state / 32768.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_Y': self._left_stick_y = deadzone(-event.state / 32768.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_RX': self._right_stick_x = deadzone(event.state / 32768.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_RY': self._right_stick_y = deadzone(-event.state / 32768.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_HAT0X': self._hat_x = event.state
                elif event.ev_type=='Absolute' and event.code=='ABS_HAT0Y': self._hat_y = event.state
                elif event.ev_type=='Key' and event.code=='BTN_NORTH': self._north = event.state
                elif event.ev_type=='Key' and event.code=='BTN_EAST': self._east = event.state
                elif event.ev_type=='Key' and event.code=='BTN_SOUTH': self._south = event.state
                elif event.ev_type=='Key' and event.code=='BTN_WEST': self._west = event.state
                elif event.ev_type=='Key' and event.code=='BTN_TL': self._tl = event.state
                elif event.ev_type=='Key' and event.code=='BTN_TR': self._tr = event.state
                elif event.ev_type=='Key' and event.code=='BTN_THUMBL': self._thumb_l = event.state
                elif event.ev_type=='Key' and event.code=='BTN_THUMBR': self._thumb_r = event.state
                elif event.ev_type=='Key' and event.code=='BTN_SELECT': self._select = event.state
                elif event.ev_type=='Key' and event.code=='BTN_START': self._start = event.state
                elif event.ev_type!='Sync': print(repr((event.ev_type, event.code, event.state)))

                
    
    @property
    def left_stick_x(self):
        return self._left_stick_x

    @property
    def left_stick_y(self):
        return self._left_stick_y

    @property
    def right_stick_x(self):
        return self._right_stick_x

    @property
    def right_stick_y(self):
        return self._right_stick_y

    @property
    def up(self):
        return True if self._hat_y==-1 else False

    @property  
    def down(self):
        return True if self._hat_y==1 else False

    @property
    def left(self):
        return True if self._hat_x==-1 else False

    @property
    def right(self):
        return True if self._hat_x==1 else False

    @property
    def start(self):
        return self._select


    #xbox exclusive
    @property
    def A(self):
        return self._south

    @property
    def B(self):
        return self._east
    
    @property
    def X(self):
        return self._west
    
    @property
    def Y(self):
        return self._north

    @property
    def left_back(self):
        return self._tl
    
    @property
    def right_back(self):
        return self._tr

    @property
    def left_trigger(self):
        return self._brake_pedal
    
    @property
    def right_trigger(self):
        return self._gas_pedal

    @property
    def left_thumb(self):
        return self._thumb_l

    @property
    def right_thumb(self):
        return self._thumb_r
    
    @property
    def back(self):
        return self._start


    #ps3 exclusive
    @property
    def cross(self):
        return self._south

    @property
    def circle(self):
        return self._east
    
    @property
    def square(self):
        return self._west
    
    @property
    def triangle(self):
        return self._north

    @property
    def L1(self):
        return self._tl
    
    @property
    def R1(self):
        return self._tr

    @property
    def L2(self):
        return self._brake_pedal
    
    @property
    def R2(self):
        return self._gas_pedal

    @property
    def L3(self):
        return self._thumb_l

    @property
    def R3(self):
        return self._thumb_r
    
    @property
    def select(self):
        return self._start
                

controller = ControllerInput()
threading.Thread(target=controller.main_poll_loop, daemon=True).start()
