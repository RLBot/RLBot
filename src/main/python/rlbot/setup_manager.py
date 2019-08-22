import msvcrt
import multiprocessing as mp
import os
import psutil
import queue
import subprocess
import time
import webbrowser
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from urllib.parse import ParseResult as URL

import psutil
from rlbot import gateway_util
from rlbot import version
from rlbot.base_extension import BaseExtension
from rlbot.botmanager.bot_manager_flatbuffer import BotManagerFlatbuffer
from rlbot.botmanager.bot_manager_independent import BotManagerIndependent
from rlbot.botmanager.bot_manager_struct import BotManagerStruct
from rlbot.botmanager.helper_process_manager import HelperProcessManager
from rlbot.matchconfig.conversions import parse_match_config
from rlbot.matchconfig.match_config import MatchConfig
from rlbot.matchcomms.server import launch_matchcomms_server
from rlbot.parsing.agent_config_parser import load_bot_appearance
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle, BotConfigBundle
from rlbot.parsing.custom_config import ConfigObject
from rlbot.parsing.rlbot_config_parser import create_bot_config_layout
from rlbot.utils import process_configuration
from rlbot.utils.class_importer import import_class_with_base, import_agent
from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.utils.process_configuration import WrongProcessArgs
from rlbot.utils.structures.start_match_structures import MAX_PLAYERS
from rlbot.utils.structures.game_interface import GameInterface

# By default, look for rlbot.cfg in the current working directory.
DEFAULT_RLBOT_CONFIG_LOCATION = os.path.realpath('./rlbot.cfg')
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'
class ROCKET_LEAGUE_PROCESS_INFO:
    GAMEID = 252950
    PROGRAM_NAME = 'RocketLeague.exe'
    PROGRAM = 'RocketLeague.exe'
    REQUIRED_ARGS = {'-rlbot'}
    IDEAL_ARGS = ['-rlbot', '-nomovie']

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
    except Exception as e:
        get_logger(DEFAULT_LOGGER).error(e)
        raise e
    finally:
        setup_manager.shut_down(kill_all_pids=True)

class SetupManager:
    """
    This class is responsible for pulling together all bits of the framework to
    set up a match between agents.

    A normal order of methods would be:
        connect_to_game()
        load_config()
        launch_ball_prediction()
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
    bot_bundles: List[BotConfigBundle] = None
    start_match_configuration = None
    agent_metadata_queue = None
    extension = None
    bot_processes: List[mp.Process] = []


    def __init__(self):
        self.logger = get_logger(DEFAULT_LOGGER)
        self.game_interface = GameInterface(self.logger)
        self.quit_event = mp.Event()
        self.helper_process_manager = HelperProcessManager(self.quit_event)
        self.bot_quit_callbacks = []
        self.bot_reload_requests = []
        self.agent_metadata_map = {}
        self.match_config: MatchConfig = None
        self.rlbot_gateway_process = None
        self.matchcomms_server: MatchcommsServerThread = None

    def connect_to_game(self):
        """
        Ensures the game is running and connects to it by initializing self.game_interface.
        """

        version.print_current_release_notes()
        self.ensure_rlbot_gateway_started()
        if self.has_started:
            return

        try:
            is_rocket_league_running = process_configuration.is_process_running(
                ROCKET_LEAGUE_PROCESS_INFO.PROGRAM,
                ROCKET_LEAGUE_PROCESS_INFO.PROGRAM_NAME,
                ROCKET_LEAGUE_PROCESS_INFO.REQUIRED_ARGS)
        except WrongProcessArgs:
            raise Exception(f"Rocket League is not running with {ROCKET_LEAGUE_PROCESS_INFO.REQUIRED_ARGS}! "
                            f"Please close Rocket League and let us start it for you instead!")
        if not is_rocket_league_running:
            self.launch_rocket_league()

        try:
            self.game_interface.load_interface()
        except Exception as e:
            self.logger.error("Terminating rlbot gateway and raising:")
            self.rlbot_gateway_process.terminate()
            raise e
        self.agent_metadata_queue = mp.Queue()
        self.has_started = True

    def launch_rocket_league(self):
        """
        Launches Rocket League but does not connect to it.
        """
        self.logger.info('Launching Rocket League...')

        # Try launch via Steam.
        steam_exe_path = try_get_steam_executable_path()
        if steam_exe_path:  # Note: This Python 3.8 feature would be useful here https://www.python.org/dev/peps/pep-0572/#abstract
            exe_and_args = [
                str(steam_exe_path),
                '-applaunch',
                str(ROCKET_LEAGUE_PROCESS_INFO.GAMEID),
            ] + ROCKET_LEAGUE_PROCESS_INFO.IDEAL_ARGS
            _ = subprocess.Popen(exe_and_args)  # This is deliberately an orphan process.
            return

        # TODO: Figure out launching via Epic games

        self.logger.warning('Using fall-back launch method.')
        self.logger.info("You should see a confirmation pop-up, if you don't see it then click on Steam! "
                         'https://gfycat.com/AngryQuickFinnishspitz')
        args_string = '%20'.join(ROCKET_LEAGUE_PROCESS_INFO.IDEAL_ARGS)
        try:
            webbrowser.open(f'steam://rungameid/{ROCKET_LEAGUE_PROCESS_INFO.GAMEID}//{args_string}')
        except webbrowser.Error:
            self.logger.warning(
                'Unable to launch Rocket League. Please launch Rocket League manually using the -rlbot option to continue.')

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

        self.bot_bundles = []

        for index, bot in enumerate(match_config.player_configs):
            self.bot_bundles.append(bundles[index])
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
            framework_config.parse_file(config_location, max_index=MAX_PLAYERS)
        if bot_configs is None:
            bot_configs = {}
        if looks_configs is None:
            looks_configs = {}

        match_config = parse_match_config(framework_config, config_location, bot_configs, looks_configs)
        self.load_match_config(match_config, bot_configs)

    def ensure_rlbot_gateway_started(self):

        for proc in psutil.process_iter():
            try:
                if proc.name() == "RLBot.exe":
                    self.rlbot_gateway_process = proc
                    self.logger.info("Already have RLBot.exe running!")
                    return
            except Exception as e:
                self.logger.error(f"Failed to read the name of a process while hunting for RLBot.exe: {e}")

        if self.rlbot_gateway_process is None or not psutil.pid_exists(self.rlbot_gateway_process.pid):
            self.rlbot_gateway_process = gateway_util.launch()
            self.logger.info(f"Python started RLBot.exe with process id {self.rlbot_gateway_process.pid}")

    def launch_ball_prediction(self):
        # This does nothing now. It's kept here temporarily so that RLBotGUI doesn't break.
        pass

    def launch_bot_processes(self):
        self.logger.debug("Launching bot processes")
        self.kill_bot_processes()

        # Start matchcomms here as it's only required for the bots.
        self.kill_matchcomms_server()
        self.matchcomms_server = launch_matchcomms_server()

        # Launch processes
        for i in range(self.num_participants):
            if self.start_match_configuration.player_configuration[i].rlbot_controlled:
                reload_request = mp.Event()
                quit_callback = mp.Event()
                self.bot_reload_requests.append(reload_request)
                self.bot_quit_callbacks.append(quit_callback)
                process = mp.Process(target=SetupManager.run_agent,
                                     args=(self.quit_event, quit_callback, reload_request, self.bot_bundles[i],
                                           str(self.start_match_configuration.player_configuration[i].name),
                                           self.teams[i], i, self.python_files[i], self.agent_metadata_queue,
                                           self.match_config, self.matchcomms_server.root_url))
                process.start()
                self.bot_processes.append(process)

        self.logger.debug("Successfully started bot processes")

    def launch_quick_chat_manager(self):
        # Quick chat manager is gone since we're using RLBot.exe now.
        # Keeping this function around for backwards compatibility.
        pass

    def start_match(self):
        self.logger.info("Python attempting to start match.")
        self.game_interface.start_match()
        time.sleep(2)  # Wait a moment. If we look too soon, we might see a valid packet from previous game.
        self.game_interface.wait_until_valid_packet()
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

        Returns how from how many bots we received metadata from.
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

    def reload_all_agents(self, quiet=False):
        if not quiet:
            self.logger.info("Reloading all agents...")
        for rr in self.bot_reload_requests:
            rr.set()

    def shut_down(self, time_limit=5, kill_all_pids=False, quiet=False):
        if not quiet:
            self.logger.info("Shutting Down")

        self.quit_event.set()
        end_time = datetime.now() + timedelta(seconds=time_limit)

        # Don't kill RLBot.exe. It needs to keep running because if we're in a GUI
        # that will persist after this shut down, the interface dll in charge of starting
        # matches is already locked in to its shared memory files, and if we start a new
        # RLBot.exe, those files will go stale. https://github.com/skyborgff/RLBot/issues/9

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
                self.kill_bot_processes()
                break

        if kill_all_pids:
            self.kill_agent_process_ids()

        self.kill_matchcomms_server()

        # The quit event can only be set once. Let's reset to our initial state
        self.quit_event = mp.Event()
        self.helper_process_manager = HelperProcessManager(self.quit_event)

        if not quiet:
            self.logger.info("Shut down complete!")

    def load_extension(self, extension_filename):
        try:
            extension_class = import_class_with_base(extension_filename, BaseExtension).get_loaded_class()
            self.extension = extension_class(self)
            self.game_interface.set_extension(self.extension)
        except FileNotFoundError as e:
            print(f'Failed to load extension: {e}')

    @staticmethod
    def run_agent(terminate_event, callback_event, reload_request, bundle: BotConfigBundle, name, team, index, python_file,
                  agent_telemetry_queue, match_config: MatchConfig, matchcomms_root: URL):

        agent_class_wrapper = import_agent(python_file)
        config_file = agent_class_wrapper.get_loaded_class().base_create_agent_configurations()
        config_file.parse_file(bundle.config_obj, config_directory=bundle.config_directory)

        if hasattr(agent_class_wrapper.get_loaded_class(), "run_independently"):
            bm = BotManagerIndependent(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                       agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root)
        elif hasattr(agent_class_wrapper.get_loaded_class(), "get_output_flatbuffer"):
            bm = BotManagerFlatbuffer(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                      agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root)
        else:
            bm = BotManagerStruct(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                  agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root)
        bm.run()

    def kill_bot_processes(self):
        for process in self.bot_processes:
            process.terminate()
        for process in self.bot_processes:
            process.join(timeout=1)
        self.bot_processes = []

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
            except psutil.AccessDenied as ex:
                self.logger.error(f"Access denied when trying to kill a bot pid! {ex}")
            except Exception as ex:
                self.logger.error(f"Unexpected exception when trying to kill a bot pid! {ex}")

    def kill_matchcomms_server(self):
        if self.matchcomms_server:
            self.matchcomms_server.close()
            self.matchcomms_server = None


def try_get_steam_executable_path() -> Optional[Path]:
    """
    Tries to find the path of the Steam executable.
    Has platform specific code.
    """

    try:
        from winreg import OpenKey, HKEY_CURRENT_USER, ConnectRegistry, QueryValueEx, REG_SZ
    except ImportError as e:
        return None  # TODO: Linux support.

    try:
        key = OpenKey(ConnectRegistry(None, HKEY_CURRENT_USER), r'Software\Valve\Steam')
        val, val_type = QueryValueEx(key, 'SteamExe')
    except FileNotFoundError:
        return None
    if val_type != REG_SZ:
        return None
    return Path(val)
