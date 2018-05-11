import os
import time

from RLBotFramework.agents.base_java_agent import BaseJavaAgent


class ProtoJava(BaseJavaAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)

    def get_port_file_path(self):
        # Look for a port.cfg file in the same directory as THIS python file.
        return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def run_independently(self, terminate_request_event):
        self.init_py4j_stuff()

        while not terminate_request_event.is_set():
            # Continuously make sure the java interface is started and the bot is registered.
            # These functions can be called repeatedly without any bad effects.
            # This is useful for re-engaging the java server if it gets restarted during development.
            try:
                self.javaInterface.ensureStarted()
                self.javaInterface.ensureFlatBotRegistered(self.index, self.name, self.team)
            except Exception as e:
                self.logger.warn(str(e))
            time.sleep(1)
