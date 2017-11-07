import math


class Agent:
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # 0 towards positive goal, 1 towards negative goal.
        self.index = index

    def get_output_vector(self, game_tick_packet):

        return [1, 1, 1, 1, 1, 1, 1, 1]

