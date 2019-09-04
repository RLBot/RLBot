import os

from rlbot.agents.base_agent import BOT_CONFIG_AGENT_HEADER
from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.botmanager import scratch_manager
from rlbot.botmanager.helper_process_request import HelperProcessRequest
from rlbot.parsing.custom_config import ConfigObject


class BaseScratchAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.port: int = None
        self.spawn_browser: bool = False
        self.sb3file: str = None
        self.headless: bool = False
        self.separate_browsers: bool = False
        self.pretend_blue_team: bool = False

    def get_helper_process_request(self):
        file = os.path.realpath(scratch_manager.__file__)
        self.logger.info(self.sb3file)
        port = self.port + self.index if self.separate_browsers else self.port
        key = f'scratch_helper{self.sb3file or ""}-{port}'
        options = {
            'port': port,
            'spawn_browser': self.spawn_browser,
            'sb3-file': self.sb3file,
            'headless': self.headless,
            'pretend_blue_team': self.pretend_blue_team
        }
        return HelperProcessRequest(file, key, options=options)

    def run_independently(self, terminate_request_event):
        pass

    def load_config(self, config_header):
        self.port = config_header.getint('port')
        self.spawn_browser = config_header.getint('spawn_browser')
        self.sb3file = config_header.getpath('sb3file')
        self.headless = config_header.getboolean('headless')
        self.separate_browsers = config_header.getboolean('separate_browsers')
        self.pretend_blue_team = config_header.getboolean('pretend_blue_team')

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('port', int, default=42008,
                         description='Port to use for websocket communication')
        params.add_value('spawn_browser', bool, default=False,
                         description='True if we should automatically open google chrome to the scratch page.')
        params.add_value('sb3file', str, default=None,
                         description='Location of the scratch .sb3 file to load automatically')
        params.add_value('headless', bool, default=False,
                         description='If true, bot will run automatically with no visible web browser')
        params.add_value('separate_browsers', bool, default=False,
                         description='If true, each bot will get its own separate browser instance '
                                     'and pretend to be player 1. Works best with spawn_browser = True.')
        params.add_value('pretend_blue_team', bool, default=False,
                         description="If true, and if your bots in the browser all on orange, we will pretend in "
                                     "Scratch that they're on the blue team.")
