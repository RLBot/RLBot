import multiprocessing
import os
import socket
import subprocess
import sys
from typing import Type

import psutil
from rlbot.agents.base_agent import BOT_CONFIG_AGENT_HEADER
from rlbot.agents.executable_with_socket_agent import ExecutableWithSocketAgent
from rlbot.agents.standalone.standalone_bot_config import StandaloneBotConfig
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle
from rlbot.utils.process_configuration import configure_process, get_team_cpus


class ExecutableWithSocketStandaloneBot(ExecutableWithSocketAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)

    def find_process_using_port(self, port: int):
        for proc in psutil.process_iter():
            for conn in proc.connections():
                if conn.laddr.port == port:
                    return proc
        return None

    def is_port_open(self, port: int):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("127.0.0.1", port))
            s.close()
            return True
        except ConnectionRefusedError:
            s.close()
            return False

    def send_add_command(self):
        message = self.build_add_command()
        self.logger.info(f"About to send add message for {self.name}")
        return self.send_command(message)

    def launch_executable(self):
        self.logger.info("Launching executable...")
        launch = [self.executable_path, str(self.get_port())]
        proc = subprocess.Popen(launch, cwd=os.path.dirname(self.executable_path))
        process = psutil.Process(pid=proc.pid)
        configure_process(process, get_team_cpus(self.team), infer_multi_team=True)
        self.logger.info("Launched executable instance")


def run_bot(agent_class: Type[ExecutableWithSocketStandaloneBot]):
    config = StandaloneBotConfig(sys.argv)

    bundle = get_bot_config_bundle(config.config_file)
    config_obj = agent_class.base_create_agent_configurations()
    config_obj.parse_file(bundle.config_obj, config_directory=bundle.config_directory)

    agent = agent_class(config.name, config.team, config.player_index)
    agent.spawn_id = config.spawn_id
    agent.load_config(config_obj.get_header(BOT_CONFIG_AGENT_HEADER))
    if not agent.send_add_command():
        agent.launch_executable()
    agent.run_independently(multiprocessing.Event())
    agent.retire()
