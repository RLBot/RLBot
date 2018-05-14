from RLBotFramework.botmanager.bot_manager import BotManager


class BotManagerProto(BotManager):
    def __init__(self, terminate_request_event, termination_complete_event, bot_configuration, name, team, index,
                 agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder):
        """
        See documentation on BotManager.
        """
        super().__init__(terminate_request_event, termination_complete_event, bot_configuration, name, team, index,
                         agent_class_wrapper, agent_metadata_queue, quick_chat_queue_holder)
        self.game_tick_proto = None

    def call_agent(self, agent, agent_class):
        controller_state = agent.get_output_proto(self.game_tick_proto)
        if not controller_state:
            raise Exception('Agent "{}" did not return a controller_state.'.format(agent_class.__name__))

        self.game_interface.update_controller_state(controller_state, self.index)

    def get_game_time(self):
        return self.game_tick_proto.game_info.seconds_elapsed

    def pull_data_from_game(self):
        self.game_tick_proto = self.game_interface.update_live_data_proto()

    def prepare_for_run(self):
        pass