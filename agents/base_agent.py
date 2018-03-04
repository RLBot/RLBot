from utils.custom_config import ConfigObject, ConfigHeader
from utils.structures.quick_chats import QuickChats

BOT_CONFIG_LOADOUT_HEADER = 'Bot Loadout'
BOT_CONFIG_LOADOUT_ORANGE_HEADER = 'Bot Loadout Orange'
BOT_CONFIG_MODULE_HEADER = 'Bot Location'
BOT_CONFIG_AGENT_HEADER = 'Bot Parameters'
AGENT_MODULE_KEY = 'agent_module'


class BaseAgent:
    # the name of the bot fixed for any duplicates that may occur
    name = None
    # 'team' is an integer: 0 towards positive goal, 1 towards negative goal.
    # 0 is blue team, 1 is orange team
    team = None
    # 'index' is an integer: it is index at which the bot appears inside game_tick_packet.gamecars
    index = None

    def __init__(self, name, team, index):
        self.name = name
        self.team = team
        self.index = index

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

    def get_chat_selection(self, game_tick_packet):
        """
        Where the bot will return the chat selection
        :param game_tick_packet: see https://github.com/drssoccer55/RLBot/wiki/Input-and-Output-Data-(current)
        :return: [chat_selection, team_only]
        """
        return [QuickChats.CHAT_NONE,
                QuickChats.CHAT_EVERYONE]

    def load_config(self, config_object):
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

    @staticmethod
    def create_agent_configurations():
        config = ConfigObject()
        location_config = config.add_header_name(BOT_CONFIG_MODULE_HEADER)
        location_config.add_value(AGENT_MODULE_KEY, str, default='atba',
                                  description='Path to module from runner\nOnly need this if RLBot controlled')

        config.add_header(BOT_CONFIG_LOADOUT_HEADER, BaseAgent._create_loadout())
        config.add_header(BOT_CONFIG_LOADOUT_ORANGE_HEADER, BaseAgent._create_loadout())
        return config

    @staticmethod
    def _create_loadout():
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
        header.add_value('paint_finish_1_id', int, default=1978, description='Paint Type (for first color)')
        header.add_value('paint_finish_2_id', int, default=1978, description='Paint Type (for secondary color)')
        header.add_value('engine_audio_id', int, default=0, description='Engine Audio Selection')
        header.add_value('trails_id', int, default=0, description='Car trail Selection')
        header.add_value('goal_explosion_id', int, default=1971, description='Goal Explosion Selection')

        return header

    @staticmethod
    def parse_bot_loadout(player_configuration, bot_config, loadout_header):
        player_configuration.ucTeamColorID = bot_config.getint(loadout_header, 'team_color_id')
        player_configuration.ucCustomColorID = bot_config.getint(loadout_header, 'custom_color_id')
        player_configuration.iCarID = bot_config.getint(loadout_header, 'car_id')
        player_configuration.iDecalID = bot_config.getint(loadout_header, 'decal_id')
        player_configuration.iWheelsID = bot_config.getint(loadout_header, 'wheels_id')
        player_configuration.iBoostID = bot_config.getint(loadout_header, 'boost_id')
        player_configuration.iAntennaID = bot_config.getint(loadout_header, 'antenna_id')
        player_configuration.iHatID = bot_config.getint(loadout_header, 'hat_id')
        player_configuration.iPaintFinishID = bot_config.getint(loadout_header, 'paint_finish_1_id')
        player_configuration.iCustomFinishID = bot_config.getint(loadout_header, 'paint_finish_2_id')
        player_configuration.iEngineAudioID = bot_config.getint(loadout_header, 'engine_audio_id')
        player_configuration.iTrailsID = bot_config.getint(loadout_header, 'trails_id')
        player_configuration.iGoalExplosionID = bot_config.getint(loadout_header, 'goal_explosion_id')
