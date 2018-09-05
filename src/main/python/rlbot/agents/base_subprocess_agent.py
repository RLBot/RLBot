from multiprocessing import Event
from signal import CTRL_C_EVENT
from subprocess import Popen

from rlbot.agents.base_agent import BOT_CONFIG_AGENT_HEADER
from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.parsing.custom_config import ConfigHeader, ConfigObject


class BaseSubprocessAgent(BaseIndependentAgent):
    """An Agent which simply delegates to an external process."""

    path: str

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('path', str, description='The path to the exe for the bot')

    def load_config(self, config_header: ConfigHeader) -> None:
        self.path = config_header.get('path')

    def run_independently(self, terminate_request_event: Event) -> None:
        # This argument sequence is consumed by Rust's `rlbot::run`.
        process = Popen([self.path, '--player-index', str(self.index)])

        # Block until we are asked to terminate, and then do so.
        terminate_request_event.wait()
        process.send_signal(CTRL_C_EVENT)
        process.wait()
