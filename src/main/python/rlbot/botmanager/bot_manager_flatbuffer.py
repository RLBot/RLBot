from rlbot.botmanager.bot_manager import BotManager
from rlbot.messages.flat import GameTickPacket


class BotManagerFlatbuffer(BotManager):
    def __init__(self, *args, **kwargs):
        """
        See documentation on BotManager.
        """
        super().__init__(*args, **kwargs)
        self.game_tick_flat = None
        self.game_tick_flat_binary = None

    def call_agent(self, agent, agent_class):
        if hasattr(agent, "set_flatbuffer_binary"):
            # This is useful for recording data in a file.
            agent.set_flatbuffer_binary(self.game_tick_flat_binary)
        player_input = agent.get_output_flatbuffer(self.game_tick_flat)
        if not player_input:
            raise Exception(f'Agent "{agent_class.__name__}" did not return a player input.')

        self.game_interface.update_player_input_flat(player_input)

    def get_game_time(self):
        try:
            return self.game_tick_flat.GameInfo().SecondsElapsed()
        except AttributeError:
            return 0.0

    def pull_data_from_game(self):
        # Set a timeout of 30 milliseconds. It's slightly less than the number of milliseconds (33.33)
        # caused by MAX_AGENT_CALL_PERIOD defined in bot_manager.py
        self.game_tick_flat_binary = self.game_interface.get_fresh_live_data_flat_binary(30, self.index)
        if self.game_tick_flat_binary is not None:
            self.game_tick_flat = GameTickPacket.GameTickPacket.GetRootAsGameTickPacket(self.game_tick_flat_binary, 0)

    def prepare_for_run(self):
        pass

    def get_spawn_id(self):
        try:
            return self.game_tick_flat.Players(self.index).SpawnId()
        except:
            return None
