from inputs import get_gamepad  # pip install inputs
import threading

def deadzone(normalized_axis):
    if abs(normalized_axis) < 0.1: return 0.0
    return normalized_axis

class ControllerInput:
    def __init__(self):
        # self.fThrottle = 0.0
        self._gas_pedal = 0.0
        self._brake_pedal = 0.0

        self.fSteer = 0.0
        self.fPitch = 0.0
        self.fYaw = 0.0
        self.fRoll = 0.0
        self.bJump = 0
        self.bBoost = 0
        self.bHandbrake = 0

    @property
    def fThrottle(self):
        return self._gas_pedal - self._brake_pedal

    def main_poll_loop(self):
        while 1:
            events = get_gamepad()  # Blocking
            for event in events:
                # print(repr((event.ev_type, event.code, event.state)))
                if False: pass
                elif event.ev_type=='Absolute' and event.code=='ABS_RZ': self._gas_pedal = deadzone(event.state / 255.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_Z': self._brake_pedal = deadzone(event.state / 255.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_X': self.fSteer = self.fYaw = deadzone(event.state / 32768.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_Y': self.fPitch = deadzone(-event.state / 32768.0)
                elif event.ev_type=='Key' and event.code=='BTN_THUMBL': self.fRoll = -event.state
                elif event.ev_type=='Key' and event.code=='BTN_SOUTH': self.bJump = event.state
                elif event.ev_type=='Key' and event.code=='BTN_TR': self.bBoost = event.state
                elif event.ev_type=='Key' and event.code=='BTN_WEST': self.bHandbrake = event.state


controller = ControllerInput()
threading.Thread(target=controller.main_poll_loop, daemon=True).start()
