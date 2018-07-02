import socket
import time

from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures import game_interface


class BaseDotNetAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        self.name = name
        self.team = team
        self.index = index

    def run_independently(self, terminate_request_event):

        while not terminate_request_event.is_set():
            port = self.read_port_from_file()
            message = "add {0} {1} {2} {3}".format(self.name, self.team, self.index, game_interface.get_dll_directory())

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", port))
                s.send(bytes(message, "ASCII"))
                s.close()
            except ConnectionRefusedError:
                self.logger.warn("Could not connect to server!")

            time.sleep(1)
        else:
            self.retire()

    def retire(self):
        port = self.read_port_from_file()
        message = "remove {0}".format(self.index)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", port))
            s.send(bytes(message, "ASCII"))
            s.close()
        except ConnectionRefusedError:
            self.logger.warn("Could not connect to server!")
    
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
