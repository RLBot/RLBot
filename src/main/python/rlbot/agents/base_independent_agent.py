from rlbot.agents.base_agent import BaseAgent


class BaseIndependentAgent(BaseAgent):
    """
    Extend this class if you want to manage calling the dll yourself.
    """

    def run_independently(self, terminate_request_event):
        raise NotImplementedError

    def is_hot_reload_enabled(self):
        return False
