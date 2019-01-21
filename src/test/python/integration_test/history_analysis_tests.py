import unittest

from .history import HistoryIO
from .gather_data import gather_data



class HistoryAnalysisTest(unittest.TestCase):
    """
    This test dumps the game tick packet to disk every tick,
    then anayzes it later.
    """

    @classmethod
    def setUpClass(cls):
        gather_data()
        cls.history = HistoryIO().get_all_history_items()


    def test_sufficient_data(self):
        self.assertGreater(len(self.history), 100)

    def test_tick_rate(self):
        """Checks that we're consistently running at 60 ticks/s."""
        history = self.history
        fps = 60  # I know it's not frames but I find it easier to read than tps.

        def get_time(history_item):
            return history_item.game_tick_proto.GameInfo().SecondsElapsed()

        def is_admissible(history_item):
            return history_item.game_tick_proto.GameInfo().IsRoundActive()

        intervals = [
            get_time(history[i + 1]) - get_time(history[i])
            for i in range(len(history) - 1)
            if is_admissible(history[i + 1]) and is_admissible(history[i])
        ]
        self.assertGreater(len(intervals), 10, "Didn't get enough admissible game_tick_proto's. (got {})".format(len(intervals)))

        def is_interval_acceptable(interval):
            acceptable_margin = 0.1 / fps
            return abs(interval - 1. / fps) < acceptable_margin
        acceptables = [is_interval_acceptable(interval) for interval in intervals]
        average_interval = sum(intervals) / len(intervals)
        proportion_acceptable = sum(acceptables) / len(acceptables)

        tick_rate_is_good = proportion_acceptable >= 0.98

        # print the intervals so we can plot them in a spreasheet or whatever.
        # if not tick_rate_is_good:
        #     for i in intervals:
        #         print (i)

        if not tick_rate_is_good:
            self.fail('Not running at a consistent {} fps. Only {} out of {} frames were on time ({} %). average_interval={:3f} ({:3f} fps)'.format(
                fps, sum(acceptables), len(acceptables), proportion_acceptable * 100, average_interval, 1 / average_interval
            ))

    # Note: there's a test along like  "atba should hit the ball to score" in training_test.py

