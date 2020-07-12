from rlbot.agents.base_independent_agent import BaseIndependentAgent


class BaseJavaAgent(BaseIndependentAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        raise NotImplementedError(
            f"Cannot run {name} because BaseJavaAgent is deprecated! "
            f"Please migrate to ExecutableWithSocketAgent! For more details see "
            f"https://discordapp.com/channels/348658686962696195/524345498359037972/691847014404849714")

    def run_independently(self, terminate_request_event):
        pass
