import unittest
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../main/python/')))

from integration_test.history_analysis_tests import HistoryAnalysisTest


if __name__ == '__main__':
    unittest.main()
