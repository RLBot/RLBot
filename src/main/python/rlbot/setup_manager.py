import msvcrt
import multiprocessing as mp
import os
import queue
import sys
import time

# Make sure the flatbuffers dir can be located on sys.path so that the generated files can find it.
# TODO: Use pip for flatbuffers if they ever get their act together: https://github.com/google/flatbuffers/issues/4507
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs")))

from rlbot.botmanager.helper_process_manager import HelperProcessManager
from rlbot.base_extension import BaseExtension
from rlbot.botmanager.bot_manager_flatbuffer import BotManagerFlatbuffer
from rlbot.botmanager.bot_manager_independent import BotManagerIndependent
from rlbot.botmanager.bot_manager_struct import BotManagerStruct
from rlbot.parsing.rlbot_config_parser import create_bot_config_layout, parse_configurations, EXTENSION_PATH_KEY
from rlbot.utils.class_importer import import_class_with_base, import_agent
from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.utils.process_configuration import configure_processes
from rlbot.utils.structures.game_interface import GameInterface
from rlbot.utils.structures.quick_chats import QuickChatManager
from rlbot.utils.structures.start_match_structures import MatchSettings

# By default, look for rlbot.cfg in the current working directory.
DEFAULT_RLBOT_CONFIG_LOCATION = os.path.realpath('./rlbot.cfg')
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'


class SetupManager:
    has_started = False
    num_participants = None
    should_stop = False
    names = None
    teams = None
    python_files = None
    parameters = None
    start_match_configuration = None
    agent_metadata_queue = None
    extension = None

    def __init__(self):
        self.logger = get_logger(DEFAULT_LOGGER)
        self.game_interface = GameInterface(self.logger)
        self.quick_chat_manager = QuickChatManager(self.game_interface)
        self.quit_event = mp.Event()
        self.helper_process_manager = HelperProcessManager(self.quit_event)
        self.bot_quit_callbacks = []
        self.agent_metadata_map = {}

    def startup(self):
        if self.has_started:
            return
        self.logger.debug("Starting up game management")
        self.game_interface.inject_dll()
        self.game_interface.load_interface()
        self.agent_metadata_queue = mp.Queue()
        self.has_started = True

    def load_config(self, framework_config=None, config_location=DEFAULT_RLBOT_CONFIG_LOCATION, bot_configs=None, looks_configs=None):
        """
        :param framework_config: A config object that indicates what bots to run. May come from parsing a rlbot.cfg.
        :param config_location: The location of the rlbot.cfg file, which will be used to resolve relative paths.
        :param bot_configs: Overrides for bot configurations.
        :param looks_configs: Overrides for looks configurations.
        """
        self.logger.debug('reading the configs')

        # Set up RLBot.cfg
        if framework_config is None:
            framework_config = create_bot_config_layout()
            framework_config.parse_file(config_location, max_index=10)
        if bot_configs is None:
            bot_configs = {}
        if looks_configs is None:
            looks_configs = {}

        # Open anonymous shared memory for entire GameInputPacket and map buffer
        self.start_match_configuration = MatchSettings()

        self.num_participants, self.names, self.teams, self.python_files, self.parameters = parse_configurations(
            self.start_match_configuration, framework_config, config_location, bot_configs, looks_configs)

        self.game_interface.participants = self.num_participants
        self.game_interface.start_match_configuration = self.start_match_configuration

        extension_path = framework_config.get(RLBOT_CONFIGURATION_HEADER, EXTENSION_PATH_KEY)
        if extension_path is not None and extension_path != "None":
            self.load_extension(extension_path)

    def launch_bot_processes(self):
        self.logger.debug("Launching bot processes")

        # Launch processes
        for i in range(self.num_participants):
            if self.start_match_configuration.player_configuration[i].rlbot_controlled:
                queue_holder = self.quick_chat_manager.create_queue_for_bot(i, self.teams[i])
                callback = mp.Event()
                self.bot_quit_callbacks.append(callback)
                process = mp.Process(target=SetupManager.run_agent,
                                     args=(self.quit_event, callback, self.parameters[i],
                                           str(self.start_match_configuration.player_configuration[i].name),
                                           self.teams[i], i, self.python_files[i], self.agent_metadata_queue, queue_holder))
                process.start()

        self.logger.debug("Successfully started bot processes")

    def run(self):
        self.should_stop = False
        self.quick_chat_manager.start_manager(self.quit_event)
        self.logger.debug("Successfully started quick chat manager")
        self.game_interface.start_match()
        self.logger.info("Match has started")

        self.logger.info("Press any character to exit")
        while True and not self.should_stop:
            if msvcrt.kbhit():
                msvcrt.getch()
                break
            try:
                single_agent_metadata = self.agent_metadata_queue.get(timeout=1)
                self.helper_process_manager.start_or_update_helper_process(single_agent_metadata)
                self.agent_metadata_map[single_agent_metadata.index] = single_agent_metadata
                configure_processes(self.agent_metadata_map, self.logger)
            except queue.Empty:
                pass
            except Exception as ex:
                self.logger.error(ex)
                pass

    def shut_down(self):
        self.logger.info("Shutting Down")

        self.quit_event.set()

        # Wait for all processes to terminate before terminating main process
        terminated = False
        while not terminated:
            terminated = True
            for callback in self.bot_quit_callbacks:
                if not callback.is_set():
                    terminated = False
            time.sleep(0.1)

    def load_extension(self, extension_filename):
        extension_class = import_class_with_base(extension_filename, BaseExtension).get_loaded_class()
        self.extension = extension_class(self)
        self.game_interface.set_extension(self.extension)

    @staticmethod
    def run_agent(terminate_event, callback_event, config_file, name, team, index, python_file,
                  agent_telemetry_queue, queue_holder):

        agent_class_wrapper = import_agent(python_file)

        if hasattr(agent_class_wrapper.get_loaded_class(), "run_independently"):
            bm = BotManagerIndependent(terminate_event, callback_event, config_file, name, team,
                                       index, agent_class_wrapper, agent_telemetry_queue, queue_holder)
        elif hasattr(agent_class_wrapper.get_loaded_class(), "get_output_flatbuffer"):
            bm = BotManagerFlatbuffer(terminate_event, callback_event, config_file, name, team,
                                      index, agent_class_wrapper, agent_telemetry_queue, queue_holder)
        else:
            bm = BotManagerStruct(terminate_event, callback_event, config_file, name, team,
                                  index, agent_class_wrapper, agent_telemetry_queue, queue_holder)
        bm.run()
