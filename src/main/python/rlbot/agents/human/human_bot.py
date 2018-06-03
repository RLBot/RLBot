from rlbot.agents.base_agent import BaseAgent
from controller_input import controller


class Agent(BaseAgent):

    def get_output_vector(self, game_tick_packet):

        return [
            controller.throttle,
            controller.steer,
            controller.pitch,
            controller.yaw,
            controller.roll,
            controller.jump,
            controller.boost,
            controller.handbrake,
        ]
