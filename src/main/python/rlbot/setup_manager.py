from contextlib import contextmanager
from datetime import datetime, timedelta
import msvcrt
import multiprocessing as mp
import os
import queue
import time
import webbrowser

import psutil
from rlbot import version
from rlbot.base_extension import BaseExtension
from rlbot.botmanager.bot_manager_flatbuffer import BotManagerFlatbuffer
from rlbot.botmanager.bot_manager_independent import BotManagerIndependent
from rlbot.botmanager.bot_manager_struct import BotManagerStruct
from rlbot.botmanager.helper_process_manager import HelperProcessManager
from rlbot.matchconfig.conversions import parse_match_config
from rlbot.matchconfig.match_config import MatchConfig
from rlbot.parsing.agent_config_parser import load_bot_appearance
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle
from rlbot.parsing.custom_config import ConfigObject
from rlbot.parsing.rlbot_config_parser import create_bot_config_layout
from rlbot.utils import process_configuration
from rlbot.utils.class_importer import import_class_with_base, import_agent
from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.utils.prediction import prediction_util
from rlbot.utils.structures.game_interface import GameInterface
from rlbot.utils.structures.quick_chats import QuickChatManager

# By default, look for rlbot.cfg in the current working directory.
DEFAULT_RLBOT_CONFIG_LOCATION = os.path.realpath('./rlbot.cfg')
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
ROCKET_LEAGUE_PROCESS_INFO = {'gameid': 252950, 'program_name': 'RocketLeague.exe', 'program': 'RocketLeague.exe'}

@contextmanager
def setup_manager_context():
    """
    Creates a initialized context manager which shuts down at the end of the
    `with` block.

    usage:
    >>> with setup_manager_context() as setup_manager:
    ...     setup_manager.load_config(...)
    ...     # ... Run match
    """
    setup_manager = SetupManager()
    setup_manager.connect_to_game()
    try:
        yield setup_manager
    finally:
        setup_manager.shut_down()

class SetupManager:
    """
    This class is responsible for pulling together all bits of the framework to
    set up a match between agents.

    A normal order of methods would be:
        connect_to_game()
        load_config()
        launch_ball_prediction()
        launch_quick_chat_manager()
        launch_bot_processes()
        start_match()
        infinite_loop()
        # the below two might be from another thread
        reload_all_agents()
        shut_down()
    """
    has_started = False
    num_participants = None
    names = None
    teams = None
    python_files = None
    parameters = None
    start_match_configuration = None
    agent_metadata_queue = None
    extension = None
    sub_processes = []

    def __init__(self):
        self.logger = get_logger(DEFAULT_LOGGER)
        self.game_interface = GameInterface(self.logger)
        self.quick_chat_manager = QuickChatManager(self.game_interface)
        self.quit_event = mp.Event()
        self.helper_process_manager = HelperProcessManager(self.quit_event)
        self.bot_quit_callbacks = []
        self.bot_reload_requests = []
        self.agent_metadata_map = {}
        self.ball_prediction_process = None
        self.match_config: MatchConfig = None

    def connect_to_game(self):
        if self.has_started:
            return
        version.print_current_release_notes()
        if not process_configuration.is_process_running(ROCKET_LEAGUE_PROCESS_INFO['program'],
                                                        ROCKET_LEAGUE_PROCESS_INFO['program_name']):
            try:
                self.logger.info("Launching Rocket League...")

                webbrowser.open(f"steam://rungameid/{ROCKET_LEAGUE_PROCESS_INFO['gameid']}")
            except webbrowser.Error:
                self.logger.info(
                    "Unable to launch Rocket League automatically. Please launch Rocket League manually to continue.")
        self.game_interface.inject_dll()
        self.game_interface.load_interface()
        self.agent_metadata_queue = mp.Queue()
        self.has_started = True

    def load_match_config(self, match_config: MatchConfig, bot_config_overrides={}):
        """
        Loads the match config into internal data structures, which prepares us to later
        launch bot processes and start the match.

        This is an alternative to the load_config method; they accomplish the same thing.
        """
        self.num_participants = match_config.num_players
        self.names = [bot.name for bot in match_config.player_configs]
        self.teams = [bot.team for bot in match_config.player_configs]

        bundles = [bot_config_overrides[index] if index in bot_config_overrides else
                   get_bot_config_bundle(bot.config_path) if bot.config_path else None
                   for index, bot in enumerate(match_config.player_configs)]

        self.python_files = [bundle.python_file if bundle else None
                             for bundle in bundles]

        self.parameters = []

        for index, bot in enumerate(match_config.player_configs):
            python_config = None
            if bot.rlbot_controlled:
                python_config = load_bot_parameters(bundles[index])
            self.parameters.append(python_config)
            if bot.loadout_config is None and bundles[index]:
                looks_config = bundles[index].get_looks_config()
                bot.loadout_config = load_bot_appearance(looks_config, bot.team)

        if match_config.extension_config is not None and match_config.extension_config.python_file_path is not None:
            self.load_extension(match_config.extension_config.python_file_path)

        self.match_config = match_config
        self.start_match_configuration = match_config.create_match_settings()
        self.game_interface.start_match_configuration = self.start_match_configuration

    def load_config(self, framework_config: ConfigObject = None, config_location=DEFAULT_RLBOT_CONFIG_LOCATION,
                    bot_configs=None,
                    looks_configs=None):
        """
        Loads the configuration into internal data structures, which prepares us to later
        launch bot processes and start the match.

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

        match_config = parse_match_config(framework_config, config_location, bot_configs, looks_configs)
        self.load_match_config(match_config, bot_configs)

    def launch_ball_prediction(self):
        # restart, in case we have changed game mode
        if self.ball_prediction_process:
            self.ball_prediction_process.terminate()

        if self.start_match_configuration.game_mode == 1:  # hoops
            prediction_util.copy_pitch_data_to_temp('hoops')
        elif self.start_match_configuration.game_mode == 2:  # dropshot
            prediction_util.copy_pitch_data_to_temp('dropshot')
        else:
            prediction_util.copy_pitch_data_to_temp('soccar')
        self.ball_prediction_process = prediction_util.launch()

    def launch_bot_processes(self):
        self.logger.debug("Launching bot processes")
        self.kill_sub_processes()

        # Launch processes
        for i in range(self.num_participants):
            if self.start_match_configuration.player_configuration[i].rlbot_controlled:
                queue_holder = self.quick_chat_manager.create_queue_for_bot(i, self.teams[i])
                reload_request = mp.Event()
                quit_callback = mp.Event()
                self.bot_reload_requests.append(reload_request)
                self.bot_quit_callbacks.append(quit_callback)
                process = mp.Process(target=SetupManager.run_agent,
                                     args=(self.quit_event, quit_callback, reload_request, self.parameters[i],
                                           str(self.start_match_configuration.player_configuration[i].name),
                                           self.teams[i], i, self.python_files[i], self.agent_metadata_queue,
                                           queue_holder, self.match_config))
                process.start()
                self.sub_processes.append(process)

        self.logger.debug("Successfully started bot processes")

    def launch_quick_chat_manager(self):
        self.quick_chat_manager.start_manager(self.quit_event)
        self.logger.debug("Successfully started quick chat manager")

    def start_match(self):
        self.game_interface.start_match()
        self.logger.info("Match has started")

    def infinite_loop(self):
        instructions = "Press 'r' to reload all agents, or 'q' to exit"
        self.logger.info(instructions)
        while not self.quit_event.is_set():
            # Handle commands
            if msvcrt.kbhit():
                command = msvcrt.getwch()
                if command.lower() == 'r':  # r: reload
                    self.reload_all_agents()
                elif command.lower() == 'q' or command == '\u001b':  # q or ESC: quit
                    self.shut_down()
                    break
                # Print instructions again if a alphabet character was pressed but no command was found
                elif command.isalpha():
                    self.logger.info(instructions)

            self.try_recieve_agent_metadata()

    def try_recieve_agent_metadata(self):
        """
        Checks whether any of the started bots have posted their AgentMetadata
        yet. If so, we put them on the agent_metadata_map such that we can
        kill their process later when we shut_down(kill_agent_process_ids=True)

        Returns how from how many bots we recieved metadata from.
        """
        num_recieved = 0
        while True:  # will exit on queue.Empty
            try:
                single_agent_metadata = self.agent_metadata_queue.get(timeout=0.1)
                num_recieved += 1
                self.helper_process_manager.start_or_update_helper_process(single_agent_metadata)
                self.agent_metadata_map[single_agent_metadata.index] = single_agent_metadata
                process_configuration.configure_processes(self.agent_metadata_map, self.logger)
            except queue.Empty:
                return num_recieved
            except Exception as ex:
                self.logger.error(ex)
                return num_recieved
        return num_recieved

    def reload_all_agents(self, quiet=False):
        if not quiet:
            self.logger.info("Reloading all agents...")
        for rr in self.bot_reload_requests:
            rr.set()

    def shut_down(self, time_limit=5, kill_all_pids=False):
        self.logger.info("Shutting Down")

        self.quit_event.set()
        end_time = datetime.now() + timedelta(seconds=time_limit)
        if self.ball_prediction_process:
            self.ball_prediction_process.terminate()

        # Wait for all processes to terminate before terminating main process
        terminated = False
        while not terminated:
            terminated = True
            for callback in self.bot_quit_callbacks:
                if not callback.is_set():
                    terminated = False
            time.sleep(0.1)
            if datetime.now() > end_time:
                self.logger.info("Taking too long to quit, trying harder...")
                self.kill_sub_processes()
                break

        if kill_all_pids:
            self.kill_agent_process_ids()

        # The quit event can only be set once. Let's reset to our initial state
        self.quit_event = mp.Event()
        self.helper_process_manager = HelperProcessManager(self.quit_event)

        self.logger.info("Shut down complete!")

    def load_extension(self, extension_filename):
        try:
            extension_class = import_class_with_base(extension_filename, BaseExtension).get_loaded_class()
            self.extension = extension_class(self)
            self.game_interface.set_extension(self.extension)
        except FileNotFoundError as e:
            print(f'Failed to load extension: {e}')

    @staticmethod
    def run_agent(terminate_event, callback_event, reload_request, config_file, name, team, index, python_file,
                  agent_telemetry_queue, queue_holder, match_config: MatchConfig):

        agent_class_wrapper = import_agent(python_file)

        if hasattr(agent_class_wrapper.get_loaded_class(), "run_independently"):
            bm = BotManagerIndependent(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                       agent_class_wrapper, agent_telemetry_queue, queue_holder, match_config)
        elif hasattr(agent_class_wrapper.get_loaded_class(), "get_output_flatbuffer"):
            bm = BotManagerFlatbuffer(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                      agent_class_wrapper, agent_telemetry_queue, queue_holder, match_config)
        else:
            bm = BotManagerStruct(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                  agent_class_wrapper, agent_telemetry_queue, queue_holder, match_config)
        bm.run()

    def kill_sub_processes(self):
        for process in self.sub_processes:
            process.terminate()
        self.sub_processes = []

    def kill_agent_process_ids(self):
        pids = process_configuration.extract_all_pids(self.agent_metadata_map)
        for pid in pids:
            try:
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                    self.logger.info(f"Killing {child.pid} (child of {pid})")
                    try:
                        child.kill()
                    except psutil._exceptions.NoSuchProcess:
                        self.logger.info("Already dead.")
                self.logger.info(f"Killing {pid}")
                try:
                    parent.kill()
                except psutil._exceptions.NoSuchProcess:
                    self.logger.info("Already dead.")
            except psutil.NoSuchProcess:
                self.logger.info("Can't fetch parent process, already dead.")


def load_bot_parameters(config_bundle) -> ConfigObject:
    """
    Initializes the agent in the bundle's python file and asks it to provide its
    custom configuration object where its parameters can be set.
    :return: the parameters as a ConfigObject
    """
    # Python file relative to the config location.
    python_file = config_bundle.python_file
    agent_class_wrapper = import_agent(python_file)
    bot_parameters = agent_class_wrapper.get_loaded_class().base_create_agent_configurations()
    bot_parameters.parse_file(config_bundle.config_obj, config_directory=config_bundle.config_directory)
    return bot_parameters
