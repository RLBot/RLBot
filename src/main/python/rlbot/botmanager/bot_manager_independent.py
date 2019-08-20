from rlbot.botmanager.bot_manager import BotManager


class BotManagerIndependent(BotManager):
    def __init__(self, *args, **kwargs):
        """
        See documentation on BotManager.
        """
        super().__init__(*args, **kwargs)

    def run(self):
        # Get bot module
        agent, agent_class_file = self.load_agent()
        agent.run_independently(self.terminate_request_event)
        if hasattr(agent, 'retire'):
            agent.retire()
        # If terminated, send callback
        self.termination_complete_event.set()

    def call_agent(self, agent, agent_class):
        pass

    def pull_data_from_game(self):
        pass

    def get_game_time(self):
        pass

    def prepare_for_run(self):
        pass

    def is_valid_field_info(self) -> bool:
        return True
