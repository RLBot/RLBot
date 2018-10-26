import flatbuffers
from rlbot.botmanager.helper_process_request import HelperProcessRequest
from rlbot.parsing.custom_config import ConfigObject, ConfigHeader
from rlbot.utils import game_state_util
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.game_data_struct import GameTickPacket, FieldInfoPacket
from rlbot.utils.structures.legacy_data_v3 import convert_to_legacy_v3
from rlbot.utils.structures.quick_chats import QuickChats
from rlbot.utils.structures.rigid_body_struct import RigidBodyTick

BOT_CONFIG_LOADOUT_HEADER = 'Bot Loadout'
BOT_CONFIG_LOADOUT_ORANGE_HEADER = 'Bot Loadout Orange'
BOT_CONFIG_MODULE_HEADER = 'Locations'
BOT_CONFIG_AGENT_HEADER = 'Bot Parameters'
PYTHON_FILE_KEY = 'python_file'
LOOKS_CONFIG_KEY = 'looks_config'
BOT_NAME_KEY = "name"


class SimpleControllerState:
    """
    Building flatbuffer objects is verbose and error prone. This class provides a friendlier
    interface to bot makers.
    """

    def __init__(self):
        self.steer = 0.0
        self.throttle = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.jump = False
        self.boost = False
        self.handbrake = False


class BaseAgent:
    # the name of the bot fixed for any duplicates that may occur
    name = None

    # 'team' is an integer: 0 towards positive goal, 1 towards negative goal.
    # 0 is blue team, 1 is orange team
    team = None

    # 'index' is an integer: it is index at which the bot appears inside game_tick_packet.game_cars
    index = None

    # passed in by the bot manager
    __quick_chat_func = None

    # passed in by the bot manager
    __field_info_func = None
    __game_state_func = None
    __get_rigid_body_tick_func = None
    renderer = None

    def __init__(self, name, team, index):
        self.name = name
        self.team = team
        self.index = index
        self.logger = get_logger('nameless_bot')

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

    def set_game_state(self, game_state: game_state_util.GameState):
        builder = flatbuffers.Builder(0)
        game_state_offset = game_state.convert_to_flat(builder)
        if game_state_offset is None:
            # There are no values to be set, so just skip it
            return

        builder.Finish(game_state_offset)

        self.__game_state_func(builder)

    def get_ball_prediction(self):
        """DEPRECATED! Please use get_ball_prediction_struct instead, because this is going away soon!"""
        return self.__ball_prediction_func()

    def get_ball_prediction_struct(self) -> BallPrediction:
        """Fetches a prediction of where the ball will go during the next few seconds."""
        return self.__ball_prediction_struct_func()

    def load_config(self, config_object_header):
        """
        Loads a config object this is called after the constructor but before anything else inside the bot.
        :param config_object: This is a config object that has headers, and values for custom agent configuration.
        """
        pass

    def initialize_agent(self):
        """
        Called for all heaver initialization that needs to happen.
        The config is fully loaded at this point
        """
        pass

    def get_extra_pids(self):
        """
        Gets the list of process ids that should be marked as high priority.
        :return: A list of process ids that are used by this bot in addition to the ones inside the python process.
        """
        return []

    def retire(self):
        """Called after the game ends"""
        pass

    def get_helper_process_request(self) -> HelperProcessRequest:
        """
        If your bot needs a helper process which can be shared, e.g. with other bots of the same type,
        you may override this to return a HelperProcessRequest.
        """
        return None

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        """
        If your bot needs to add custom configurations, you may override this and use the `config` object.
        :param config: A ConfigObject instance.
        """
        pass

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


    ############
    #  Methods that should not be called or changed by subclasses
    ############

    @staticmethod
    def _create_looks_configurations() -> ConfigObject:
        config = ConfigObject()
        config.add_header(BOT_CONFIG_LOADOUT_HEADER, BaseAgent._create_loadout())
        config.add_header(BOT_CONFIG_LOADOUT_ORANGE_HEADER, BaseAgent._create_loadout())
        return config

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

    def _set_renderer(self, renderer: RenderingManager):
        self.renderer = renderer

    # Information about @classmethod: https://docs.python.org/3/library/functions.html#classmethod
    @classmethod
    def base_create_agent_configurations(cls) -> ConfigObject:
        """
        This is used when initializing agent config via builder pattern.
        It also calls `create_agent_configurations` that can be used by BaseAgent subclasses for custom configs.
        :return: Returns an instance of a ConfigObject object.
        """
        config = ConfigObject()
        location_config = config.add_header_name(BOT_CONFIG_MODULE_HEADER)
        location_config.add_value(LOOKS_CONFIG_KEY, str,
                                  description='Path to loadout config from runner')
        location_config.add_value(PYTHON_FILE_KEY, str,
                                  description="Bot's python file.\nOnly need this if RLBot controlled")
        location_config.add_value(BOT_NAME_KEY, str, default='nameless',
                                  description='The name that will be displayed in game')

        cls.create_agent_configurations(config)

        return config

    @staticmethod
    def _create_loadout() -> ConfigHeader:
        header = ConfigHeader()
        header.add_value('team_color_id', int, default=27, description='Primary Color selection')
        header.add_value('custom_color_id', int, default=75, description='Secondary Color selection')
        header.add_value('car_id', int, default=23, description='Car type (Octane, Merc, etc')
        header.add_value('decal_id', int, default=307, description='Type of decal')
        header.add_value('wheels_id', int, default=1656, description='Wheel selection')
        header.add_value('boost_id', int, default=0, description='Boost selection')
        header.add_value('antenna_id', int, default=287, description='Antenna Selection')
        header.add_value('hat_id', int, default=0, description='Hat Selection')
        header.add_value('paint_finish_id', int, default=1978, description='Paint Type (for first color)')
        header.add_value('custom_finish_id', int, default=1978, description='Paint Type (for secondary color)')
        header.add_value('engine_audio_id', int, default=0, description='Engine Audio Selection')
        header.add_value('trails_id', int, default=0, description='Car trail Selection')
        header.add_value('goal_explosion_id', int, default=1971, description='Goal Explosion Selection')

        return header

    @staticmethod
    def _parse_bot_loadout(player_configuration, bot_config, loadout_header):
        player_configuration.team_color_id = bot_config.getint(loadout_header, 'team_color_id')
        player_configuration.custom_color_id = bot_config.getint(loadout_header, 'custom_color_id')
        player_configuration.car_id = bot_config.getint(loadout_header, 'car_id')
        player_configuration.decal_id = bot_config.getint(loadout_header, 'decal_id')
        player_configuration.wheels_id = bot_config.getint(loadout_header, 'wheels_id')
        player_configuration.boost_id = bot_config.getint(loadout_header, 'boost_id')
        player_configuration.antenna_id = bot_config.getint(loadout_header, 'antenna_id')
        player_configuration.hat_id = bot_config.getint(loadout_header, 'hat_id')
        player_configuration.paint_finish_id = bot_config.getint(loadout_header, 'paint_finish_id')
        player_configuration.custom_finish_id = bot_config.getint(loadout_header, 'custom_finish_id')
        player_configuration.engine_audio_id = bot_config.getint(loadout_header, 'engine_audio_id')
        player_configuration.trails_id = bot_config.getint(loadout_header, 'trails_id')
        player_configuration.goal_explosion_id = bot_config.getint(loadout_header, 'goal_explosion_id')
