import os

from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.botmanager.helper_process_request import HelperProcessRequest


class DroneAgent(BaseIndependentAgent):
    # Path to the hivemind helperprocess python file.
    hive_path = None
    # Bots with the same key will be part of the same hivemind.
    hive_key = None
    # Name of your hivemind that shows up in the console.
    hive_name = None

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        if self.hive_path is None:
            raise NotImplementedError('You need to specify a path to the hivemind file.')
        if self.hive_key is None:
            raise NotImplementedError('You need to specify a key for your hivemind.')
        if self.hive_name is None:
            raise NotImplementedError('You need to specify a name for your hivemind.')

    def run_independently(self, terminate_request_event):
        pass

    def get_helper_process_request(self) -> HelperProcessRequest:
        if not os.path.isfile(self.hive_path):
            raise FileNotFoundError(f'Could not find file: {self.hive_path}')

        # Appends hive_path to key so that hiveminds in different places don't compete.
        # Appends team to key so that each team has its own hivemind.
        key = f'{self.hive_path}{self.hive_key}{self.team}'

        # Creates request for helper process.
        options = {
            'name': self.hive_name
        }

        return HelperProcessRequest(self.hive_path, key, options=options)
