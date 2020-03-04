import glob
import os
import time
import traceback
from datetime import datetime, timedelta
from urllib.parse import ParseResult as URL

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, MAXIMUM_TICK_RATE_PREFERENCE_KEY
from rlbot.botmanager.agent_metadata import AgentMetadata
from rlbot.matchconfig.match_config import MatchConfig
from rlbot.messages.flat import MatchSettings
from rlbot.utils.game_state_util import GameState
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.rlbot_exception import EmptyDllResponse
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.structures.game_interface import GameInterface
from rlbot.utils.structures.game_status import RLBotCoreStatus
from rlbot.utils.structures.quick_chats import send_quick_chat_flat

MAX_AGENT_CALL_PERIOD = timedelta(seconds=1.0 / 2)  # Minimum call rate when paused.
REFRESH_IN_PROGRESS = 1
REFRESH_NOT_IN_PROGRESS = 0
MAX_CARS = 10

# Backward compatibility with Python 3.6:
try:
    time.perf_counter_ns()
except AttributeError:
    time.perf_counter_ns = lambda: time.perf_counter() * 1e9


# Backward compatibility with Python 3.6:
try:
    time.perf_counter_ns()
except AttributeError:
    time.perf_counter_ns = lambda: time.perf_counter() * 1e9


class BotManager:

    def __init__(self, terminate_request_event, termination_complete_event, reload_request_event, bot_configuration,
                 name, team, index, agent_class_wrapper, agent_metadata_queue, match_config: MatchConfig,
                 matchcomms_root: URL, spawn_id: int):
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
        :param agent_metadata_queue: a Queue (multiprocessing) which expects to receive AgentMetadata once available.
        :param match_config: Describes the match that is being played.
        :param matchcomms_root: The server to connect to if you want to communicate to other participants in the match.
        :param spawn_id: The identifier we expect to see in the game tick packet at our player index. If it does not
            match, then we will force the agent to retire. Pass None to opt out of this behavior.
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
        self.last_chat_time = time.time()
        self.chat_counter = 0
        self.reset_chat_time = True
        self.game_tick_packet = None
        self.bot_input = None
        self.ball_prediction = None
        self.rigid_body_tick = None
        self.match_config = match_config
        self.matchcomms_root = matchcomms_root
        self.last_message_index = 0
        self.agent = None
        self.agent_class_file = None
        self.last_module_modification_time = 0
        self.scan_last = 0
        self.scan_temp = 0
        self.file_iterator = None
        self.maximum_tick_rate_preference = bot_configuration.get(BOT_CONFIG_MODULE_HEADER,
                                                                  MAXIMUM_TICK_RATE_PREFERENCE_KEY)
        self.spawn_id = spawn_id
        self.counter = 0

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

    def load_agent(self):
        """
        Loads and initializes an agent using instance variables, registers for quick chat and sets render functions.
        :return: An instance of an agent, and the agent class file.
        """
        agent_class = self.agent_class_wrapper.get_loaded_class()
        self.agent = agent_class(self.name, self.team, self.index)
        self.agent.init_match_config(self.match_config)

        self.agent.load_config(self.bot_configuration.get_header("Bot Parameters"))

        self.update_metadata_queue()
        self.set_render_manager()

        self.agent_class_file = self.agent_class_wrapper.python_file
        self.agent._register_quick_chat(self.send_quick_chat_from_agent)
        self.agent._register_field_info(self.get_field_info)
        self.agent._register_set_game_state(self.set_game_state)
        self.agent._register_ball_prediction(self.get_ball_prediction)
        self.agent._register_ball_prediction_struct(self.get_ball_prediction_struct)
        self.agent._register_get_rigid_body_tick(self.get_rigid_body_tick)
        self.agent._register_match_settings_func(self.get_match_settings)
        self.agent.matchcomms_root = self.matchcomms_root

        # Once all engine setup is done, do the agent-specific initialization, if any:
        self.agent.initialize_agent()
        return self.agent, self.agent_class_file

    def set_render_manager(self):
        """
        Sets the render manager for the agent.
        :param agent: An instance of an agent.
        """
        rendering_manager = self.game_interface.renderer.get_rendering_manager(self.index, self.team)
        self.agent._set_renderer(rendering_manager)

    def update_metadata_queue(self):
        """
        Adds a new instance of AgentMetadata into the `agent_metadata_queue` using `agent` data.
        :param agent: An instance of an agent.
        """
        pids = {os.getpid(), *self.agent.get_extra_pids()}

        helper_process_request = self.agent.get_helper_process_request()

        self.agent_metadata_queue.put(AgentMetadata(self.index, self.name, self.team, pids, helper_process_request))

    def reload_agent(self):
        """
        Reloads the agent. Can throw exceptions. External classes should use reload_event.set() instead.
        """
        self.logger.info('Reloading Agent: ' + self.agent.name)
        self.agent_class_wrapper.reload()
        old_agent = self.agent
        self.load_agent()
        self.retire_agent(old_agent)  # We do this after load_agent as load_agent might fail.

    def run(self):
        """
        Loads interface for RLBot, prepares environment and agent, and calls the update for the agent.
        """
        self.logger.debug('initializing agent')
        self.game_interface.load_interface()

        self.prepare_for_run()

        last_tick_game_time = 0  # What the tick time of the last observed tick was
        last_call_real_time = datetime.now()  # When we last called the Agent
        frame_urgency = 0  # If the bot is getting called more than its preferred max rate, urgency will go negative.

        # Get bot module
        self.load_agent()

        self.last_module_modification_time = self.check_modification_time(os.path.dirname(self.agent_class_file))

        # Run until main process tells to stop, or we detect Ctrl+C
        try:
            while not self.terminate_request_event.is_set():
                self.pull_data_from_game()

                # Run the Agent only if the game_info has updated.
                tick_game_time = self.get_game_time()
                now = datetime.now()
                should_call_while_paused = now - last_call_real_time >= MAX_AGENT_CALL_PERIOD or self.match_config.enable_lockstep

                if frame_urgency < 1 / self.maximum_tick_rate_preference:
                    # Urgency increases every frame, but don't let it build up a large backlog
                    frame_urgency += tick_game_time - last_tick_game_time

                if tick_game_time != last_tick_game_time and frame_urgency >= 0 or should_call_while_paused:
                    last_call_real_time = now
                    # Urgency decreases when a tick is processed.
                    if frame_urgency > 0:
                        frame_urgency -= 1 / self.maximum_tick_rate_preference

                    self.perform_tick()
                    self.counter += 1

                last_tick_game_time = tick_game_time
                if self.spawn_id is not None:
                    packet_spawn_id = self.get_spawn_id()
                    if packet_spawn_id != self.spawn_id:
                        self.logger.warn(f"The bot's spawn id {self.spawn_id} does not match the one in the packet "
                                         f"{packet_spawn_id}, retiring!")
                        break

        except KeyboardInterrupt:
            self.terminate_request_event.set()

        self.retire_agent(self.agent)

        # If terminated, send callback
        self.termination_complete_event.set()

    def perform_tick(self):
        # Reload the Agent if it has been modified or if reload is requested from outside.
        # But only do that every 20th tick.
        if self.agent.is_hot_reload_enabled() and self.counter % 20 == 1:
            self.hot_reload_if_necessary()
        try:
            chat_messages = self.game_interface.receive_chat(self.index, self.team, self.last_message_index)
            for i in range(0, chat_messages.MessagesLength()):
                message = chat_messages.Messages(i)
                if len(self.match_config.player_configs) > message.PlayerIndex():
                    self.agent.handle_quick_chat(
                        index=message.PlayerIndex(),
                        team=self.match_config.player_configs[message.PlayerIndex()].team,
                        quick_chat=message.QuickChatSelection())
                else:
                    self.logger.debug(f"Skipping quick chat delivery for {message.MessageIndex()} because "
                                      "we don't recognize the player index. Probably stale.")
                self.last_message_index = message.MessageIndex()
        except EmptyDllResponse:
            self.logger.debug("Empty response when reading chat!")
        # Call agent
        try:
            self.call_agent(self.agent, self.agent_class_wrapper.get_loaded_class())
        except Exception as e:
            self.logger.error("Call to agent failed:\n" + traceback.format_exc())

    def hot_reload_if_necessary(self):
        try:
            new_module_modification_time = self.check_modification_time(os.path.dirname(self.agent_class_file))
            if new_module_modification_time != self.last_module_modification_time or self.reload_request_event.is_set():
                self.reload_request_event.clear()
                self.last_module_modification_time = new_module_modification_time
                # Clear the render queue on reload.
                if hasattr(self.agent, 'renderer') and isinstance(self.agent.renderer, RenderingManager):
                    self.agent.renderer.clear_all_touched_render_groups()
                self.reload_agent()
        except FileNotFoundError:
            self.logger.error(f"Agent file {self.agent_class_file} was not found. Will try again.")
            time.sleep(0.5)
        except Exception:
            self.logger.error("Reloading the agent failed:\n" + traceback.format_exc())
            time.sleep(5)  # Avoid burning CPU, and give the user a moment to read the log

    def retire_agent(self, agent):
        # Shut down the bot by calling cleanup functions.
        if hasattr(agent, 'retire'):
            try:
                agent.retire()
            except Exception as e:
                self.logger.error("Retiring the agent failed:\n" + traceback.format_exc())
        if hasattr(agent, 'renderer') and isinstance(agent.renderer, RenderingManager):
            agent.renderer.clear_all_touched_render_groups()
        # Zero out the inputs, so it's more obvious that the bot has stopped.
        self.game_interface.update_player_input(PlayerInput(), self.index)

        # Don't trust the agent to shut down its own client in retire().
        if agent._matchcomms is not None:
            agent._matchcomms.close()

    def check_modification_time(self, directory, timeout_ms=1):
        if self.scan_last > 0 and timeout_ms is not None:
            stop_time = time.perf_counter_ns() + timeout_ms * 10**6
        else:
            stop_time = None
        if self.file_iterator is None:
            self.file_iterator = glob.iglob(f"{directory}/**/*.py", recursive=True)
        for f in self.file_iterator:
            self.scan_temp = max(self.scan_temp, os.stat(f).st_mtime)
            if stop_time is not None and time.perf_counter_ns() > stop_time:
                # Timeout exceeded. The scan will pick up from here on the next call.
                break
        else:
            # Scan finished. Update the modification time and restart the scan:
            self.scan_last, self.scan_temp = self.scan_temp, 0
            self.file_iterator = None
        return self.scan_last

    def get_field_info(self):
        return self.game_interface.get_field_info()

    def get_rigid_body_tick(self):
        """Get the most recent state of the physics engine."""
        return self.game_interface.update_rigid_body_tick(self.rigid_body_tick)

    def set_game_state(self, game_state: GameState) -> None:
        self.game_interface.set_game_state(game_state)

    def get_ball_prediction(self):
        return self.game_interface.get_ball_prediction()

    def get_match_settings(self) -> MatchSettings:
        return self.game_interface.get_match_settings()

    def get_ball_prediction_struct(self):
        raise NotImplementedError

    def prepare_for_run(self):
        raise NotImplementedError

    def call_agent(self, agent: BaseAgent, agent_class):
        raise NotImplementedError

    def get_game_time(self):
        raise NotImplementedError

    def pull_data_from_game(self):
        raise NotImplementedError

    def get_spawn_id(self):
        raise NotImplementedError
