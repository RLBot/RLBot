from RLBotFramework.agents.base_agent import BaseAgent

class BaseIndependentAgent(BaseAgent):
    """
    Extend this class if you want to manage calling the dll yourself.
    """

    def run_independently(self):
        raise NotImplementedError
