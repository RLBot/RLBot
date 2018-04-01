import os
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

        self.get_agent_options()
        self.update_teams_listwidgets()



    def connect_functions(self):
        self.loadout_preset_toolbutton.clicked.connect(self.car_customisation.show)
        self.orange_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        self.blue_listwidget.itemSelectionChanged.connect(self.load_selected_bot)

    def get_agent_options(self):
        # populate dropdown
        print(os.path.dirname(__file__))
        agents_folder = os.path.join()

    def update_teams_listwidgets(self):
        self.blue_bots = []
        self.orange_bots = []
        self.blue_bot_names = []
        self.orange_bot_names = []
        for agent in self.agents:
            if agent.get_team_is_blue():
                self.blue_bots.append(agent)
                self.blue_bot_names.append(agent.__str__())
            else:
                self.orange_bots.append(agent)
                self.orange_bot_names.append(agent.__str__())

        self.blue_listwidget.clear()
        self.blue_listwidget.addItems(self.blue_bot_names)
        self.orange_listwidget.clear()
        self.orange_listwidget.addItems(self.orange_bot_names)


    def load_selected_bot(self):
        # deselect the other listbox
        if self.sender() is self.blue_listwidget:
            self.orange_listwidget.clearSelection()
        elif self.sender() is self.orange_listwidget:
            self.blue_listwidget.clearSelection()




    @staticmethod
    def main():
        app = QtWidgets.QApplication(sys.argv)
        window = RLBotQTGui()
        window.show()
        app.exec_()


    def _add_agent(self, agent):
        pass