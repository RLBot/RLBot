from agents.human.controller_input import controller
from RLBotFramework.agents.base_agent import BaseAgent


class Agent(BaseAgent):
    def __init__(self, name, team, index):
        super(Agent, self).__init__(name, team, index)

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
