from rlbot.base_extension import BaseExtension
from rlbot.utils.logging_utils import get_logger


class SimpleExtension(BaseExtension):
    def __init__(self, setup_manager):
        super().__init__(setup_manager)
        self.logger = get_logger("SimpleExtension")

    def on_match_start(self):
        self.logger.error("MATCH HAS STARTED")

    def on_match_end(self, score, scoreboard):
        self.logger.error("SCORE IS: %s", str(score))

