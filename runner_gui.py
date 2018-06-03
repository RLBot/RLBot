import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + '/src/main/python/'))
from rlbot.gui.qt_root import RLBotQTGui

if __name__ == '__main__':
    RLBotQTGui.main()
