from integration_test.history import HistoryIO
from rlbot.utils.logging_utils import log

from integration_test.tests.blah_test import test_tick_rate, test_sufficient_data

def run_all_tests():
    log('Loading history...')
    io = HistoryIO()
    history = io.get_all_history_items()

    log("Running tests...")
    test_sufficient_data(history)
    test_tick_rate(history)

    log("================")
    log("All tests passed")
    log("================")
