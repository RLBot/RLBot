import os

import time
from py4j.java_gateway import GatewayParameters
from py4j.java_gateway import JavaGateway

from RLBotFramework.agents.base_independent_agent import BaseIndependentAgent
from RLBotFramework.utils.logging_utils import get_logger


class BaseJavaAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.gateway = None
        self.javaInterface = None
        self.logger = get_logger('ProtoJava' + str(self.index))
        self.port = self.read_port_from_file()

    def read_port_from_file(self):
        try:
            location = self.get_port_file_path()

            with open(os.path.join(location, "port.cfg"), "r") as portFile:
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
                self.javaInterface.ensureStarted()
                self.javaInterface.ensureBotRegistered(self.index, self.name)
            except Exception as e:
                self.logger.warn(str(e))
            time.sleep(1)

    def get_extra_pids(self):
        """
        Gets the list of process ids that should be marked as high priority.
        :return: A list of process ids that are used by this bot in addition to the ones inside the python process.
        """
        return []

    def retire(self):
        try:
            self.javaInterface.retireBot(self.index)
        except Exception as e:
            self.logger.warn(str(e))

    def init_py4j_stuff(self):
        self.logger.info("Connecting to Java Gateway on port " + str(self.port))
        self.gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True, port=self.port))
        self.javaInterface = self.gateway.entry_point
        self.logger.info("Connection to Java successful!")
