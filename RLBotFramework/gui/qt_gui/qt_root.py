import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from RLBotFramework.gui.base_gui import BaseGui
from RLBotFramework.gui.base_gui_agent import BaseGuiAgent

from RLBotFramework.gui.qt_gui.qt_gui import Ui_MainWindow
from RLBotFramework.gui.qt_gui.car_customisation import Ui_Form


class CarCustomisation(QtWidgets.QDialog, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class RLBotQTGui(QtWidgets.QMainWindow, Ui_MainWindow, BaseGui):

    def __init__(self):
        super().__init__()
        BaseGui.__init__(self)
        self.setupUi(self)
        self.car_customisation = CarCustomisation()
        self.connect_functions()
        self.update_teams_listwidgets()

    def connect_functions(self):
        self.loadout_preset_toolbutton.clicked.connect(self.car_customisation.show)


    def update_teams_listwidgets(self):
        for agent in self.agents:
            print(agent.get_team_is_blue())

    @staticmethod
    def main():
        app = QtWidgets.QApplication(sys.argv)
        window = RLBotQTGui()
        window.show()
        app.exec_()


    def _add_agent(self, agent):
        pass