from RLBotFramework.botmanager.bot_manager import BotManager


class BotManagerFlatbuffer(BotManager):
    def __init__(self, terminate_request_event, termination_complete_event, bot_configuration, name, team, index,
                 agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder):
        """
        See documentation on BotManager.
        """
        super().__init__(terminate_request_event, termination_complete_event, bot_configuration, name, team, index,
                         agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder)
        self.game_tick_flat = None

    def call_agent(self, agent, agent_class):
        player_input = agent.get_output_flatbuffer(self.game_tick_flat)
        if not player_input:
            raise Exception('Agent "{}" did not return a player input.'.format(agent_class.__name__))

        self.game_interface.update_player_input_flat(player_input)

    def get_game_time(self):
        try:
            return self.game_tick_flat.GameInfo().SecondsElapsed()
        except AttributeError:
            return 0.0

    def pull_data_from_game(self):
        self.game_tick_flat = self.game_interface.update_live_data_flat()

    def prepare_for_run(self):
        pass