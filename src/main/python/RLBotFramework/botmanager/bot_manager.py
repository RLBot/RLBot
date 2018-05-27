import os
import time
import traceback
from datetime import datetime, timedelta

from RLBotFramework.botmanager.agent_metadata import AgentMetadata
from RLBotFramework.utils import rate_limiter
from RLBotFramework.utils.class_importer import ExternalClassWrapper
from RLBotFramework.utils.logging_utils import get_logger
from RLBotFramework.utils.structures.game_interface import GameInterface
from RLBotFramework.utils.structures.quick_chats import send_quick_chat, register_for_quick_chat

GAME_TICK_PACKET_REFRESHES_PER_SECOND = 120  # 2*60. https://en.wikipedia.org/wiki/Nyquist_rate
MAX_CHAT_RATE = 2.0
MAX_CHAT_COUNT = 5
MAX_AGENT_CALL_PERIOD = timedelta(seconds=1.0 / 30)  # Minimum call rate when paused.
REFRESH_IN_PROGRESS = 1
REFRESH_NOT_IN_PROGRESS = 0
MAX_CARS = 10


class BotManager:
    def __init__(self, terminate_request_event, termination_complete_event, bot_configuration, name, team, index,
                 agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder):
        """
        :param terminate_request_event: an Event (multiprocessing) which will be set from the outside when the program is trying to terminate
        :param termination_complete_event: an Event (multiprocessing) which should be set from inside this class when termination has completed successfully
        :param bot_configuration: parameters which will be passed to the bot's constructor
        :param name: name which will be passed to the bot's constructor. Will probably be displayed in-game.
        :param team: 0 for blue team or 1 for orange team. Will be passed to the bot's constructor.
        :param index: The player index, i.e. "this is player number <index>". Will be passed to the bot's constructor.
            Can be used to pull the correct data corresponding to the bot's car out of the game tick packet.
        :param agent_class_wrapper: The ExternalClassWrapper object that can be used to load and reload the bot
        :param agent_metadata_queue: a Queue (multiprocessing) which expects to receive certain metadata about the agent once available.
        :param quick_chat_queue_holder: A data structure which helps the bot send and receive quickchat
        """
        self.terminate_request_event = terminate_request_event
        self.termination_complete_event = termination_complete_event
        self.bot_configuration = bot_configuration
        self.name = name
        self.team = team
        self.index = index
        self.agent_class_wrapper = agent_class_wrapper
        self.agent_metadata_queue = agent_metadata_queue
        self.logger = get_logger('bot' + str(self.index))
        self.game_interface = GameInterface(self.logger)
        self.quick_chat_queue_holder = quick_chat_queue_holder
        self.last_chat_time = time.time()
        self.chat_counter = 0
        self.reset_chat_time = True
        self.game_tick_packet = None
        self.bot_input = None

    def send_quick_chat_from_agent(self, team_only, quick_chat):
        """
        Passes the agents quick chats to the other bots.
        This does perform limiting.
        You are limited to 5 quick chats in a 2 second period starting from the first chat.
        This means you can spread your chats out to be even within that 2 second period.
        You could spam them in the first little bit but then will be throttled.
        """
        time_since_last_chat = time.time() - self.last_chat_time
        if not self.reset_chat_time and time_since_last_chat >= MAX_CHAT_RATE:
            self.reset_chat_time = True
        if self.reset_chat_time:
            self.last_chat_time = time.time()
            self.chat_counter = 0
            self.reset_chat_time = False
        if self.chat_counter < MAX_CHAT_COUNT:
            send_quick_chat(self.quick_chat_queue_holder, self.index, self.team, team_only, quick_chat)
            self.chat_counter += 1
        else:
            self.logger.debug('quick chat disabled for %s', MAX_CHAT_RATE - time_since_last_chat)

    def load_agent(self, agent_wrapper: ExternalClassWrapper):
        agent_class = agent_wrapper.get_loaded_class()
        agent = agent_class(self.name, self.team, self.index)
        agent.logger = self.logger
        agent.load_config(self.bot_configuration.get_header("Bot Parameters"))
        agent.initialize_agent()

        self.update_metadata_queue(agent)
        agent_class_file = self.agent_class_wrapper.python_file
        agent.register_quick_chat(self.send_quick_chat_from_agent)
        register_for_quick_chat(self.quick_chat_queue_holder, agent.receive_quick_chat, self.terminate_request_event)
        return agent, agent_class_file

    def set_render_functions(self, agent):
        render_functions = self.game_interface.renderer.get_render_functions()
        render_functions.set_bot_index(self.index)
        agent.set_renderer(render_functions)

    def update_metadata_queue(self, agent):
        pids = set()
        pids.add(os.getpid())
        pids.update(agent.get_extra_pids())

        helper_process_request = agent.get_helper_process_request()

        self.agent_metadata_queue.put(AgentMetadata(self.index, self.name, self.team, pids, helper_process_request))

    def run(self):
        self.logger.debug('initializing agent')
        self.game_interface.load_interface()

        self.prepare_for_run()

        # Create Ratelimiter
        rate_limit = rate_limiter.RateLimiter(GAME_TICK_PACKET_REFRESHES_PER_SECOND)
        last_tick_game_time = None  # What the tick time of the last observed tick was
        last_call_real_time = datetime.now()  # When we last called the Agent

        # Get bot module
        agent, agent_class_file = self.load_agent(self.agent_class_wrapper)
        self.set_render_functions(agent)

        last_module_modification_time = os.stat(agent_class_file).st_mtime

        # Run until main process tells to stop
        while not self.terminate_request_event.is_set():
            before = datetime.now()
            self.pull_data_from_game()
            # game_tick_packet = self.game_interface.get
            # Read from game data shared memory

            # Run the Agent only if the gameInfo has updated.
            tick_game_time = self.get_game_time()
            should_call_while_paused = datetime.now() - last_call_real_time >= MAX_AGENT_CALL_PERIOD
            if tick_game_time != last_tick_game_time or should_call_while_paused:
                last_tick_game_time = tick_game_time
                last_call_real_time = datetime.now()

                try:
                    # Reload the Agent if it has been modified.
                    new_module_modification_time = os.stat(agent_class_file).st_mtime
                    if new_module_modification_time != last_module_modification_time:
                        last_module_modification_time = new_module_modification_time
                        self.logger.info('Reloading Agent: ' + agent_class_file)
                        self.agent_class_wrapper.reload()
                        old_agent = agent
                        agent, agent_class_file = self.load_agent(self.agent_class_wrapper)
                        self.set_render_functions(agent)
                        # Retire after the replacement initialized properly.
                        if hasattr(old_agent, 'retire'):
                            old_agent.retire()

                    # Call agent
                    self.call_agent(agent, self.agent_class_wrapper.get_loaded_class())
                except Exception as e:
                    self.logger.error("Reloading the agent failed:\n" + traceback.format_exc())

            # Ratelimit here
            after = datetime.now()

            rate_limit.acquire(after - before)

        if hasattr(agent, 'retire'):
            agent.retire()
        # If terminated, send callback
        self.termination_complete_event.set()

    def prepare_for_run(self):
        raise NotImplementedError

    def call_agent(self, agent, agent_class):
        raise NotImplementedError

    def get_game_time(self):
        raise NotImplementedError

    def pull_data_from_game(self):
        raise NotImplementedError
