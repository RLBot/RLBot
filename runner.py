import sys
import os.path
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__) + '/src/main/python/'))
from src.main.python import runner as framework_runner

if __name__ == '__main__':
    framework_runner.main()


