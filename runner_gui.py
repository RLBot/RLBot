import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__) + '/src/main/python/'))
from src.main.python.RLBotFramework.gui.qt_gui.qt_root import RLBotQTGui

if __name__ == '__main__':
    RLBotQTGui.main()
