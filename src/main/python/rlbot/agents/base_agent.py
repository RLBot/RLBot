from typing import Optional
from urllib.parse import ParseResult as URL

from flatbuffers import Builder
from rlbot.agents.rlbot_runnable import RLBotRunnable, LOCATIONS_HEADER, DETAILS_HEADER
from rlbot.botmanager.helper_process_request import HelperProcessRequest
from rlbot.matchcomms.client import MatchcommsClient
from rlbot.messages.flat import MatchSettings, ControllerState, PlayerInput
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.game_state_util import GameState
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.game_data_struct import GameTickPacket, FieldInfoPacket
from rlbot.utils.structures.legacy_data_v3 import convert_to_legacy_v3
from rlbot.utils.structures.quick_chats import QuickChats
from rlbot.utils.structures.rigid_body_struct import RigidBodyTick

BOT_CONFIG_MODULE_HEADER = LOCATIONS_HEADER
BOT_CONFIG_AGENT_HEADER = 'Bot Parameters'
BOT_CONFIG_DETAILS_HEADER = DETAILS_HEADER
PYTHON_FILE_KEY = 'python_file'
SUPPORTS_STANDALONE = 'supports_standalone'
LOADOUT_GENERATOR_FILE_KEY = 'loadout_generator'
LOGO_FILE_KEY = 'logo_file'
LOOKS_CONFIG_KEY = 'looks_config'
BOT_NAME_KEY = "name"
SUPPORTS_EARLY_START_KEY = "supports_early_start"
MAXIMUM_TICK_RATE_PREFERENCE_KEY = "maximum_tick_rate_preference"


class SimpleControllerState:
    """
    Building flatbuffer objects is verbose and error prone. This class provides a friendlier
    interface to bot makers.
    """

    def __init__(self,
                 steer: float = 0.0,
                 throttle: float = 0.0,
                 pitch: float = 0.0,
                 yaw: float = 0.0,
                 roll: float = 0.0,
                 jump: bool = False,
                 boost: bool = False,
                 handbrake: bool = False,
                 use_item: bool = False):
        """
        :param steer:    Range: -1 .. 1, negative=left, positive=right
        :param throttle: Range: -1 .. 1, negative=backward, positive=forward
        :param pitch:    Range: -1 .. 1, negative=nose-down, positive=nose-up
        :param yaw:      Range: -1 .. 1, negative=nose-left, positive=nose-right
        :param roll:     Range: -1 .. 1, negative=anticlockwise, positive=clockwise  (when looking forwards along the car)
        :param jump: Analogous to the jump button in game.
        :param boost: Analogous to the boost button in game.
        :param handbrake: Analogous to the handbrake button in game.
        :param use_item: Analogous to the use item button (from rumble) in game.
        """
        self.steer = steer
        self.throttle = throttle
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.jump = jump
        self.boost = boost
        self.handbrake = handbrake
        self.use_item = use_item

    def to_flatbuffer(self, player_index: int) -> Builder:
        builder = Builder(100)
        ControllerState.ControllerStateStart(builder)
        ControllerState.ControllerStateAddSteer(builder, self.steer)
        ControllerState.ControllerStateAddThrottle(builder, self.throttle)
        ControllerState.ControllerStateAddPitch(builder, self.pitch)
        ControllerState.ControllerStateAddYaw(builder, self.yaw)
        ControllerState.ControllerStateAddRoll(builder, self.roll)
        ControllerState.ControllerStateAddJump(builder, self.jump)
        ControllerState.ControllerStateAddBoost(builder, self.boost)
        ControllerState.ControllerStateAddHandbrake(builder, self.handbrake)
        cs_offset = ControllerState.ControllerStateEnd(builder)
        PlayerInput.PlayerInputStart(builder)
        PlayerInput.PlayerInputAddPlayerIndex(builder, player_index)
        PlayerInput.PlayerInputAddControllerState(builder, cs_offset)
        pi_offset = PlayerInput.PlayerInputEnd(builder)
        builder.Finish(pi_offset)
        return builder


class BaseAgent(RLBotRunnable):
    # 'team' is an integer: 0 towards positive goal, 1 towards negative goal.
    # 0 is blue team, 1 is orange team
    team = None

    # 'index' is an integer: it is index at which the bot appears inside game_tick_packet.game_cars
    index = None

    # passed in by the bot manager
    __quick_chat_func = None
    __field_info_func = None
    __game_state_func = None
    __get_rigid_body_tick_func = None
    __match_settings_func = None
    renderer: RenderingManager = None
    matchcomms_root: URL = None

    def __init__(self, name, team, index):
        super().__init__(name)
        self.team = team
        self.index = index
        self.logger = get_logger(f'bot{index}')
        self.spawn_id = -1

    def get_output(self, game_tick_packet: GameTickPacket) -> SimpleControllerState:
        """
        Where all the logic of your bot gets its input and returns its output.
        :param game_tick_packet: see https://github.com/drssoccer55/RLBot/wiki/Input-and-Output-Data-(current)
        :return: [throttle, steer, pitch, yaw, roll, jump, boost, handbrake]
        """
        return SimpleControllerState()

    def send_quick_chat(self, team_only, quick_chat):
        """
        Sends a quick chat to the other bots.
        If it is QuickChats.CHAT_NONE or None it does not send a quick chat to other bots.
        :param team_only: either True or False, this says if the quick chat should only go to team members.
        :param quick_chat: The quick chat selection, available chats are defined in quick_chats.py
        """
        if quick_chat == QuickChats.CHAT_NONE or quick_chat is None:
            return
        self.__quick_chat_func(team_only, quick_chat)

    def handle_quick_chat(self, index, team, quick_chat):
        """
        Handles a quick chat from another bot.
        This will not receive any chats that this bot sends out.
        Currently does nothing, override to add functionality.
        :param index: Returns the index in the list of game cars that sent the quick chat
        :param team: Which team this player is on
        :param quick_chat: What the quick chat selection was
        """
        pass

    def get_field_info(self):
        """Gets the information about the field.
        This does not change during a match so it only needs to be called once after the everything is loaded."""
        return self.__field_info_func()

    def get_rigid_body_tick(self) -> RigidBodyTick:
        """Get the most recent state of the physics engine."""
        return self.__get_rigid_body_tick_func()

    def set_game_state(self, game_state: GameState):
        """CHEAT: Change the rocket league game to the given game_state"""
        self.__game_state_func(game_state)

    def get_ball_prediction(self):
        """DEPRECATED! Please use get_ball_prediction_struct instead, because this is going away soon!"""
        return self.__ball_prediction_func()

    def get_ball_prediction_struct(self) -> BallPrediction:
        """Fetches a prediction of where the ball will go during the next few seconds."""
        return self.__ball_prediction_struct_func()

    def get_match_settings(self) -> MatchSettings:
        """Gets the current match settings in flatbuffer format. Useful for determining map, game mode,
        mutator settings, etc."""
        return self.__match_settings_func()

    _matchcomms: Optional[MatchcommsClient] = None
    @property
    def matchcomms(self) -> MatchcommsClient:
        """
        Gets a client to send and recieve messages to other participants in the match (e.g. bots, trainer)
        """
        if self.matchcomms_root is None:
            # We had a choice here between raising the exception (fail fast) or printing a message and
            # returning None since missing matchcomms might be harmless / unused by the bot. Failing fast
            # is almost always the best policy, AND in the one case we've seen so far, returning None would
            # not have saved the situation - https://github.com/VirxEC/VirxERLU/blob/master/match_comms.py
            raise ValueError("Your bot tried to access matchcomms but matchcomms_root is None! This "
                             "may be due to manually running a bot in standalone mode without passing the "
                             "--matchcomms-url argument. That's a fine thing to do, and if it's safe to "
                             "ignore matchcomms in your case then go ahead and wrap your matchcomms access "
                             "in a try-except, or do a check first for whether matchcomms_root is None.")
        if self._matchcomms is None:
            self._matchcomms = MatchcommsClient(self.matchcomms_root)
        return self._matchcomms  # note: _matchcomms.close() is called by the bot_manager.

    def load_config(self, config_object_header):
        """
        Loads a config object this is called after the constructor but before anything else inside the bot.
        :param config_object: This is a config object that has headers, and values for custom agent configuration.
        """
        pass

    def get_extra_pids(self):
        """
        Gets the list of process ids that should be marked as high priority.
        :return: A list of process ids that are used by this bot in addition to the ones inside the python process.
        """
        return []

    def get_helper_process_request(self) -> HelperProcessRequest:
        """
        If your bot needs a helper process which can be shared, e.g. with other bots of the same type,
        you may override this to return a HelperProcessRequest.
        """
        return None

    def convert_output_to_v4(self, controller_input):
        """Converts a v3 output to a v4 controller state"""
        player_input = SimpleControllerState()
        player_input.throttle = controller_input[0]
        player_input.steer = controller_input[1]
        player_input.pitch = controller_input[2]
        player_input.yaw = controller_input[3]
        player_input.roll = controller_input[4]
        player_input.jump = controller_input[5]
        player_input.boost = controller_input[6]
        player_input.handbrake = controller_input[7]

        return player_input

    def convert_packet_to_v3(self, game_tick_packet: GameTickPacket, field_info_packet: FieldInfoPacket = None):
        """Converts the current game tick packet to v3
        :param game_tick_packet a game tick packet in the v4 struct format.
        :param field_info_packet a field info packet in the v4 struct format. Optional. If this is not supplied,
        none of the boost locations will be filled in.
        :return: A v3 version of the game tick packet"""
        return convert_to_legacy_v3(game_tick_packet, field_info_packet)

    def is_hot_reload_enabled(self):
        """
        If true, the framework will watch all your python files for modifications and instantly reload your bot
        so that the logic changes take effect. You may wish to disable this if you're concerned about performance.
        """
        return True

    ############
    #  Methods that should not be called or changed by subclasses
    ############

    def _register_quick_chat(self, quick_chat_func):
        """
        Registers the send quick chat function.
        This should not be overwritten by the agent.
        """
        self.__quick_chat_func = quick_chat_func

    def _register_field_info(self, field_info_func):
        """
        Sets the function to grab field information from the interface.
        This should not be overwritten by the agent.
        """
        self.__field_info_func = field_info_func

    def _register_get_rigid_body_tick(self, get_rigid_body_tick_func):
        self.__get_rigid_body_tick_func = get_rigid_body_tick_func

    def _register_set_game_state(self, game_state_func):
        self.__game_state_func = game_state_func

    def _register_ball_prediction(self, ball_prediction_func):
        """
        Deprecated.  __ball_prediction_struct_func will be used instead.

        Sets the function to grab ball predictions from the interface.
        This should not be overwritten by the agent.
        """
        self.__ball_prediction_func = ball_prediction_func

    def _register_ball_prediction_struct(self, ball_prediction_func):
        """
        Sets the function to grab ball predictions from the interface.
        This should not be overwritten by the agent.
        """
        self.__ball_prediction_struct_func = ball_prediction_func

    def _register_match_settings_func(self, match_settings_func):
        """
        Sets the function to grab match settings from the interface.
        This should not be overwritten by the agent.
        """
        self.__match_settings_func = match_settings_func

    def _set_renderer(self, renderer: RenderingManager):
        self.renderer = renderer

    def _set_spawn_id(self, spawn_id: int):
        self.spawn_id = spawn_id

    # Information about @classmethod: https://docs.python.org/3/library/functions.html#classmethod
    @classmethod
    def base_create_agent_configurations(cls) -> ConfigObject:
        """
        This is used when initializing agent config via builder pattern.
        It also calls `create_agent_configurations` that can be used by BaseAgent subclasses for custom configs.
        :return: Returns an instance of a ConfigObject object.
        """

        config = super().base_create_agent_configurations()
        location_config = config.get_header(LOCATIONS_HEADER)

        location_config.add_value(PYTHON_FILE_KEY, str,
                                  description="Bot's python file.\nOnly need this if RLBot controlled")
        location_config.add_value(LOOKS_CONFIG_KEY, str,
                                  description='Path to loadout config from runner')
        location_config.add_value(LOADOUT_GENERATOR_FILE_KEY, str,
                                  description="A file that provide dynamic bot loadouts (optional).")
        location_config.add_value(MAXIMUM_TICK_RATE_PREFERENCE_KEY, int, default=60,
                                  description="The maximum number of ticks per second that your bot wishes to receive.")
        location_config.add_value(SUPPORTS_STANDALONE, bool,
                                  description="True if the bot can accept args and run as a standalone process.")

        cls.create_agent_configurations(config)

        return config
