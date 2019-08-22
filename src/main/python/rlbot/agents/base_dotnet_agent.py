import os
import socket
import time

import psutil

from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.botmanager.helper_process_request import HelperProcessRequest
from rlbot.utils.structures import game_interface


class BaseDotNetAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.port = self.read_port_from_file()
        self.is_retired = False
        self.dotnet_executable_path = None

    def run_independently(self, terminate_request_event):

        while not terminate_request_event.is_set():
            message = f"add\n{self.name}\n{self.team}\n{self.index}\n{game_interface.get_dll_directory()}"
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

    def get_helper_process_request(self):
        if self.is_executable_configured():
            return HelperProcessRequest(python_file_path=None, key=__file__ + str(self.port),
                                        executable=self.dotnet_executable_path,
                                        current_working_directory=os.path.dirname(self.dotnet_executable_path))
        return None

    def is_executable_configured(self):
        return self.dotnet_executable_path is not None and os.path.isfile(self.dotnet_executable_path)

    def get_extra_pids(self):
        """
        Gets the list of process ids that should be marked as high priority.
        :return: A list of process ids that are used by this bot in addition to the ones inside the python process.
        """
        while not self.is_retired:
            for proc in psutil.process_iter():
                for conn in proc.connections():
                    if conn.laddr.port == self.port:
                        self.logger.debug(f".NET socket server for {self.name} appears to have pid {proc.pid}")
                        return [proc.pid]
            if self.is_executable_configured():
                return []
            time.sleep(1)
            if self.dotnet_executable_path is None:
                self.logger.info("Can't auto-start .NET executable because no executable is configured. "
                                 "Please start the .NET bot manually!")
            else:
                self.logger.info(f"Can't auto-start .NET executable because {self.dotnet_executable_path} "
                                 "is not found. Please start the .NET bot manually!")

    def retire(self):
        port = self.read_port_from_file()
        message = f"remove\n{self.index}"

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
