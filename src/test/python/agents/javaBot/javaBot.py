from rlbot.agents.executable_with_socket_agent import ExecutableWithSocketAgent


class JavaBot(ExecutableWithSocketAgent):
    def get_port(self):
        return 24008
