import os

from rlbot.agents.base_java_agent import BaseJavaAgent


class JavaBot(BaseJavaAgent):
    def get_port_file_path(self):
        # Look for a port.cfg file in the same directory as THIS python file.
        return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'port.cfg'))
