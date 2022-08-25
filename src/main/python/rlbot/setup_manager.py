import signal

import multiprocessing as mp
import os
import sys
import json
from dataclasses import dataclass

import psutil
import platform
import queue
import subprocess
import time
import webbrowser
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Set
from urllib.parse import ParseResult as URL
from urllib.request import urlopen
from urllib.error import URLError

from dataclasses import dataclass

from rlbot.gamelaunch.epic_launch import launch_with_epic_login_trick, launch_with_epic_simple
from rlbot.socket.socket_data_reporter import get_one_packet
from rlbot.utils.structures import game_data_struct

from rlbot import gateway_util
from rlbot import version
from rlbot.base_extension import BaseExtension
from rlbot.botmanager.bot_manager_independent import BotManagerIndependent
from rlbot.botmanager.bot_manager_struct import BotManagerStruct
from rlbot.botmanager.helper_process_manager import HelperProcessManager
from rlbot.botmanager.agent_metadata import AgentMetadata
from rlbot.gateway_util import LaunchOptions, NetworkingRole
from rlbot.matchconfig.conversions import parse_match_config
from rlbot.matchconfig.match_config import MatchConfig, PlayerConfig
from rlbot.matchconfig.psyonix_config import set_random_psyonix_bot_preset
from rlbot.matchcomms.server import launch_matchcomms_server
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle, BotConfigBundle, get_script_config_bundle
from rlbot.parsing.custom_config import ConfigObject
from rlbot.parsing.rlbot_config_parser import create_bot_config_layout
from rlbot.utils import process_configuration
from rlbot.utils.class_importer import import_class_with_base, import_agent
from rlbot.utils.logging_utils import get_logger, DEFAULT_LOGGER
from rlbot.utils.process_configuration import WrongProcessArgs
from rlbot.utils.structures.start_match_structures import MAX_PLAYERS
from rlbot.utils.structures.game_interface import GameInterface, USE_OLD_LAUNCH
from rlbot.utils.config_parser import mergeTASystemSettings, cleanUpTASystemSettings
from rlbot.parsing.rlbot_config_parser import LAUNCHER_PREFERENCE_KEY
from rlbot.matchcomms.server import MatchcommsServerThread
from rlbot.utils.virtual_environment_management import EnvBuilderWithRequirements

if platform.system() == 'Windows':
    import msvcrt

# By default, look for rlbot.cfg in the current working directory.
DEFAULT_RLBOT_CONFIG_LOCATION = os.path.realpath('./rlbot.cfg')
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'


class ROCKET_LEAGUE_PROCESS_INFO:
    GAMEID = 252950
    PROGRAM_NAME = 'RocketLeague.exe' if platform.system() == 'Windows' else 'RocketLeague'
    PROGRAM = 'RocketLeague.exe' if platform.system() == 'Windows' else 'RocketLeague'
    REQUIRED_ARGS = {r'-rlbot', r'RLBot_ControllerURL=127.0.0.1:[0-9]+'}

    @staticmethod
    def get_ideal_args(port):
        # We are specifying RLBot_PacketSendRate=240, which will override people's TARLBot.ini settings.
        # We believe there is no downside to 240. See https://github.com/RLBot/RLBot/wiki/Tick-Rate
        return ['-rlbot', f'RLBot_ControllerURL=127.0.0.1:{port}', 'RLBot_PacketSendRate=240', '-nomovie']

@dataclass
class RocketLeagueLauncherPreference:
    STEAM = 'steam'
    EPIC = 'epic' # This tries epic first, then falls back to steam. Weird name is for backwards compat.
    EPIC_ONLY = 'epic_only'
    preferred_launcher: str
    use_login_tricks: bool
    rocket_league_exe_path: Optional[Path] = None


# By default, we will attempt Epic with login tricks, then fall back to Steam.
DEFAULT_LAUNCHER_PREFERENCE = RocketLeagueLauncherPreference(RocketLeagueLauncherPreference.EPIC, True)


@contextmanager
def setup_manager_context(launcher_preference: RocketLeagueLauncherPreference = None):
    """
    Creates a initialized context manager which shuts down at the end of the
    `with` block.

    usage:
    >>> with setup_manager_context() as setup_manager:
    ...     setup_manager.load_config(...)
    ...     # ... Run match
    """
    setup_manager = SetupManager()
    setup_manager.connect_to_game(launcher_preference)
    try:
        yield setup_manager
    except Exception as e:
        get_logger(DEFAULT_LOGGER).error(e)
        raise e
    finally:
        setup_manager.shut_down(kill_all_pids=True)


@dataclass
class BotProcessInfo:
    process: mp.Process
    subprocess: subprocess.Popen
    player_config: PlayerConfig

    def is_alive(self):
        if self.process is not None:
            return self.process.is_alive()
        return self.subprocess.poll() is None


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
    match_config: MatchConfig = None
    extension = None

    def __init__(self):
        self.logger = get_logger(DEFAULT_LOGGER)
        self.game_interface = GameInterface(self.logger)
        self.quit_event = mp.Event()
        self.helper_process_manager = HelperProcessManager(self.quit_event)
        self.bot_quit_callbacks = []
        self.bot_reload_requests = []
        self.agent_metadata_map: Dict[int, AgentMetadata] = {}
        self.match_config: MatchConfig = None
        self.launcher_preference = None
        self.rlbot_gateway_process = None
        self.matchcomms_server: MatchcommsServerThread = None
        self.early_start_seconds = 0
        self.num_metadata_received = 0
        self.agent_metadata_queue = mp.Queue()
        self.bot_processes: Dict[int, BotProcessInfo] = {}
        self.script_processes: Dict[int, subprocess.Popen] = {}

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

    def connect_to_game(self, launcher_preference: RocketLeagueLauncherPreference = None):
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
            pref = launcher_preference or self.launcher_preference or DEFAULT_LAUNCHER_PREFERENCE
            if not self.launch_rocket_league(port=port, launcher_preference=pref):
                raise Exception("Failed to launch Rocket League!")

        try:
            self.logger.info("Loading interface...")
            # We're not going to use this game_interface for much, just sending start match messages and inspecting
            # the packet to see if the appropriate cars have been spawned.
            self.game_interface.load_interface(
                port=23234, wants_ball_predictions=False, wants_quick_chat=False, wants_game_messages=False)
        except Exception as e:
            self.logger.error("Terminating rlbot gateway and raising:")
            self.rlbot_gateway_process.terminate()
            raise e
        self.has_started = True

    @staticmethod
    def _read_port_from_rocket_league_args(args):
        for arg in args:
            # The arg will look like RLBot_ControllerURL="127.0.0.1:23233"
            if 'RLBot_ControllerURL' in arg:
                rocket_league_port = int(arg.split(':')[1].replace('"', ''))
                return int(rocket_league_port)
        return None

    def launch_rocket_league(self, port, launcher_preference: RocketLeagueLauncherPreference = DEFAULT_LAUNCHER_PREFERENCE) -> bool:
        if launcher_preference.preferred_launcher == RocketLeagueLauncherPreference.EPIC_ONLY:
            return self.launch_rocket_league_with_epic(port,  launcher_preference)
        elif launcher_preference.preferred_launcher == RocketLeagueLauncherPreference.STEAM:
            return self.launch_rocket_league_with_steam(port)
        elif launcher_preference.preferred_launcher == RocketLeagueLauncherPreference.EPIC:
            # Historically, the preference of EPIC has caused RLBot to try Epic first, then Steam.
            # Keeping that behavior for backwards compatibility.
            epic_worked = self.launch_rocket_league_with_epic(port, launcher_preference)
            if epic_worked:
                return True
            self.logger.info("Epic launch has failed, falling back to Steam!")
            return self.launch_rocket_league_with_steam(port)
    
    def launch_rocket_league_with_epic(self, port, launcher_preference: RocketLeagueLauncherPreference) -> bool:
        """
        Launches Rocket League but does not connect to it.
        """
        ideal_args = ROCKET_LEAGUE_PROCESS_INFO.get_ideal_args(port)

        if launcher_preference.use_login_tricks:
            if launch_with_epic_login_trick(ideal_args, launcher_preference):
                return True
            else:
                self.logger.info("Epic login trick seems to have failed!")
        if launch_with_epic_simple(ideal_args, launcher_preference):
            return True

    def launch_rocket_league_with_steam(self, port) -> bool:
        # Try launch via Steam.
        ideal_args = ROCKET_LEAGUE_PROCESS_INFO.get_ideal_args(port)

        steam_exe_path = try_get_steam_executable_path()
        if steam_exe_path:  # Note: This Python 3.8 feature would be useful here https://www.python.org/dev/peps/pep-0572/#abstract
            exe_and_args = [
                str(steam_exe_path),
                '-applaunch',
                str(ROCKET_LEAGUE_PROCESS_INFO.GAMEID),
            ] + ideal_args
            self.logger.info(f'Launching Rocket League with: {exe_and_args}')
            _ = subprocess.Popen(exe_and_args)  # This is deliberately an orphan process.
            return True

        self.logger.warning(f'Launching Rocket League using Steam-only fall-back launch method with args: {ideal_args}')
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
                return True
            except OSError:
                self.logger.warning('Could not launch Steam executable on Linux.')

        try:
            self.logger.info("Launching rocket league via steam browser URL as a last resort...")
            webbrowser.open(f'steam://rungameid/{ROCKET_LEAGUE_PROCESS_INFO.GAMEID}//{args_string}')
        except webbrowser.Error:
            self.logger.warning(
                'Unable to launch Rocket League. Please launch Rocket League manually using the -rlbot option to continue.')
            return False
        return True

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
            if player.bot and not player.rlbot_controlled and not player.loadout_config:
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
                bot.loadout_config = bundles[index].generate_loadout_config(index, bot.team)

        if match_config.extension_config is not None and match_config.extension_config.python_file_path is not None:
            self.load_extension(match_config.extension_config.python_file_path)

        try:
            urlopen("http://google.com")
            checked_environment_requirements = set()
            online = True
        except URLError:
            print("The user is offline, skipping upgrade the bot requirements")
            online = False

        for bundle in self.bot_bundles:
            if bundle is not None and bundle.use_virtual_environment:
                do_post_setup = online

                if do_post_setup:
                    if bundle.requirements_file in checked_environment_requirements:
                        do_post_setup = False
                    else:
                        checked_environment_requirements.add(bundle.requirements_file)

                builder = EnvBuilderWithRequirements(bundle=bundle, do_post_setup=do_post_setup)
                path = Path(bundle.config_directory) / 'venv'
                if not path.exists():
                    builder.create(path)
                else:
                    env_dir = os.path.abspath(path)
                    context = builder.ensure_directories(env_dir)
                    if not builder.upgrade:
                        builder.post_setup(context)

        for script_config in match_config.script_configs:
            script_config_bundle = get_script_config_bundle(script_config.config_path)
            if script_config_bundle.use_virtual_environment:
                do_post_setup = online

                if do_post_setup:
                    if bundle.requirements_file in checked_environment_requirements:
                        do_post_setup = False
                    else:
                        checked_environment_requirements.add(bundle.requirements_file)

                builder = EnvBuilderWithRequirements(bundle=script_config_bundle, do_post_setup=do_post_setup)
                path = Path(script_config_bundle.config_directory) / 'venv'
                if not path.exists():
                    builder.create(path)
                else:
                    env_dir = os.path.abspath(path)
                    context = builder.ensure_directories(env_dir)
                    if not builder.upgrade:
                        builder.post_setup(context)

        self.match_config = match_config
        self.game_interface.match_config = match_config
        self.game_interface.start_match_flatbuffer = match_config.create_flatbuffer()

        if USE_OLD_LAUNCH:
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
        raw_launcher_string = framework_config.get(RLBOT_CONFIGURATION_HEADER, LAUNCHER_PREFERENCE_KEY)
        if raw_launcher_string == RocketLeagueLauncherPreference.STEAM:
            self.launcher_preference = RocketLeagueLauncherPreference(RocketLeagueLauncherPreference.STEAM, False)
        else:
            self.launcher_preference = DEFAULT_LAUNCHER_PREFERENCE

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

    def launch_early_start_bot_processes(self, match_config: MatchConfig = None):
        """
        Some bots can start up before the game is ready and not be bothered by missing
        or strange looking values in the game tick packet, etc. Such bots can opt in to the
        early start category and enjoy extra time to load up before the match starts.

        WARNING: Early start is a bad idea if there's any risk that bots will not get their promised
        index. This can happen with remote RLBot, etc.
        """

        if self.match_config.networking_role == NetworkingRole.remote_rlbot_client:
            return  # The bot indices are liable to change, so don't start anything yet.

        self.logger.debug("Launching early-start bot processes")
        num_started = self.launch_bot_process_helper(early_starters_only=True, match_config=match_config or self.match_config)
        self.try_recieve_agent_metadata()
        if num_started > 0 and self.early_start_seconds > 0:
            self.logger.info(f"Waiting for {self.early_start_seconds} seconds to let early-start bots load.")
            end_time = datetime.now() + timedelta(seconds=self.early_start_seconds)
            while datetime.now() < end_time:
                self.try_recieve_agent_metadata()
                time.sleep(0.1)

    def launch_bot_processes(self, match_config: MatchConfig = None):
        self.logger.debug("Launching bot processes")
        self.launch_bot_process_helper(early_starters_only=False, match_config=match_config or self.match_config)

    def launch_bot_process_helper(self, early_starters_only=False, match_config: MatchConfig = None):
        # Start matchcomms here as it's only required for the bots.
        if not self.matchcomms_server:
            self.matchcomms_server = launch_matchcomms_server()
        self.bot_processes = {ind: proc for ind, proc in self.bot_processes.items() if proc.is_alive()}

        num_started = 0

        # Launch processes
        # TODO: this might be the right moment to fix the player indices based on a game tick packet.
        if not early_starters_only:
            if USE_OLD_LAUNCH:
                packet = game_data_struct.GameTickPacket()
                self.game_interface.update_live_data_packet(packet)
            else:
                packet = get_one_packet()

        # TODO: root through the packet and find discrepancies in the player index mapping.
        for i in range(min(self.num_participants, len(match_config.player_configs))):

            player_config = match_config.player_configs[i]
            if not player_config.has_bot_script():
                continue
            if early_starters_only and not self.bot_bundles[i].supports_early_start:
                continue

            spawn_id = player_config.spawn_id

            if early_starters_only:
                # Danger: we have low confidence in this since we're not leveraging the spawn id.
                participant_index = i
            else:
                participant_index = None

                self.logger.info(f'Player in slot {i} was sent with spawn id {spawn_id}, will search in the packet.')
                num_players = packet.num_cars if USE_OLD_LAUNCH else packet.PlayersLength()
                for n in range(0, num_players):
                    packet_spawn_id = packet.game_cars[n].spawn_id if USE_OLD_LAUNCH else packet.Players(n).SpawnId()
                    if spawn_id == packet_spawn_id:
                        self.logger.info(f'Looks good, considering participant index to be {n}')
                        participant_index = n
                if participant_index is None:
                    for prox_index, proc_info in self.bot_processes.items():
                        if spawn_id == proc_info.player_config.spawn_id:
                            participant_index = prox_index
                    if participant_index is None:
                        raise Exception(f"Unable to determine the bot index for spawn id {spawn_id}")

            if participant_index not in self.bot_processes:
                bundle = get_bot_config_bundle(player_config.config_path)
                deduped_name = str(self.match_config.player_configs[i].deduped_name)
                if bundle.supports_standalone:
                    executable = sys.executable
                    if bundle.use_virtual_environment:
                        if platform.system() == "Windows":
                            executable = str(Path(bundle.config_directory) / 'venv' / 'Scripts' / 'python.exe')
                        else:
                            executable = str(Path(bundle.config_directory) / 'venv' / 'bin' / 'python')
                    process = subprocess.Popen([
                        executable,
                        bundle.python_file,
                        '--config-file', str(player_config.config_path),
                        '--name', deduped_name,
                        '--team', str(self.teams[i]),
                        '--player-index', str(participant_index),
                        '--spawn-id', str(spawn_id),
                        '--matchcomms-url', self.matchcomms_server.root_url.geturl()
                    ], cwd=Path(bundle.config_directory).parent)
                    self.bot_processes[participant_index] = BotProcessInfo(process=None, subprocess=process, player_config=player_config)

                    # Insert immediately into the agent metadata map because the standalone process has no way to communicate it back out
                    self.agent_metadata_map[participant_index] = AgentMetadata(participant_index, deduped_name, self.teams[i], {process.pid})
                    self.num_metadata_received += 1
                else:
                    reload_request = mp.Event()
                    quit_callback = mp.Event()
                    self.bot_reload_requests.append(reload_request)
                    self.bot_quit_callbacks.append(quit_callback)
                    process = mp.Process(target=SetupManager.run_agent,
                                         args=(self.quit_event, quit_callback, reload_request, self.bot_bundles[i],
                                               deduped_name,
                                               self.teams[i], participant_index, self.python_files[i], self.agent_metadata_queue,
                                               match_config, self.matchcomms_server.root_url, spawn_id))
                    process.start()
                    self.bot_processes[participant_index] = BotProcessInfo(process=process, subprocess=None, player_config=player_config)
                num_started += 1

        self.logger.info(f"Successfully started {num_started} bot processes")

        process_configuration.configure_processes(self.agent_metadata_map, self.logger)

        scripts_started = 0
        for script_config in match_config.script_configs:
            script_config_bundle = get_script_config_bundle(script_config.config_path)
            if early_starters_only and not script_config_bundle.supports_early_start:
                continue
            executable = sys.executable
            if script_config_bundle.use_virtual_environment:
                if platform.system() == "Windows":
                    executable = str(Path(script_config_bundle.config_directory) / 'venv' / 'Scripts' / 'python.exe')
                else:
                    executable = str(Path(script_config_bundle.config_directory) / 'venv' / 'bin' / 'python')

            process = subprocess.Popen(
                [
                    executable,
                    script_config_bundle.script_file,
                    '--matchcomms-url', self.matchcomms_server.root_url.geturl()
                ],
                cwd=Path(script_config_bundle.config_directory).parent
            )
            self.logger.info(f"Started script with pid {process.pid} using {process.args}")
            self.script_processes[process.pid] = process
            scripts_started += 1

        self.logger.debug(f"Successfully started {scripts_started} scripts")

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
            else:
                try:
                    # https://python-forum.io/Thread-msvcrt-getkey-for-linux
                    import termios, sys
                    TERMIOS = termios

                    fd = sys.stdin.fileno()
                    old = termios.tcgetattr(fd)
                    new = termios.tcgetattr(fd)
                    new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
                    new[6][TERMIOS.VMIN] = 1
                    new[6][TERMIOS.VTIME] = 0
                    termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
                    command = None
                    try:
                        command = os.read(fd, 1)
                    finally:
                        termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
                    command = command.decode("utf-8")
                    if command.lower() == 'r':  # r: reload
                        self.reload_all_agents()
                    elif command.lower() == 'q' or command == '\u001b':  # q or ESC: quit
                        self.shut_down()
                        break
                    # Print instructions again if a alphabet character was pressed but no command was found
                    elif command.isalpha():
                        self.logger.info(instructions)
                except:
                    pass

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
                single_agent_metadata: AgentMetadata = self.agent_metadata_queue.get(timeout=0.1)
                num_recieved += 1
                if single_agent_metadata.name not in [pc.deduped_name for pc in self.match_config.player_configs]:
                    self.logger.warn(f"Got agent metadata for {single_agent_metadata.name} but it shouldn't be running!")

                self.helper_process_manager.start_or_update_helper_process(single_agent_metadata)
                self.agent_metadata_map[single_agent_metadata.index] = single_agent_metadata
                process_configuration.configure_processes(self.agent_metadata_map, self.logger)
            except queue.Empty:
                self.num_metadata_received += num_recieved
                break

        # Let's go through the agent metadata map and see if we can expand it with any child processes.
        # We'll do it every time this function is called (generall periodically),
        # we don't know when an agent might spawn another process.
        if process_configuration.append_child_pids(self.agent_metadata_map):
            process_configuration.configure_processes(self.agent_metadata_map, self.logger)

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
        self.kill_agent_process_ids(set(self.script_processes.keys()))

        if kill_all_pids:
            # The original meaning of the kill_all_pids flag only applied to bots, not scripts,
            # so we are doing that separately.
            self.kill_agent_process_ids(process_configuration.extract_all_pids(self.agent_metadata_map))

        self.kill_matchcomms_server()

        # Drain the agent_metadata_queue to make sure nothing rears its head later.
        while True:  # will exit on queue.Empty
            try:
                metadata = self.agent_metadata_queue.get(timeout=0.1)
                self.logger.warn(f"Drained out metadata for {metadata.name} during shutdown!")
            except queue.Empty:
                break

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

        # Set the working directory to one level above the bot cfg file.
        # This mimics the behavior you get when executing run.py in one of the
        # example bot repositories, so bots will be more likely to 'just work'
        # even if the developer is careless about file paths.
        os.chdir(Path(bundle.config_directory).parent)

        agent_class_wrapper = import_agent(python_file)
        config_file = agent_class_wrapper.get_loaded_class().base_create_agent_configurations()
        config_file.parse_file(bundle.config_obj, config_directory=bundle.config_directory)

        if hasattr(agent_class_wrapper.get_loaded_class(), "run_independently"):
            bm = BotManagerIndependent(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                       agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root,
                                       spawn_id)
        else:
            bm = BotManagerStruct(terminate_event, callback_event, reload_request, config_file, name, team, index,
                                  agent_class_wrapper, agent_telemetry_queue, match_config, matchcomms_root, spawn_id)
        bm.run()

    def kill_bot_processes(self):
        for process_info in self.bot_processes.values():
            proc = process_info.process or process_info.subprocess
            proc.terminate()
        for process_info in self.bot_processes.values():
            if process_info.process:
                process_info.process.join(timeout=1)
        self.bot_processes.clear()
        self.num_metadata_received = 0

    def send_sigterm_recursive(self, pid: int) -> List[psutil.Process]:
        """
        Returns the list of processes under the pid and including the pid for further handling,
        because they may become orphaned by the sigterm.
        """
        all_processes = []
        immediate_children = []
        try:
            process = psutil.Process(pid)
            immediate_children = [c for c in process.children(recursive=False)]
            all_processes = [process] + [c for c in process.children(recursive=True)]
            process.send_signal(signal.SIGTERM)
        except Exception as ex:
            self.logger.debug(f"Got {ex} while sending sigterm to pid {pid}.")

        for c in immediate_children:
            self.send_sigterm_recursive(c.pid)

        return all_processes

    def kill_agent_process_ids(self, pids: Set[int]):
        all_processes = []
        for pid in pids:
            all_processes += self.send_sigterm_recursive(pid)

        time.sleep(.5)

        for c in all_processes:
            try:
                c.kill()
            except Exception as ex:
                self.logger.debug(f"Got {ex} while killing pid {pid}.")

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
        return  # TODO: Linux support.

    try:
        key = OpenKey(ConnectRegistry(None, HKEY_CURRENT_USER), r'Software\Valve\Steam')
        val, val_type = QueryValueEx(key, 'SteamExe')
    except FileNotFoundError:
        return
    if val_type != REG_SZ:
        return
    return Path(val)


