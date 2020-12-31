import os
import socket
import time

import psutil
from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.botmanager.helper_process_request import HelperProcessRequest
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures import game_interface
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.game_interface import GameInterface


class ExecutableWithSocketAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.logger = get_logger('ExeSocket' + str(self.index))
        self.is_retired = False
        self.executable_path = None
        self.game_interface = GameInterface(self.logger)
        self.game_tick_packet = GameTickPacket()
        self.spawn_id_seen = False

    def run_independently(self, terminate_request_event):
        self.game_interface.load_interface()

        while not terminate_request_event.is_set():

            self.game_interface.update_live_data_packet(self.game_tick_packet)
            packet_spawn_id = self.game_tick_packet.game_cars[self.index].spawn_id
            if self.spawn_id_seen:
                if packet_spawn_id != self.spawn_id:
                    break  # This will cause the bot to retire.
            elif packet_spawn_id == self.spawn_id and self.game_tick_packet.game_info.is_round_active:
                self.spawn_id_seen = True

            # Continuously make sure the the bot is registered.
            # These functions can be called repeatedly without any bad effects.
            # This is useful for re-engaging the socket server if it gets restarted during development.
            message = self.build_add_command()
            self.send_command(message)
            time.sleep(1)

    def get_helper_process_request(self):
        if self.is_executable_configured():
            return HelperProcessRequest(python_file_path=None, key=__file__ + str(self.get_port()),
                                        executable=self.executable_path, exe_args=[str(self.get_port())],
                                        current_working_directory=os.path.dirname(self.executable_path))
        return None

    def retire(self):
        message = self.build_retire_command()
        self.logger.info(f"Sending retire message for {self.name}")
        self.send_command(message)
        self.is_retired = True

    def build_add_command(self) -> str:
        return f"add\n{self.name}\n{self.team}\n{self.index}\n{game_interface.get_dll_directory()}"

    def build_retire_command(self) -> str:
        return f"remove\n{self.index}"

    def send_command(self, message):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect(("127.0.0.1", self.get_port()))
            s.send(bytes(message, "ASCII"))
            s.close()
            return True
        except ConnectionRefusedError:
            self.logger.warn("Could not connect to server!")
            return False

    def is_executable_configured(self):
        return self.executable_path is not None and os.path.isfile(self.executable_path)

    def get_extra_pids(self):
        """
        Gets the list of process ids that should be marked as high priority.
        :return: A list of process ids that are used by this bot in addition to the ones inside the python process.
        """

        if self.is_executable_configured():
            # The helper process will start the exe and report the PID. Nothing to do here.
            return []

        while not self.is_retired:
            for proc in psutil.process_iter():
                for conn in proc.connections():
                    if conn.laddr.port == self.get_port():
                        self.logger.debug(f'server for {self.name} appears to have pid {proc.pid}')
                        return [proc.pid]
            time.sleep(1)
            if self.executable_path is None:
                self.logger.info(
                    "Can't auto-start because no executable is configured. Please start manually!")
            else:
                self.logger.info(f"Can't auto-start because {self.executable_path} is not found. "
                                 "Please start manually!")

    def get_port(self) -> int:
        raise NotImplementedError
