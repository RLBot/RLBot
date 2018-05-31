from rlbot.botmanager.helper_process_request import HelperProcessRequest
from rlbot.parsing.custom_config import ConfigObject, ConfigHeader
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.quick_chats import QuickChats
from rlbot.utils.rendering.rendering_manager import RenderingManager

BOT_CONFIG_LOADOUT_HEADER = 'Bot Loadout'
BOT_CONFIG_LOADOUT_ORANGE_HEADER = 'Bot Loadout Orange'
BOT_CONFIG_MODULE_HEADER = 'Locations'
BOT_CONFIG_AGENT_HEADER = 'Bot Parameters'
PYTHON_FILE_KEY = 'python_file'
LOOKS_CONFIG_KEY = 'looks_config'


class BaseAgent:
    # the name of the bot fixed for any duplicates that may occur
    name = None
    # 'team' is an integer: 0 towards positive goal, 1 towards negative goal.
    # 0 is blue team, 1 is orange team
    team = None
    # 'index' is an integer: it is index at which the bot appears inside game_tick_packet.gamecars
    index = None
    __quick_chat_func = None
    renderer = None

    def __init__(self, name, team, index):
        self.name = name
        self.team = team
        self.index = index
        self.logger = get_logger('nameless_bot')

    def get_output_vector(self, game_tick_packet):
        """
        Where all the logic of your bot gets its input and returns its output.
        :param game_tick_packet: see https://github.com/drssoccer55/RLBot/wiki/Input-and-Output-Data-(current)
        :return: [throttle, steer, pitch, yaw, roll, jump, boost, handbrake]
        """
        return [
            1.0,  # throttle
            0.0,  # steer
            0.0,  # pitch
            0.0,  # yaw
            0.0,  # roll
            0,    # jump
            0,    # boost
            0     # handbrake
        ]

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
        Currently just logs the chat, override to add functionality.
        :param index: Returns the index in the list of game cars that sent the quick chat
        :param team: Which team this player is on
        :param quick_chat: What the quick chat selection was
        """
        self.logger.debug('got quick chat from bot %s on team %s with message %s:', index, team,
                          QuickChats.quick_chat_list[quick_chat])

    def register_quick_chat(self, quick_chat_func):
        """
        Registers the send quick chat function.
        This should not be overwritten by the agent.
        """
        self.__quick_chat_func = quick_chat_func

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

    def set_renderer(self, renderer: RenderingManager):
        self.renderer = renderer

    def get_helper_process_request(self) -> HelperProcessRequest:
        """
        If your bot needs a helper process which can be shared, e.g. with other bots of the same type,
        you may override this to return a HelperProcessRequest.
        """
        return None

    @staticmethod
    def create_agent_configurations() -> ConfigObject:
        config = ConfigObject()
        location_config = config.add_header_name(BOT_CONFIG_MODULE_HEADER)
        location_config.add_value(LOOKS_CONFIG_KEY, str, default='./atba_looks.cfg',
                                  description='Path to loadout config from runner')
        location_config.add_value(PYTHON_FILE_KEY, str, default='./atba.py',
                                  description="Bot's python file.\nOnly need this if RLBot controlled")
        return config

    @staticmethod
    def create_looks_configurations() -> ConfigObject:
        config = ConfigObject()
        config.add_header(BOT_CONFIG_LOADOUT_HEADER, BaseAgent._create_loadout())
        config.add_header(BOT_CONFIG_LOADOUT_ORANGE_HEADER, BaseAgent._create_loadout())
        return config

    @staticmethod
    def _create_loadout() -> ConfigHeader:
        header = ConfigHeader()
        header.add_value('name', str, default='nameless', description='The name that will be displayed in game')
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
    def parse_bot_loadout(player_configuration, bot_config, loadout_header):
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
