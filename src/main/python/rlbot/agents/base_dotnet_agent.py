import msvcrt
import socket
import time

import psutil

from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.utils.structures import game_interface


class BaseDotNetAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        self.name = name
        self.team = team
        self.index = index
        self.port = self.read_port_from_file()
        self.is_retired = False

    def run_independently(self, terminate_request_event):

        while not terminate_request_event.is_set():
            message = "add {0} {1} {2} {3}".format(self.name, self.team, self.index, game_interface.get_dll_directory())

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", self.port))
                s.send(bytes(message, "ASCII"))
                s.close()
            except ConnectionRefusedError:
                self.logger.warn("Could not connect to server!")

            time.sleep(1)
        else:
            self.retire()

    def get_extra_pids(self):
        """
        Gets the list of process ids that should be marked as high priority.
        :return: A list of process ids that are used by this bot in addition to the ones inside the python process.
        """
        while not self.is_retired:
            for proc in psutil.process_iter():
                for conn in proc.connections():
                    if conn.laddr.port == self.port:
                        self.logger.debug('.NET socket server for {} appears to have pid {}'.format(self.name, proc.pid))
                        return [proc.pid]
            time.sleep(1)

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
        self.is_retired = True
    
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
