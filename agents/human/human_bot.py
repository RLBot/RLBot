from agents.human.controller_input import controller

class Agent:
    def __init__(self, name, team, index):
        pass

    def get_output_vector(self, game_tick_packet):

        return [
            controller.fThrottle,
            controller.fSteer,
            controller.fPitch,
            controller.fYaw,
            controller.fRoll,
            controller.bJump,
            controller.bBoost,
            controller.bHandbrake,
        ]
