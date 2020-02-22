from signal import SIGTERM
from subprocess import Popen

import queue
import os

import rlbot
from rlbot.botmanager.agent_metadata import AgentMetadata
from rlbot.botmanager.bot_helper_process import BotHelperProcess
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_interface import get_dll_directory

class SubprocessHivemind(BotHelperProcess):

    # Terminology:
    # hivemind - main process controlling the drones.
    # drone - a bot under the hivemind's control.

    # Path to the executable.
    exec_path = None

    def __init__(self, agent_metadata_queue, quit_event, options):
        super().__init__(agent_metadata_queue, quit_event, options)

        # Sets up the logger. The string is the name of your hivemind.
        # This is configured inside your config file under hivemind_name.
        self.logger = get_logger(options['name'])

        # Give a warning if exec_path was given.
        if 'exec_path' is None:
            raise NotImplementedError(
                "Please specify the exec_path in your subclass of SubprocessHivemind.")

        # drone_indices is a set of bot indices
        # which requested this hivemind with the same key.
        self.drone_indices = set()

    def try_receive_agent_metadata(self):
        """Adds all drones with the correct key to our set of running indices."""
        while not self.metadata_queue.empty():
            # Tries to get the next agent from the queue.
            single_agent_metadata: AgentMetadata = self.metadata_queue.get(
                timeout=1.0)
            # Adds the index to the drone_indices.
            self.drone_indices.add(single_agent_metadata.index)

    def start(self):
        """Starts the BotHelperProcess - Hivemind."""
        # Prints an activation message into the console.
        # This lets you know that the process is up and running.
        self.logger.debug("Hello, world!")

        # Collect drone indices that requested a helper process with our key.
        self.logger.info("Collecting drones; give me a moment.")
        self.try_receive_agent_metadata()
        self.logger.info("Starting subprocess!")

        if not os.path.isfile(self.exec_path): 
            raise FileNotFoundError(f"Could not find file: {self.exec_path}")

        # Starts the process.
        # The drone indices are all the numbers after --drone-indices.
        # example.exe --rlbot-version 1.35.5 --rlbot-dll-directory some/directory/dll/ --drone-indices 0,1,2,3,4,5
        process = Popen(
            [
                self.exec_path,
                '--rlbot-version',
                rlbot.__version__,
                '--rlbot-dll-directory',
                get_dll_directory(),
                '--drone-indices',
                ','.join([str(index) for index in self.drone_indices])
            ]
        )

        # Wait until we get a quit_event, and then terminate the process.
        self.quit_event.wait()
        process.send_signal(SIGTERM)
        process.wait()
