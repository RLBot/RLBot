import sys
import random
from typing import Optional
from urllib.parse import urlparse, ParseResult as URL

from rlbot.agents.rlbot_runnable import RLBotRunnable, LOCATIONS_HEADER
from rlbot.matchcomms.client import MatchcommsClient
from rlbot.messages.flat import MatchSettings
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.game_state_util import GameState
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.game_interface import GameInterface

SCRIPT_FILE_KEY = "script_file"

class BaseScript(RLBotRunnable):
    """
    A convenience class for building scripts on top of.
    It is NOT required to use this when configuring a script.
    """

    matchcomms_root: Optional[URL] = None

    def __init__(self, name):
        super().__init__(name)
        self.logger = get_logger(name)
        self.__key = hash("BaseScript:" + name)
        self.game_tick_packet = GameTickPacket()
        self.ball_prediction = BallPrediction()
        self.game_interface = GameInterface(self.logger)
        self.game_interface.load_interface()
        fake_index = random.randint(100, 10000)  # a number unlikely to conflict with bots or other scripts
        self.renderer = self.game_interface.renderer.get_rendering_manager(bot_index=fake_index, bot_team=2)
        # Get matchcomms root if provided as a command line argument.
        try:
            pos = sys.argv.index("--matchcomms-url")
            potential_url = urlparse(sys.argv[pos + 1])
        except (ValueError, IndexError):
            # Missing the command line argument.
            pass
        else:
            if potential_url.scheme == "ws" and potential_url.netloc:
                self.matchcomms_root = potential_url
            else:
                raise ValueError("The matchcomms url is invalid")

    def get_game_tick_packet(self):
        """Gets the latest game tick packet immediately, without blocking."""
        return self.game_interface.update_live_data_packet(self.game_tick_packet)

    def wait_game_tick_packet(self):
        """A blocking call which waits for the next new game tick packet and returns as soon
        as it's available. Will wait for a maximum of 30 milliseconds before giving up and returning
        the packet the framework already has. This is suitable for low-latency update loops."""
        return self.game_interface.fresh_live_data_packet(self.game_tick_packet, 30, self.__key)

    def get_field_info(self):
        """Gets the information about the field.
        This does not change during a match so it only needs to be called once after the everything is loaded."""
        return self.game_interface.get_field_info()

    def set_game_state(self, game_state: GameState):
        self.game_interface.set_game_state(game_state)

    def get_ball_prediction_struct(self) -> BallPrediction:
        """Fetches a prediction of where the ball will go during the next few seconds."""
        return self.game_interface.update_ball_prediction(self.ball_prediction)

    def get_match_settings(self) -> MatchSettings:
        """Gets the current match settings in flatbuffer format. Useful for determining map, game mode,
        mutator settings, etc."""
        return self.game_interface.get_match_settings()

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

        location_config.add_value(SCRIPT_FILE_KEY, str,
                                  description="Script's python file.")

        cls.create_agent_configurations(config)

        return config

    # Same as in BaseAgent.
    _matchcomms: Optional[MatchcommsClient] = None
    @property
    def matchcomms(self) -> MatchcommsClient:
        """
        Gets a client to send and recieve messages to other participants in the match (e.g. bots, trainer)
        """
        if self.matchcomms_root is None:
            raise ValueError("Your bot tried to access matchcomms but matchcomms_root is None! This "
                             "may be due to manually running a bot in standalone mode without passing the "
                             "--matchcomms-url argument. That's a fine thing to do, and if it's safe to "
                             "ignore matchcomms in your case then go ahead and wrap your matchcomms access "
                             "in a try-except, or do a check first for whether matchcomms_root is None.")
        if self._matchcomms is None:
            self._matchcomms = MatchcommsClient(self.matchcomms_root)
        return self._matchcomms
