from RLBotFramework.agents.base_agent import BaseAgent
from controller_input import controller


class Agent(BaseAgent):

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
