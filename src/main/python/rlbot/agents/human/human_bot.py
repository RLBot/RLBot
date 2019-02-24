from rlbot.agents.base_agent import BaseAgent
from controller_input import controller


class Agent(BaseAgent):

    def get_output(self, game_tick_packet):
        return controller.get_output()

