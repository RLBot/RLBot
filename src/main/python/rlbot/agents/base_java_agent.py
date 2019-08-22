import os
import time

import psutil
from py4j.java_gateway import GatewayParameters
from py4j.java_gateway import JavaGateway

from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.botmanager.helper_process_request import HelperProcessRequest
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures import game_interface


class BaseJavaAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.gateway = None
        self.javaInterface = None
        self.logger = get_logger('ProtoJava' + str(self.index))
        self.port = self.read_port_from_file()
        self.is_retired = False
        self.java_executable_path = None

    def read_port_from_file(self):
        try:
            location = self.get_port_file_path()

            with open(location, "r") as portFile:
                return int(portFile.readline().rstrip())

        except ValueError:
            self.logger.warn("Failed to parse port file!")
            raise

    def get_port_file_path(self):
        raise NotImplementedError

    def run_independently(self, terminate_request_event):
        self.init_py4j_stuff()

        while not terminate_request_event.is_set():
            # Continuously make sure the java interface is started and the bot is registered.
            # These functions can be called repeatedly without any bad effects.
            # This is useful for re-engaging the java server if it gets restarted during development.
            try:
                self.javaInterface.ensureStarted(game_interface.get_dll_location())
                self.javaInterface.ensureBotRegistered(self.index, self.name, self.team)
            except Exception as e:
                self.logger.warn(str(e))
            time.sleep(1)

    def get_helper_process_request(self):
        if self.is_executable_configured():
            return HelperProcessRequest(python_file_path=None, key=__file__ + str(self.port),
                                        executable=self.java_executable_path,
                                        current_working_directory=os.path.dirname(self.java_executable_path))
        return None

    def is_executable_configured(self):
        return self.java_executable_path is not None and os.path.isfile(self.java_executable_path)

    def get_extra_pids(self):
        """
        Gets the list of process ids that should be marked as high priority.
        :return: A list of process ids that are used by this bot in addition to the ones inside the python process.
        """
        while not self.is_retired:
            for proc in psutil.process_iter():
                for conn in proc.connections():
                    if conn.laddr.port == self.port:
                        self.logger.debug(f'py4j server for {self.name} appears to have pid {proc.pid}')
                        return [proc.pid]
            if self.is_executable_configured():
                # The helper process will start java and report the PID. Nothing to do here.
                return []
            time.sleep(1)
            if self.java_executable_path is None:
                self.logger.info(
                    "Can't auto-start java because no executable is configured. Please start java manually!")
            else:
                self.logger.info(f"Can't auto-start java because {self.java_executable_path} is not found. "
                                 "Please start java manually!")

    def retire(self):
        try:
            # Shut down the whole java process, because currently java is clumsy with the interface dll
            # and cannot really survive a restart of the python framework.
            self.javaInterface.shutdown()
        except Exception as e:
            self.logger.warn(str(e))
        self.is_retired = True

    def init_py4j_stuff(self):
        self.logger.info("Connecting to Java Gateway on port " + str(self.port))
        self.gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True, port=self.port))
        self.javaInterface = self.gateway.entry_point
        self.logger.info("Connection to Java successful!")
