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

        # THIS IS VERY HACKY.
        # reimplmented the dropEvent of these listwidgets to update the lists behind the scenes.
        self.blue_listwidget.dropEvent = lambda event: self.listwidget_dropEvent(self.blue_listwidget, event)
        self.orange_listwidget.dropEvent = lambda event: self.listwidget_dropEvent(self.orange_listwidget, event)

        self.blue_bots = []
        self.orange_bots = []
        self.blue_bot_names = []
        self.orange_bot_names = []
        self.bot_names_to_agent_dict = {}

        self.car_customisation = CarCustomisation()

        self.update_bot_type_combobox()

        self.connect_functions()

        self.get_agent_options()
        self.update_teams_listwidgets()


    def listwidget_dropEvent(self, dropped_listwidget, event):
        QtWidgets.QListWidget.dropEvent(dropped_listwidget, event)
        dragged_listwidget = event.source()
        if dragged_listwidget is dropped_listwidget:
            return
        # event.pos doesnt really help as it gives the position where the drop occurred
        # (and the item usually moves up afterward)
        # print("test guess dropped bot", dropped_listwidget.itemAt(event.pos()))

        current_blue_items = [self.blue_listwidget.item(i).text() for i in range(self.blue_listwidget.count())]
        current_orange_items = [self.orange_listwidget.item(i).text() for i in range(self.orange_listwidget.count())]

        # # Note how the dragged bot appears in both lists:
        # print(current_blue_items, current_orange_items)

        dragged_bot_name = None
        for _bot_name in current_blue_items:
            if _bot_name in current_orange_items:
                dragged_bot_name = _bot_name
        assert dragged_bot_name, "Could not find overlap in dragged bot"
        print("Found dragged bot: %s. Bot placed in %s" % (dragged_bot_name, dropped_listwidget.objectName()))
        dragged_bot = self.bot_names_to_agent_dict[dragged_bot_name]
        print(dragged_bot)

        # update agent team
        if dropped_listwidget is self.blue_listwidget:
            # TODO: Create the agent set_team stuff.
            # dragged_bot.set_team(0)
            pass
        else:
            # dragged_bot.set_team(1)
            pass
        # update self.blue_bots, self.blue_bot_names and for orange.

        # update all lists according to listwidget. to allow for insertion at any position.
        # at this point, the dragged bot exists in both listwidgets for some reason.
        if dropped_listwidget is self.blue_listwidget:
            # update blue totally. update orange barring dragged_bot
            self.blue_bots = []
            self.blue_bot_names = []
            for i in range(self.blue_listwidget.count()):
                _bot_name = self.blue_listwidget.item(i).text()
                _bot_agent = self.bot_names_to_agent_dict[_bot_name]
                self.blue_bot_names.append(_bot_name)
                self.blue_bots.append(_bot_agent)

            self.orange_bots = []
            self.orange_bot_names = []
            for i in range(self.orange_listwidget.count()):
                _bot_name = self.orange_listwidget.item(i).text()
                _bot_agent = self.bot_names_to_agent_dict[_bot_name]
                if _bot_agent is not dragged_bot:
                    self.orange_bot_names.append(_bot_name)
                    self.orange_bots.append(_bot_agent)
        else:
            # update orange totally. update blue barring dragged bot
            # update blue totally. update orange barring dragged_bot
            self.orange_bots = []
            self.orange_bot_names = []
            self.blue_bots = []
            self.blue_bot_names = []
            for i in range(self.orange_listwidget.count()):
                _bot_name = self.orange_listwidget.item(i).text()
                _bot_agent = self.bot_names_to_agent_dict[_bot_name]
                self.orange_bot_names.append(_bot_name)
                self.orange_bots.append(_bot_agent)

            self.blue_bots = []
            self.blue_bot_names = []
            for i in range(self.blue_listwidget.count()):
                _bot_name = self.blue_listwidget.item(i).text()
                _bot_agent = self.bot_names_to_agent_dict[_bot_name]
                if _bot_agent is not dragged_bot:

                    self.blue_bot_names.append(_bot_name)
                    self.blue_bots.append(_bot_agent)



    def connect_functions(self):
        self.bot_type_combobox.currentIndexChanged.connect(self.update_bot_type_combobox)
        self.loadout_preset_toolbutton.clicked.connect(self.car_customisation.show)
        self.orange_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        self.blue_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        # self.blue_listwidget.keyPressEvent.connect(self.keypress_on_teams_listwidgets)

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

            self.bot_names_to_agent_dict[agent.__str__()] = agent
        self.blue_listwidget.clear()
        self.blue_listwidget.addItems(self.blue_bot_names)
        self.orange_listwidget.clear()
        self.orange_listwidget.addItems(self.orange_bot_names)


    def keypress_on_teams_listwidgets(self):
        print(self.sender())

    def load_selected_bot(self):
        # prevent proccing from itself (clearing the other one procs this)
        if not self.sender().selectedItems():
            return
        # deselect the other listbox
        if self.sender() is self.blue_listwidget:
            self.orange_listwidget.clearSelection()
            agent_name = self.blue_listwidget.currentItem().text()
            agent_i = self.blue_listwidget.currentRow()
            try:
                agent = self.blue_bots[agent_i]
            except IndexError:
                import traceback
                traceback.print_exc()
                return
        elif self.sender() is self.orange_listwidget:
            self.blue_listwidget.clearSelection()
            agent_name = self.orange_listwidget.currentItem().text()
            agent_i = self.orange_listwidget.currentRow()
            try:
                agent = self.orange_bots[agent_i]
            except IndexError:
                import traceback
                traceback.print_exc()
                return
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




    @staticmethod
    def main():
        app = QtWidgets.QApplication(sys.argv)
        window = RLBotQTGui()
        window.show()
        app.exec_()


    def _add_agent(self, agent):
        pass