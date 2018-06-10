from inputs import get_gamepad  # pip install inputs
import threading

def deadzone(normalized_axis):
    if abs(normalized_axis) < 0.1: return 0.0
    return normalized_axis

class ControllerInput:
    def __init__(self):
        # self.throttle = 0.0
        self._gas_pedal = 0.0
        self._brake_pedal = 0.0

        self.steer = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.jump = 0
        self.boost = 0
        self.handbrake = 0

    @property
    def throttle(self):
        return self._gas_pedal - self._brake_pedal

    def main_poll_loop(self):
        while 1:
            events = get_gamepad()  # Blocking
            for event in events:
                # print(repr((event.ev_type, event.code, event.state)))
                if False: pass
                elif event.ev_type=='Absolute' and event.code=='ABS_RZ': self._gas_pedal = deadzone(event.state / 255.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_Z': self._brake_pedal = deadzone(event.state / 255.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_X': self.steer = self.yaw = deadzone(event.state / 32768.0)
                elif event.ev_type=='Absolute' and event.code=='ABS_Y': self.pitch = deadzone(-event.state / 32768.0)
                elif event.ev_type=='Key' and event.code=='BTN_THUMBL': self.roll = -event.state
                elif event.ev_type=='Key' and event.code=='BTN_SOUTH': self.jump = event.state
                elif event.ev_type=='Key' and event.code=='BTN_TR': self.boost = event.state
                elif event.ev_type=='Key' and event.code=='BTN_WEST': self.handbrake = event.state


controller = ControllerInput()
threading.Thread(target=controller.main_poll_loop, daemon=True).start()
