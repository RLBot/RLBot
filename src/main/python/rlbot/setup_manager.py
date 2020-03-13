import multiprocessing as mp
import os
import psutil
import platform
import queue
import subprocess
import time
import webbrowser
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict
from urllib.parse import ParseResult as URL

from rlbot.utils.structures import game_data_struct

from rlbot import gateway_util
from rlbot import version
from rlbot.base_extension import BaseExtension
from rlbot.botmanager.bot_manager_flatbuffer import BotManagerFlatbuffer
from rlbot.botmanager.bot_manager_independent import BotManagerIndependent
from rlbot.botmanager.bot_manager_struct import BotManagerStruct
from rlbot.botmanager.helper_process_manager import HelperProcessManager
from rlbot.gateway_util import LaunchOptions, NetworkingRole
from rlbot.matchconfig.conversions import parse_match_config
from rlbot.matchconfig.match_config import MatchConfig
from rlbot.matchconfig.psyonix_config import set_random_psyonix_bot_preset
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
from rlbot.utils.config_parser import mergeTASystemSettings, cleanUpTASystemSettings
from rlbot.matchcomms.server import MatchcommsServerThread

if platform.system() == 'Windows':
    import msvcrt

# By default, look for rlbot.cfg in the current working directory.
DEFAULT_RLBOT_CONFIG_LOCATION = os.path.realpath('./rlbot.cfg')
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'


class ROCKET_LEAGUE_PROCESS_INFO:
    GAMEID = 252950
    PROGRAM_NAME = 'RocketLeague.exe'
    PROGRAM = 'RocketLeague.exe'
    REQUIRED_ARGS = {r'-rlbot', r'RLBot_ControllerURL=127.0.0.1:[0-9]+'}
    PORT_PLACEHOLDER = '%PORT%'
    IDEAL_ARGS = ['-rlbot', f'RLBot_ControllerURL=127.0.0.1:{PORT_PLACEHOLDER}', '-nomovie']

    @staticmethod
    def get_ideal_args(port):
        return [arg.replace(ROCKET_LEAGUE_PROCESS_INFO.PORT_PLACEHOLDER, str(port))
                for arg in ROCKET_LEAGUE_PROCESS_INFO.IDEAL_ARGS]


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
    bot_processes: Dict[int, mp.Process] = {}

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
        self.early_start_seconds = 0
        self.num_metadata_received = 0

    def is_rocket_league_running(self, port) -> bool:
        """
        Returns whether Rocket League is running with the right port.
        """

        try:
            is_rocket_league_running, proc = process_configuration.is_process_running(
                ROCKET_LEAGUE_PROCESS_INFO.PROGRAM,
                ROCKET_LEAGUE_PROCESS_INFO.PROGRAM_NAME,
                ROCKET_LEAGUE_PROCESS_INFO.REQUIRED_ARGS)

            if proc is not None:
                # Check for correct port.
                rocket_league_port = self._read_port_from_rocket_league_args(proc.cmdline())
                if rocket_league_port is not None and rocket_league_port != port:
                    raise Exception(f"Rocket League is already running with port {rocket_league_port} but we wanted "
                                    f"{port}! Please close Rocket League and let us start it for you instead!")
        except WrongProcessArgs:
            raise Exception(f"Rocket League is not running with {ROCKET_LEAGUE_PROCESS_INFO.REQUIRED_ARGS}!\n"
                            "Please close Rocket League and let us start it for you instead!")

        return is_rocket_league_running

    def connect_to_game(self):
        """
        Connects to the game by initializing self.game_interface.
        """
        version.print_current_release_notes()
        port = self.ensure_rlbot_gateway_started()

        # Prevent loading game interface twice.
        if self.has_started:
            if not self.is_rocket_league_running(port):
                raise Exception("Rocket League is not running even though we started it once.\n"
                                "Please restart RLBot.")
            return

        # Currently match_config is None when launching from RLBotGUI.
        if self.match_config is not None and self.match_config.networking_role == 'remote_rlbot_client':
            self.logger.info("Will not start Rocket League because this is configured as a client!")
        # Launch the game if it is not running.
        elif not self.is_rocket_league_running(port):
            mergeTASystemSettings()
            self.launch_rocket_league(port=port)

        try:
            self.game_interface.load_interface()
        except Exception as e:
            self.logger.error("Terminating rlbot gateway and raising:")
            self.rlbot_gateway_process.terminate()
            raise e
        self.agent_metadata_queue = mp.Queue()
        self.has_started = True

    @staticmethod
    def _read_port_from_rocket_league_args(args):
        for arg in args:
            # The arg will look like RLBot_ControllerURL="127.0.0.1:23233"
            if 'RLBot_ControllerURL' in arg:
                rocket_league_port = int(arg.split(':')[1].replace('"', ''))
                return int(rocket_league_port)
        return None

    def launch_rocket_league(self, port):
        """
        Launches Rocket League but does not connect to it.
        """
        ideal_args = ROCKET_LEAGUE_PROCESS_INFO.get_ideal_args(port)
        self.logger.info(f'Launching Rocket League with args: {ideal_args}')

        # Try launch via Steam.
        steam_exe_path = try_get_steam_executable_path()
        if steam_exe_path:  # Note: This Python 3.8 feature would be useful here https://www.python.org/dev/peps/pep-0572/#abstract
            exe_and_args = [
                str(steam_exe_path),
                '-applaunch',
                str(ROCKET_LEAGUE_PROCESS_INFO.GAMEID),
            ] + ideal_args
            _ = subprocess.Popen(exe_and_args)  # This is deliberately an orphan process.
            return

        # TODO: Figure out launching via Epic games

        self.logger.warning('Using fall-back launch method.')
        self.logger.info("You should see a confirmation pop-up, if you don't see it then click on Steam! "
                         'https://gfycat.com/AngryQuickFinnishspitz')
        args_string = '%20'.join(ideal_args)

        # Try launch via terminal (Linux)
        if platform.system() == 'Linux':
            linux_args = [
                'steam',
                f'steam://rungameid/{ROCKET_LEAGUE_PROCESS_INFO.GAMEID}//{args_string}'
            ]

            try:
                _ = subprocess.Popen(linux_args)

            except OSError:
                self.logger.warning(
                    'Could not find Steam executable, using browser to open instead.')
            else:
                return

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

        for player in match_config.player_configs:
            if player.bot and not player.rlbot_controlled:
                set_random_psyonix_bot_preset(player)

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

    def ensure_rlbot_gateway_started(self) -> int:
        """
        Ensures that RLBot.exe is running. Returns the port that it will be listening on for connections from
        Rocket League. Rocket League should be passed a command line argument so that it starts with this same port.
        :return:
        """

        # TODO: Uncomment this when done with local testing of Remote RLBot.
        self.rlbot_gateway_process, port = gateway_util.find_existing_process()
        if self.rlbot_gateway_process is not None:
            self.logger.info(f"Already have RLBot.exe running! Port is {port}")
            return port

        launch_options = LaunchOptions()
        if self.match_config is not None:  # Currently this is None when launching from RLBotGUI.
            networking_role = NetworkingRole[self.match_config.networking_role]
            launch_options = LaunchOptions(
                networking_role=networking_role,
                remote_address=self.match_config.network_address)

        self.rlbot_gateway_process, port = gateway_util.launch(launch_options)
        self.logger.info(f"Python started RLBot.exe with process id {self.rlbot_gateway_process.pid} "
                         f"and port {port}")
        return port

    def launch_ball_prediction(self):
        # This does nothing now. It's kept here temporarily so that RLBotGUI doesn't break.
        pass

    def has_received_metadata_from_all_bots(self):
        expected_metadata_calls = sum(1 for player in self.match_config.player_configs if player.rlbot_controlled)
        return self.num_metadata_received >= expected_metadata_calls

    def launch_early_start_bot_processes(self):
        """
        Some bots can start up before the game is ready and not be bothered by missing
        or strange looking values in the game tick packet, etc. Such bots can opt in to the
        early start category and enjoy extra time to load up before the match starts.
        """

        if self.match_config.networking_role == NetworkingRole.remote_rlbot_client:
            return  # The bot indices are liable to change, so don't start anything yet.

        self.logger.debug("Launching early-start bot processes")
        num_started = self.launch_bot_process_helper(early_starters_only=True)
        self.try_recieve_agent_metadata()
        if num_started > 0 and self.early_start_seconds > 0:
            self.logger.info(f"Waiting for {self.early_start_seconds} seconds to let early-start bots load.")
            end_time = datetime.now() + timedelta(seconds=self.early_start_seconds)
            while datetime.now() < end_time:
                self.try_recieve_agent_metadata()
                time.sleep(0.1)

    def launch_bot_processes(self):
        self.logger.debug("Launching bot processes")
        self.launch_bot_process_helper(early_starters_only=False)

    def launch_bot_process_helper(self, early_starters_only=False):
        # Start matchcomms here as it's only required for the bots.
        self.kill_matchcomms_server()
        self.matchcomms_server = launch_matchcomms_server()

        num_started = 0

        # Launch processes
        # TODO: this might be the right moment to fix the player indices based on a game tick packet.
        packet = game_data_struct.GameTickPacket()
        self.game_interface.update_live_data_packet(packet)

        # TODO: root through the packet and find discrepancies in the player index mapping.
        for i in range(self.num_participants):
            if not self.start_match_configuration.player_configuration[i].rlbot_controlled:
                continue
            if early_starters_only and not self.bot_bundles[i].supports_early_start:
                continue

            bot_manager_spawn_id = None

            if early_starters_only:
                # Don't use a spawn id stuff for the early start system. The bots will be starting up before
                # the car spawns, and we don't want the bot manager to panic.
                participant_index = i
            else:
                participant_index = None
                spawn_id = self.game_interface.start_match_configuration.player_configuration[i].spawn_id
                self.logger.info(f'Player in slot {i} was sent with spawn id {spawn_id}, will search in the packet.')
                for n in range(0, packet.num_cars):
                    packet_spawn_id = packet.game_cars[n].spawn_id
                    if spawn_id == packet_spawn_id:
                        self.logger.info(f'Looks good, considering participant index to be {n}')
                        participant_index = n
                        bot_manager_spawn_id = spawn_id
                if participant_index is None:
                    raise Exception("Unable to determine the bot index!")

            if participant_index not in self.bot_processes:
                reload_request = mp.Event()
                quit_callback = mp.Event()
                self.bot_reload_requests.append(reload_request)
                self.bot_quit_callbacks.append(quit_callback)
                process = mp.Process(target=SetupManager.run_agent,
                                     args=(self.quit_event, quit_callback, reload_request, self.bot_bundles[i],
                                           str(self.start_match_configuration.player_configuration[i].name),
                                           self.teams[i], participant_index, self.python_files[i], self.agent_metadata_queue,
                                           self.match_config, self.matchcomms_server.root_url, bot_manager_spawn_id))
                process.start()
                self.bot_processes[i] = process
                num_started += 1

        self.logger.debug(f"Successfully started {num_started} bot processes")
        return num_started

    def launch_quick_chat_manager(self):
        # Quick chat manager is gone since we're using RLBot.exe now.
        # Keeping this function around for backwards compatibility.
        pass

    def start_match(self):

        if self.match_config.networking_role == NetworkingRole.remote_rlbot_client:
            match_settings = self.game_interface.get_match_settings()
            # TODO: merge the match settings into self.match_config
            # And then make sure we still only start the appropriate bot processes
            # that we originally asked for.

        self.logger.info("Python attempting to start match.")
        self.game_interface.start_match()
        time.sleep(2)  # Wait a moment. If we look too soon, we might see a valid packet from previous game.
        self.game_interface.wait_until_valid_packet()
        self.logger.info("Match has started")

        cleanUpTASystemSettings()

    def infinite_loop(self):
        instructions = "Press 'r' to reload all agents, or 'q' to exit"
        self.logger.info(instructions)
        while not self.quit_event.is_set():
            # Handle commands
            # TODO windows only library
            if platform.system() == 'Windows':
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
                self.num_metadata_received += num_recieved
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
                break

        self.kill_bot_processes()

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
    def run_agent(terminate_event, callback_event, reload_request, bundle: BotConfigBundle, name, team, index,
                  python_file, agent_telemetry_queue, match_config: MatchConfig, matchcomms_root: URL, spawn_id: str):

        agent_class_wrapper = import_agent(python_file)
        config_file = agent_class_wrapper.get_loaded_class().base_create_agent_configurations()
        config_file.parse_file(bundle.config_obj, config_directory=bundle.config_directory)

        if hasattr(agent_class_wrapper.get_loaded_class(), "run_independently"):
            bm = BotManagerIndependent(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                       agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root,
                                       spawn_id)
        elif hasattr(agent_class_wrapper.get_loaded_class(), "get_output_flatbuffer"):
            bm = BotManagerFlatbuffer(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                      agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root,
                                      spawn_id)
        else:
            bm = BotManagerStruct(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                  agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root, spawn_id)
        bm.run()

    def kill_bot_processes(self):
        for process in self.bot_processes.values():
            process.terminate()
        for process in self.bot_processes.values():
            process.join(timeout=1)
        self.bot_processes.clear()
        self.num_metadata_received = 0

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
