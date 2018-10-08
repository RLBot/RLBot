import os
import time
import traceback
from datetime import datetime, timedelta

from rlbot.botmanager.agent_metadata import AgentMetadata
from rlbot.utils import rate_limiter
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_interface import GameInterface
from rlbot.utils.structures.game_status import RLBotCoreStatus
from rlbot.utils.structures.quick_chats import register_for_quick_chat, send_quick_chat_flat, send_quick_chat

GAME_TICK_PACKET_REFRESHES_PER_SECOND = 120  # 2*60. https://en.wikipedia.org/wiki/Nyquist_rate
MAX_AGENT_CALL_PERIOD = timedelta(seconds=1.0 / 30)  # Minimum call rate when paused.
REFRESH_IN_PROGRESS = 1
REFRESH_NOT_IN_PROGRESS = 0
MAX_CARS = 10


class BotManager:
    def __init__(self, terminate_request_event, termination_complete_event, reload_request_event, bot_configuration,
                 name, team, index, agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder):
        """
        :param terminate_request_event: an Event (multiprocessing) which will be set from the outside when the program is trying to terminate
        :param termination_complete_event: an Event (multiprocessing) which should be set from inside this class when termination has completed successfully
        :param reload_request_event: an Event (multiprocessing) which will be set from the outside to force a reload of the agent
        :param reload_complete_event: an Event (multiprocessing) which should be set from inside this class when reloading has completed successfully
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
        self.reload_request_event = reload_request_event
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
        self.ball_prediction = None
        self.rigid_body_tick = None

    def send_quick_chat_from_agent(self, team_only, quick_chat):
        """
        Passes the agents quick chats to the game, and also to other python bots.
        This does perform limiting.
        You are limited to 5 quick chats in a 2 second period starting from the first chat.
        This means you can spread your chats out to be even within that 2 second period.
        You could spam them in the first little bit but then will be throttled.
        """

        # Send the quick chat to the game
        rlbot_status = send_quick_chat_flat(self.game_interface, self.index, self.team, team_only, quick_chat)

        if rlbot_status == RLBotCoreStatus.QuickChatRateExceeded:
            self.logger.debug('quick chat disabled')
        else:
            # Make the quick chat visible to other python bots. Unfortunately other languages can't see it.
            send_quick_chat(self.quick_chat_queue_holder, self.index, self.team, team_only, quick_chat)

    def load_agent(self):
        """
        Loads and initializes an agent using instance variables, registers for quick chat and sets render functions.
        :return: An instance of an agent, and the agent class file.
        """
        agent_class = self.agent_class_wrapper.get_loaded_class()
        agent = agent_class(self.name, self.team, self.index)
        agent.logger = self.logger
        agent.load_config(self.bot_configuration.get_header("Bot Parameters"))

        self.update_metadata_queue(agent)
        self.set_render_manager(agent)

        agent_class_file = self.agent_class_wrapper.python_file
        agent._register_quick_chat(self.send_quick_chat_from_agent)
        agent._register_field_info(self.get_field_info)
        agent._register_set_game_state(self.set_game_state)
        agent._register_ball_prediction(self.get_ball_prediction)
        agent._register_ball_prediction_struct(self.get_ball_prediction_struct)
        agent._register_get_rigid_body_tick(self.get_rigid_body_tick)
        register_for_quick_chat(self.quick_chat_queue_holder, agent.handle_quick_chat, self.terminate_request_event)

        # Once all engine setup is done, do the agent-specific initialization, if any:
        agent.initialize_agent()
        return agent, agent_class_file

    def set_render_manager(self, agent):
        """
        Sets the render manager for the agent.
        :param agent: An instance of an agent.
        """
        rendering_manager = self.game_interface.renderer.get_rendering_manager(self.index, self.team)
        agent._set_renderer(rendering_manager)

    def update_metadata_queue(self, agent):
        """
        Adds a new instance of AgentMetadata into the `agent_metadata_queue` using `agent` data.
        :param agent: An instance of an agent.
        """
        pids = {os.getpid(), *agent.get_extra_pids()}

        helper_process_request = agent.get_helper_process_request()

        self.agent_metadata_queue.put(AgentMetadata(self.index, self.name, self.team, pids, helper_process_request))

    def reload_agent(self, agent, agent_class_file):
        """
        Reloads the agent. Can throw exceptions. External classes should use reload_event.set() instead.
        :param agent: An instance of an agent.
        :param agent_class_file: The agent's class file.
        :return: The reloaded instance of the agent, and the agent class file.
        """
        self.logger.info('Reloading Agent: ' + agent_class_file)
        self.agent_class_wrapper.reload()
        old_agent = agent
        agent, agent_class_file = self.load_agent()

        # Retire after the replacement initialized properly.
        if hasattr(old_agent, 'retire'):
            old_agent.retire()

        return agent, agent_class_file

    def run(self):
        """
        Loads interface for RLBot, prepares environment and agent, and calls the update for the agent.
        """
        self.logger.debug('initializing agent')
        self.game_interface.load_interface()

        self.prepare_for_run()

        # Create Ratelimiter
        rate_limit = rate_limiter.RateLimiter(GAME_TICK_PACKET_REFRESHES_PER_SECOND)
        last_tick_game_time = None  # What the tick time of the last observed tick was
        last_call_real_time = datetime.now()  # When we last called the Agent

        # Get bot module
        agent, agent_class_file = self.load_agent()

        last_module_modification_time = os.stat(agent_class_file).st_mtime

        # Run until main process tells to stop
        while not self.terminate_request_event.is_set():
            before = datetime.now()
            self.pull_data_from_game()
            # game_tick_packet = self.game_interface.get
            # Read from game data shared memory

            # Run the Agent only if the game_info has updated.
            tick_game_time = self.get_game_time()
            should_call_while_paused = datetime.now() - last_call_real_time >= MAX_AGENT_CALL_PERIOD
            if tick_game_time != last_tick_game_time or should_call_while_paused:
                last_tick_game_time = tick_game_time
                last_call_real_time = datetime.now()

                # Reload the Agent if it has been modified or if reload is requested from outside.
                try:
                    new_module_modification_time = os.stat(agent_class_file).st_mtime
                    if new_module_modification_time != last_module_modification_time or self.reload_request_event.is_set():
                        self.reload_request_event.clear()
                        last_module_modification_time = new_module_modification_time
                        agent, agent_class_file = self.reload_agent(agent, agent_class_file)
                except FileNotFoundError:
                    self.logger.error("Agent file {} was not found. Will try again.".format(agent_class_file))
                    time.sleep(0.5)
                except Exception:
                    self.logger.error("Reloading the agent failed:\n" + traceback.format_exc())
                    time.sleep(0.5)  # Avoid burning CPU / logs if this starts happening constantly

                # Call agent
                try:
                    self.call_agent(agent, self.agent_class_wrapper.get_loaded_class())
                except Exception as e:
                    self.logger.error("Call to agent failed:\n" + traceback.format_exc())

            # Ratelimit here
            after = datetime.now()

            rate_limit.acquire(after - before)

        if hasattr(agent, 'retire'):
            agent.retire()
        # If terminated, send callback
        self.termination_complete_event.set()

    def get_field_info(self):
        return self.game_interface.get_field_info()

    def get_rigid_body_tick(self):
        """Get the most recent state of the physics engine."""
        return self.game_interface.update_rigid_body_tick(self.rigid_body_tick)

    def set_game_state(self, game_state):
        return self.game_interface.set_game_state(game_state)

    def get_ball_prediction(self):
        return self.game_interface.get_ball_prediction()

    def get_ball_prediction_struct(self):
        raise NotImplementedError

    def prepare_for_run(self):
        raise NotImplementedError

    def call_agent(self, agent, agent_class):
        raise NotImplementedError

    def get_game_time(self):
        raise NotImplementedError

    def pull_data_from_game(self):
        raise NotImplementedError
