import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from RLBotFramework.gui.base_gui import BaseGui
from RLBotFramework.gui.base_gui_agent import BaseGuiAgent

from RLBotFramework.gui.qt_gui.qt_gui import Ui_MainWindow
from RLBotFramework.gui.qt_gui.car_customisation import Ui_Form


class CarCustomisationDialog(QtWidgets.QDialog, Ui_Form):
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
        self.current_bot = None

        self.car_customisation = CarCustomisationDialog()

        self.update_bot_type_combobox()

        self.connect_functions()

        self.get_agent_options()
        self.update_teams_listwidgets()
        self.load_selected_bot()

        self.statusbar.showMessage("Saved CFG.")
        print(self.cfg_file_path_lineedit.text(), type(self.cfg_file_path_lineedit.text()))
        # self.lineEdit.setText("asfasfasfasf *")
        # myFont = QtGui.QFont()
        # myFont.setItalic(True)
        # self.lineEdit.setFont(myFont)

    def listwidget_dropEvent(self, dropped_listwidget, event):
        dragged_listwidget = event.source()
        if dragged_listwidget is dropped_listwidget:
            # do not do dropping into same listwidget.
            return
        print('dropping')
        QtWidgets.QListWidget.dropEvent(dropped_listwidget, event)
        print('dropped')

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
        self.cfg_file_path_lineedit.textEdited.connect(self.textstuff)

    def textstuff(self):
        print(self.sender())

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

    def load_selected_bot(self):
        # if no bot selected, disable botconfig groupbox
        if not self.blue_listwidget.selectedItems() and not self.orange_listwidget.selectedItems():
            self.bot_config_groupbox.setDisabled(True)
            return
        else:
            self.bot_config_groupbox.setDisabled(False)

        # prevent proccing from itself (clearing the other one procs this)
        if not self.sender().selectedItems():
            return
        # deselect the other listbox
        bot_stuff = self.get_selected_bot(self.sender())
        if bot_stuff:
            agent, agent_name = bot_stuff
        else:
            return
        if self.current_bot == agent:
            return
        else:
            self.current_bot = agent

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

    def get_selected_bot(self, sender: QtWidgets.QListWidget):
        if sender is self.blue_listwidget:
            bots_list = self.blue_bots
            self.orange_listwidget.clearSelection()
        elif sender is self.orange_listwidget:
            bots_list = self.orange_bots
            self.blue_listwidget.clearSelection()

        agent_name = sender.currentItem().text()
        agent_i = sender.currentRow()
        try:
            agent = bots_list[agent_i]
        except IndexError:
            print("\nI am printing this error manually. It can be hidden easily:")
            import traceback
            traceback.print_exc()
            return
        for _i in range(sender.count()):
            if _i != agent_i:
                sender.item(_i).setSelected(False)

        return agent, agent_name


    @staticmethod
    def main():
        app = QtWidgets.QApplication(sys.argv)
        window = RLBotQTGui()
        window.show()
        app.exec_()

    def _add_agent(self, agent):
        pass
