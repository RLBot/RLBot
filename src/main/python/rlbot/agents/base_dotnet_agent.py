import msvcrt
import os
import time

import psutil
from py4j.java_gateway import GatewayParameters
from py4j.java_gateway import JavaGateway
from rlbot.utils.structures import game_interface

from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.utils.logging_utils import get_logger


class BaseDotNetAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        # TODO: Set up what is needed to connect to server
        raise NotImplementedError

    def run_independently(self, terminate_request_event):
        # TODO: Connect to C# server and give information
        raise NotImplementedError

    def retire(self):
        # TODO: Tell C# server to retire the bot
        raise NotImplementedError
    
    def read_port_from_file(self):
        try:
            location = self.get_port_file_path()

            with open(location, "r") as port_file:
                return int(port_file.readline().rstrip())

        except ValueError:
            self.logger.warn("Failed to parse port file!")
            raise

    def get_port_file_path(self):
        raise NotImplementedError
