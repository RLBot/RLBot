from multiprocessing import Event
from signal import SIGTERM
from subprocess import Popen

import rlbot
from rlbot.agents.base_agent import BOT_CONFIG_AGENT_HEADER
from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.parsing.custom_config import ConfigHeader, ConfigObject
from rlbot.utils.structures.game_interface import get_dll_directory


class BaseSubprocessAgent(BaseIndependentAgent):
    """An Agent which simply delegates to an external process."""

    path: str

    @staticmethod
    def create_agent_configurations(config: ConfigObject) -> None:
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('path', str, description='The path to the exe for the bot')

    def load_config(self, config_header: ConfigHeader) -> None:
        self.path = config_header.getpath('path')

    def run_independently(self, terminate_request_event: Event) -> None:
        # This argument sequence is consumed by Rust's `rlbot::run`.
        process = Popen([
            self.path,
            '--rlbot-version',
            rlbot.__version__,
            '--rlbot-dll-directory',
            get_dll_directory(),
            '--player-index',
            str(self.index),
        ])

        # Block until we are asked to terminate, and then do so.
        terminate_request_event.wait()
        process.send_signal(SIGTERM)
        process.wait()
