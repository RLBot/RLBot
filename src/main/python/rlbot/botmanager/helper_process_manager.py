import multiprocessing as mp
import subprocess
from multiprocessing import Event

from rlbot.botmanager.agent_metadata import AgentMetadata
from rlbot.utils.class_importer import import_class_with_base

from rlbot.botmanager.bot_helper_process import BotHelperProcess


class HelperProcessManager:
    """
    Creates and keeps track of BotHelperProcess instances.
    """

    def __init__(self, quit_event: Event):
        self.quit_event = quit_event
        self.helper_process_map = {}

    def start_or_update_helper_process(self, agent_metadata: AgentMetadata):
        """
        Examines the agent metadata to see if the agent needs a helper process. If the process is not running yet,
        create the process. Once the process is running, feed the agent metadata to it.

        If a process is created here, the pid will be added to the agent metadata.
        """

        helper_req = agent_metadata.helper_process_request

        if helper_req is not None:
            if helper_req.key not in self.helper_process_map:
                metadata_queue = mp.Queue()
                if helper_req.python_file_path is not None:
                    process = mp.Process(target=run_helper_process,
                                         args=(helper_req.python_file_path, metadata_queue, self.quit_event,
                                               helper_req.options))
                    process.daemon = True
                    process.start()
                    agent_metadata.pids.add(process.pid)

                    self.helper_process_map[helper_req.key] = metadata_queue

                if helper_req.executable is not None:
                    launch = [helper_req.executable]
                    if helper_req.exe_args is not None:
                        launch.extend(helper_req.exe_args)
                    process = subprocess.Popen(launch, cwd=helper_req.current_working_directory)

                    agent_metadata.pids.add(process.pid)

                    self.helper_process_map[helper_req.key] = metadata_queue

            metadata_queue = self.helper_process_map[helper_req.key]
            metadata_queue.put(agent_metadata)


def run_helper_process(python_file, metadata_queue, quit_event, options):
    """
    :param python_file: The absolute path of a python file containing the helper process that should be run.
    It must define a class which is a subclass of BotHelperProcess.
    :param metadata_queue: A queue from which the helper process will read AgentMetadata updates.
    :param quit_event: An event which should be set when rlbot is shutting down.
    :param options: A dict with arbitrary options that will be passed through to the helper process.
    """
    class_wrapper = import_class_with_base(python_file, BotHelperProcess)
    helper_class = class_wrapper.get_loaded_class()
    helper = helper_class(metadata_queue, quit_event, options)
    helper.start()
