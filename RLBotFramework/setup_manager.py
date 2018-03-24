import configparser
import msvcrt
import multiprocessing as mp
import queue

from RLBotFramework.agents import bot_manager
from RLBotFramework.base_extension import BaseExtension
from RLBotFramework.utils.class_importer import import_class_with_base, import_agent
from RLBotFramework.utils.logging_utils import get_logger, DEFAULT_LOGGER
from RLBotFramework.utils.process_configuration import configure_processes
from RLBotFramework.utils.rlbot_config_parser import create_bot_config_layout, parse_configurations, EXTENSION_PATH_KEY
from RLBotFramework.utils.structures import bot_input_struct as bi
from RLBotFramework.utils.structures.game_interface import GameInterface
from RLBotFramework.utils.structures.quick_chats import QuickChatManager

RLBOT_CONFIG_FILE = 'rlbot.cfg'
RLBOT_CONFIGURATION_HEADER = 'RLBot Configuration'


class SetupManager:
    has_started = False
    num_participants = None
    names = None
    teams = None
    python_files = None
    parameters = None
    game_input_packet = None
    agent_metadata_queue = None
    agent_metadata_map = None
    quit_event = None
    extension = None

    def __init__(self):
        self.logger = get_logger(DEFAULT_LOGGER)
        self.game_interface = GameInterface(self.logger)
        self.quick_chat_manager = QuickChatManager(self.game_interface)
        self.callbacks = []

    def startup(self):
        if self.has_started:
            return
        self.logger.debug("Starting up game management")
        self.game_interface.inject_dll()
        self.game_interface.load_interface()
        # Create Quit event
        self.quit_event = mp.Event()

        self.agent_metadata_map = {}
        self.agent_metadata_queue = mp.Queue()

        self.has_started = True

    def load_config(self, framework_config=None, bot_configs=None, looks_configs=None):
        self.logger.debug('reading the configs')

        # Set up RLBot.cfg
        if framework_config is None:
            raw_config_parser = configparser.RawConfigParser()
            raw_config_parser.read(RLBOT_CONFIG_FILE)

            framework_config = create_bot_config_layout()
            framework_config.parse_file(raw_config_parser, max_index=10)
        if bot_configs is None:
            bot_configs = {}
        if looks_configs is None:
            looks_configs = {}

        # Open anonymous shared memory for entire GameInputPacket and map buffer
        self.game_input_packet = bi.GameInputPacket()

        self.num_participants, self.names, self.teams, self.python_files, self.parameters = parse_configurations(
            self.game_input_packet, framework_config, bot_configs, looks_configs)

        self.game_interface.participants = self.num_participants
        self.game_interface.game_input_packet = self.game_input_packet

        extension_path = framework_config.get(RLBOT_CONFIGURATION_HEADER, EXTENSION_PATH_KEY)
        if extension_path is not None:
            self.load_extension(extension_path)

    def launch_bot_processes(self):
        self.logger.debug("Launching bot processes")

        # Launch processes
        for i in range(self.num_participants):
            if self.game_input_packet.sPlayerConfiguration[i].bRLBotControlled:
                queue_holder = self.quick_chat_manager.create_queue_for_bot(i, self.teams[i])
                callback = mp.Event()
                self.callbacks.append(callback)
                process = mp.Process(target=SetupManager.run_agent,
                                     args=(self.quit_event, callback, self.parameters[i],
                                           str(self.game_input_packet.sPlayerConfiguration[i].wName),
                                           self.teams[i], i, self.python_files[i], self.agent_metadata_queue, queue_holder))
                process.start()

        self.logger.debug("Successfully started bot processes")

    def run(self):
        self.quick_chat_manager.start_manager()
        self.logger.debug("Successfully started quick chat manager")
        self.game_interface.start_match()
        self.logger.info("Match has started")

        self.logger.info("Press any character to exit")
        while True:
            if msvcrt.kbhit():
                msvcrt.getch()
                break
            try:
                single_agent_metadata = self.agent_metadata_queue.get(timeout=1)
                self.agent_metadata_map[single_agent_metadata['index']] = single_agent_metadata
                configure_processes(self.agent_metadata_map, self.logger)
            except queue.Empty:
                pass
            except Exception as ex:
                print(ex)
                pass

    def load_extension(self, extension_filename):
        extension_class = import_class_with_base(extension_filename, BaseExtension).get_loaded_class()
        self.extension = extension_class(self)
        self.game_interface.set_extension(self.extension)

    @staticmethod
    def run_agent(terminate_event, callback_event, config_file, name, team, index, python_file,
                  agent_telemetry_queue, queue_holder):

        agent_class_wrapper = import_agent(python_file)

        if hasattr(agent_class_wrapper.get_loaded_class(), "run_independently"):
            bm = bot_manager.BotManagerIndependent(terminate_event, callback_event, config_file, name, team,
                                                   index, agent_class_wrapper, agent_telemetry_queue, queue_holder)

        elif hasattr(agent_class_wrapper.get_loaded_class(), "get_output_proto"):
            bm = bot_manager.BotManagerProto(terminate_event, callback_event, config_file, name, team,
                                             index, agent_class_wrapper, agent_telemetry_queue, queue_holder)
        else:
            bm = bot_manager.BotManagerStruct(terminate_event, callback_event, config_file, name, team,
                                              index, agent_class_wrapper, agent_telemetry_queue, queue_holder)
        bm.run()
