from rlbot.agents.executable_with_socket_agent import ExecutableWithSocketAgent


class JavaBot(ExecutableWithSocketAgent):
    def get_port(self):
        return 24008

    def build_add_command(self) -> str:
        # TODO: pull the RLBot port from somewhere instead of hard coding
        return f"addsocket\n{self.name}\n{self.team}\n{self.index}\nlocalhost\n23234"
