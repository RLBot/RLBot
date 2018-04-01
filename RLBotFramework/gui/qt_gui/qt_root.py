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
        self.update_bot_type_combobox()
        self.connect_functions()

        self.get_agent_options()
        self.update_teams_listwidgets()



    def connect_functions(self):
        self.bot_type_combobox.currentIndexChanged.connect(self.update_bot_type_combobox)
        self.loadout_preset_toolbutton.clicked.connect(self.car_customisation.show)
        self.orange_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        self.blue_listwidget.itemSelectionChanged.connect(self.load_selected_bot)


    def update_bot_type_combobox(self):
        if self.bot_type_combobox.currentText() == 'RLBot':
            self.rlbot_frame.setHidden(False)
            self.extra_line.setHidden(False)
            self.psyonix_bot_frame.setHidden(True)
        elif self.bot_type_combobox.currentText() == 'Human':
            self.psyonix_bot_frame.setHidden(True)
            self.rlbot_frame.setHidden(True)
            self.extra_line.setHidden(True)
        elif self.bot_type_combobox.currentText() == 'Psyonix':
            self.psyonix_bot_frame.setHidden(False)
            self.rlbot_frame.setHidden(True)
            self.extra_line.setHidden(False)
        elif self.bot_type_combobox.currentText() == 'Possessed Human':
            self.psyonix_bot_frame.setHidden(True)
            self.rlbot_frame.setHidden(True)
            self.extra_line.setHidden(True)


    def get_agent_options(self):
        # populate dropdown
        print(os.path.dirname(__file__))
        # agents_folder = os.path.join()

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
        # prevent proccing from itself (clearing the other one procs this)
        if not self.sender().selectedItems():
            return
        # deselect the other listbox
        if self.sender() is self.blue_listwidget:
            self.orange_listwidget.clearSelection()
            agent_name = self.blue_listwidget.currentItem().text()
            agent_i = self.blue_listwidget.currentRow()
            agent = self.blue_bots[agent_i]
        elif self.sender() is self.orange_listwidget:
            self.blue_listwidget.clearSelection()
            agent_name = self.orange_listwidget.currentItem().text()
            agent_i = self.orange_listwidget.currentRow()
            agent = self.orange_bots[agent_i]

        # load bot config
        agent_type = agent.get_participant_type()
        print('Selected Agent:', agent, agent_name, agent_type)

        known_types = ['human', 'psyonix', 'rlbot', 'possessed_human']

        assert agent_type in known_types, 'Bot has unknown type: %s' % agent_type
        self.bot_type_combobox.setCurrentIndex(known_types.index(agent_type))
        if agent.get_team_is_blue():
            self.blue_radiobutton.setChecked(True)
        else:
            self.orange_radiobutton.setChecked(True)
        self.ign_lineedit.setText(agent_name)
        # if




    @staticmethod
    def main():
        app = QtWidgets.QApplication(sys.argv)
        window = RLBotQTGui()
        window.show()
        app.exec_()


    def _add_agent(self, agent):
        pass