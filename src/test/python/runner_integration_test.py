import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../main/python/')))
import unittest

from integration_test.training_test import TrainingTest
from integration_test.history_analysis_tests import HistoryAnalysisTest


if __name__ == '__main__':
    unittest.main()
