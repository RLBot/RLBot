import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui

from RLBotFramework.gui.base_gui import BaseGui
from RLBotFramework.gui.qt_gui.design.qt_gui import Ui_MainWindow
from RLBotFramework.gui.qt_gui.dialogs import CarCustomisationDialog, AgentCustomisationDialog
from RLBotFramework.parsing.rlbot_config_parser import TEAM_CONFIGURATION_HEADER
from RLBotFramework.setup_manager import SetupManager
from RLBotFramework.parsing.match_settings_config_parser import *
from RLBotFramework.utils.class_importer import get_python_root

class RLBotQTGui(QtWidgets.QMainWindow, Ui_MainWindow, BaseGui):

    def __init__(self):
        super().__init__()
        BaseGui.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("images/RLBot_logo.png"))

        # THIS IS VERY HACKY.
        # reimplemented the dropEvent of these listwidgets to update the lists behind the scenes.
        self.blue_listwidget.dropEvent = lambda event: self.listwidget_dropEvent(self.blue_listwidget, event)
        self.orange_listwidget.dropEvent = lambda event: self.listwidget_dropEvent(self.orange_listwidget, event)

        self.blue_bots = []
        self.orange_bots = []
        self.blue_bot_names = []
        self.orange_bot_names = []
        self.bot_names_to_agent_dict = {}
        self.current_bot = None

        try:
            super().load_overall_config(os.path.realpath("rlbot.cfg"))
            self.statusbar.showMessage("Loaded CFG.")
        except FileNotFoundError:
            self.statusbar.showMessage("Unable to load overall config")

        self.car_customisation = CarCustomisationDialog(self)
        self.agent_customisation = AgentCustomisationDialog(self)

        self.car_customisation.update_presets_widgets()
        self.agent_customisation.update_presets_widgets()

        self.init_match_settings()
        self.update_match_settings()

        self.connect_functions()

        self.enable_disable_on_bot_select_deselect()
        self.update_bot_type_combobox()

    def listwidget_dropEvent(self, dropped_listwidget, event):
        dragged_listwidget = event.source()
        if dragged_listwidget is dropped_listwidget:
            # do not do dropping into same listwidget.
            return
        QtWidgets.QListWidget.dropEvent(dropped_listwidget, event)

        current_blue_items = [self.blue_listwidget.item(i).text() for i in range(self.blue_listwidget.count())]
        current_orange_items = [self.orange_listwidget.item(i).text() for i in range(self.orange_listwidget.count())]

        dragged_bot_name = None
        for _bot_name in current_blue_items:
            if _bot_name in current_orange_items:
                dragged_bot_name = _bot_name
        assert dragged_bot_name, "Could not find overlap in dragged bot"
        print("Found dragged bot: %s. Bot placed in %s" % (dragged_bot_name, dropped_listwidget.objectName()))
        dragged_bot = self.bot_names_to_agent_dict[dragged_bot_name]
        old_team_index = dragged_listwidget is self.orange_listwidget
        self.switch_team_bot(old_team_index, dragged_bot)

    def move_bot_between_list(self, old_team_index):
        if not old_team_index:
            from_list = self.blue_listwidget
            to_list = self.orange_listwidget
        else:
            from_list = self.orange_listwidget
            to_list = self.blue_listwidget
        item = from_list.takeItem(from_list.row(from_list.selectedItems()[0]))
        to_list.addItem(item)
        return item

    def switch_team_bot(self, team_index, bot):
        # update agent team
        if team_index:
            bot.set_team(0)
        else:
            bot.set_team(1)
        # update self.blue_bots, self.blue_bot_names and for orange.

        # update all lists according to listwidget. to allow for insertion at any position.
        # at this point, the dragged bot exists in both listwidgets for some reason.
        if team_index:
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
                if _bot_agent is not bot:
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
                if _bot_agent is not bot:
                    self.blue_bot_names.append(_bot_name)
                    self.blue_bots.append(_bot_agent)

    def init_match_settings(self):
        self.mode_type_combobox.addItems(game_mode_types)
        self.map_type_combobox.addItems(map_types)
        self.match_length_combobox.addItems(match_length_types)
        self.boost_type_combobox.addItems(boost_types)

    def update_match_settings(self):
        self.mode_type_combobox.setCurrentText(self.overall_config.get(MATCH_CONFIGURATION_HEADER, GAME_MODE))
        self.map_type_combobox.setCurrentText(self.overall_config.get(MATCH_CONFIGURATION_HEADER, GAME_MAP))
        self.skip_replays_checkbox.setChecked(self.overall_config.getboolean(MATCH_CONFIGURATION_HEADER, SKIP_REPLAYS))
        self.instant_start_checkbox.setChecked(self.overall_config.getboolean(MATCH_CONFIGURATION_HEADER, INSTANT_START))
        self.match_length_combobox.setCurrentText(self.overall_config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_MATCH_LENGTH))
        self.boost_type_combobox.setCurrentText(self.overall_config.get(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BOOST_AMOUNT))

    def connect_functions(self):
        self.bot_type_combobox.currentIndexChanged.connect(self.update_bot_type_combobox)
        self.loadout_preset_toolbutton.clicked.connect(self.car_customisation.popup)
        self.agent_preset_toolbutton.clicked.connect(self.agent_customisation.popup)
        self.orange_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        self.blue_listwidget.itemSelectionChanged.connect(self.load_selected_bot)

        self.cfg_load_pushbutton.clicked.connect(lambda e: self.load_overall_config())
        self.cfg_save_pushbutton.clicked.connect(lambda e: self.save_overall_config(0))

        self.blue_plus_toolbutton.clicked.connect(lambda: self.gui_add_bot(team_index=0))
        self.orange_plus_toolbutton.clicked.connect(lambda: self.gui_add_bot(team_index=1))

        self.blue_minus_toolbutton.clicked.connect(lambda: self.gui_remove_bot(team_index=0))
        self.orange_minus_toolbutton.clicked.connect(lambda: self.gui_remove_bot(team_index=1))

        self.run_button.clicked.connect(lambda e: self.start_match())

        widgets = [self.cfg_file_path_lineedit, self.ign_lineedit, self.bot_level_slider,
                   self.blue_radiobutton, self.orange_radiobutton,
                   self.blue_name_lineedit, self.blue_color_spinbox,
                   self.orange_name_lineedit, self.orange_color_spinbox,
                   self.loadout_preset_combobox, self.agent_preset_combobox,
                   self.mode_type_combobox, self.map_type_combobox, self.skip_replays_checkbox,
                   self.instant_start_checkbox, self.match_length_combobox, self.boost_type_combobox]

        for item in widgets:
            if isinstance(item, QtWidgets.QLineEdit):
                item.editingFinished.connect(self.edit_event)
            elif isinstance(item, QtWidgets.QSlider):
                item.sliderMoved.connect(self.edit_event)
            elif isinstance(item, QtWidgets.QAbstractSpinBox):
                item.valueChanged.connect(self.edit_event)
            elif isinstance(item, QtWidgets.QRadioButton):
                item.toggled.connect(self.edit_event)
            elif isinstance(item, QtWidgets.QCheckBox):
                item.toggled.connect(self.edit_event)
            elif isinstance(item, QtWidgets.QComboBox):
                item.currentTextChanged.connect(self.edit_event)

    def save_overall_config(self, time_out=5000):
        super().save_overall_config(time_out)
        self.cfg_file_path_lineedit.setText(self.overall_config_path)

    def edit_event(self, value=None):
        def auto_save():
            pass  # disabling the auto_save for now, takes too much time to fix
            # if self.cfg_autosave_checkbox.isChecked():
            #     self.save_overall_config(time_out=5000)

        s = self.sender()
        if isinstance(s, QtWidgets.QLineEdit):
            value = s.text()

        agent = self.current_bot
        if s is self.cfg_file_path_lineedit:
            if not os.path.exists(value):
                self.cfg_file_path_lineedit.setText(self.overall_config_path)
            else:
                self.load_overall_config(value)

        elif s is self.blue_name_lineedit or s is self.orange_name_lineedit:
            team = "Blue" if s is self.blue_name_lineedit else "Orange"
            self.overall_config.set_value(TEAM_CONFIGURATION_HEADER, "Team " + team + " Name", value)
            auto_save()
        elif s is self.blue_color_spinbox or s is self.orange_color_spinbox:
            team = "Blue" if s is self.blue_color_spinbox else "Orange"
            self.overall_config.set_value(TEAM_CONFIGURATION_HEADER, "Team " + team + " Color", value)
            auto_save()

        elif s is self.ign_lineedit:
            if not self.current_bot.get_team():
                listwidget = self.blue_listwidget
            else:
                listwidget = self.orange_listwidget
            if not listwidget.selectedItems():  # happens when you 'finish editing' by click delete [-]
                return
            name = self.validate_name(value, agent)
            old_name = self.validate_name(agent.ingame_name, agent)
            listwidget.selectedItems()[0].setText(name)
            del self.bot_names_to_agent_dict[old_name]
            agent.set_name(value)
            self.bot_names_to_agent_dict[name] = agent
            self.update_bot_names_listwidgets()

        elif s is self.bot_level_slider:
            agent.set_bot_skill(value / 100)

        elif s is self.blue_radiobutton and value:  # 'and value' check to make sure that one got selected
            if agent.get_team() == 1:
                item = self.move_bot_between_list(1)
                self.switch_team_bot(1, agent)
                self.blue_listwidget.setCurrentItem(item)

        elif s is self.orange_radiobutton and value:
            if agent.get_team() == 0:
                item = self.move_bot_between_list(0)
                self.switch_team_bot(0, agent)
                self.orange_listwidget.setCurrentItem(item)

        elif s is self.loadout_preset_combobox:
            if value and self.bot_config_groupbox.isEnabled() and self.current_bot is not None:
                self.current_bot.set_loadout_preset(self.loadout_presets[value])
        elif s is self.agent_preset_combobox:
            if value and self.bot_config_groupbox.isEnabled() and self.current_bot is not None:
                self.current_bot.set_agent_preset(self.agent_presets[value])

        elif s is self.mode_type_combobox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, GAME_MODE, value)
        elif s is self.map_type_combobox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, GAME_MAP, value)
        elif s is self.skip_replays_checkbox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, SKIP_REPLAYS, value)
        elif s is self.instant_start_checkbox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, INSTANT_START, value)
        elif s is self.match_length_combobox:
            self.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, MUTATOR_MATCH_LENGTH, value)
        elif s is self.boost_type_combobox:
            self.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BOOST_AMOUNT, value)

    def validate_name(self, name, agent):
        if name in self.bot_names_to_agent_dict and self.bot_names_to_agent_dict[name] is not agent:
            i = 0
            while True:
                if name + " (" + str(i) + ")" in self.bot_names_to_agent_dict and \
                        self.bot_names_to_agent_dict[name + " (" + str(i) + ")"] is not agent:
                    i += 1
                else:
                    value = name + " (" + str(i) + ")"
                    return value
        else:
            return name

    def update_overall_config_stuff(self):
        self.update_teams_listwidgets()
        self.cfg_file_path_lineedit.setText(self.overall_config_path)

    def update_bot_type_combobox(self):
        if not self.bot_config_groupbox.isEnabled():
            # same as below except no self.current_bot
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
        else:
            if self.bot_type_combobox.currentText() == 'RLBot':
                self.rlbot_frame.setHidden(False)
                self.extra_line.setHidden(False)
                self.psyonix_bot_frame.setHidden(True)
                self.current_bot.set_participant_type("rlbot")
            elif self.bot_type_combobox.currentText() == 'Human':
                self.psyonix_bot_frame.setHidden(True)
                self.rlbot_frame.setHidden(True)
                self.extra_line.setHidden(True)
                self.current_bot.set_participant_type("human")
            elif self.bot_type_combobox.currentText() == 'Psyonix':
                self.psyonix_bot_frame.setHidden(False)
                self.rlbot_frame.setHidden(True)
                self.extra_line.setHidden(False)
                self.current_bot.set_participant_type("psyonix")
            elif self.bot_type_combobox.currentText() == 'Possessed Human':
                self.psyonix_bot_frame.setHidden(True)
                self.rlbot_frame.setHidden(True)
                self.extra_line.setHidden(True)
                self.current_bot.set_participant_type("party_member_bot")

    def enable_disable_on_bot_select_deselect(self):
        # if no bot selected, disable botconfig groupbox and minus buttons
        if not self.blue_listwidget.selectedItems() and not self.orange_listwidget.selectedItems():
            self.bot_config_groupbox.setDisabled(True)
            self.blue_minus_toolbutton.setDisabled(True)
            self.orange_minus_toolbutton.setDisabled(True)
            return
        else:
            self.bot_config_groupbox.setDisabled(False)

    def update_bot_names_listwidgets(self):
        for agent_name, agent in self.bot_names_to_agent_dict.items():
            list_name = self.validate_name(agent.ingame_name, agent)
            if agent_name != list_name:
                del self.bot_names_to_agent_dict[agent_name]
                self.bot_names_to_agent_dict[list_name] = agent
                list_widget = self.blue_listwidget if not agent.get_team() else self.orange_listwidget
                list_widget.findItems(agent_name, QtCore.Qt.MatchExactly)[0].setText(list_name)

    def update_teams_listwidgets(self):
        self.blue_bots.clear()
        self.orange_bots.clear()
        self.blue_bot_names.clear()
        self.orange_bot_names.clear()
        self.bot_names_to_agent_dict.clear()
        for agent in self.agents:
            name = self.validate_name(agent.ingame_name, agent)
            if not agent.get_team():
                self.blue_bots.append(agent)
                self.blue_bot_names.append(name)
            else:
                self.orange_bots.append(agent)
                self.orange_bot_names.append(name)

            self.bot_names_to_agent_dict[name] = agent
        self.blue_listwidget.clear()
        self.blue_listwidget.addItems(self.blue_bot_names)
        self.orange_listwidget.clear()
        self.orange_listwidget.addItems(self.orange_bot_names)

        self.enable_disable_on_bot_select_deselect()

        # if max bot count reached: disable + button
        if not self.index_manager.has_free_slots():
            self.blue_plus_toolbutton.setDisabled(True)
            self.orange_plus_toolbutton.setDisabled(True)
        else:
            self.blue_plus_toolbutton.setDisabled(False)
            self.orange_plus_toolbutton.setDisabled(False)

    def load_overall_config(self, config_path=None):
        super().load_overall_config(config_path)
        self.car_customisation.update_presets_widgets()
        self.agent_customisation.update_presets_widgets()

    def load_selected_bot(self):
        # prevent proccing from itself (clearing the other one procs this)
        if not self.sender().selectedItems():
            return
        # deselect the other listbox
        item_name = self.sender().selectedItems()[0].text()
        agent = self.get_selected_bot(self.sender())
        if agent is None:
            return
        if self.current_bot == agent:
            return
        else:
            self.current_bot = agent

        # enable/disable bot config (and maybe [+])
        self.enable_disable_on_bot_select_deselect()
        # enable [-] for right listwidget
        if self.sender() is self.blue_listwidget:
            self.blue_minus_toolbutton.setDisabled(False)
            self.orange_minus_toolbutton.setDisabled(True)
        elif self.sender() is self.orange_listwidget:
            self.orange_minus_toolbutton.setDisabled(False)
            self.blue_minus_toolbutton.setDisabled(True)

        # load bot config
        agent_type = agent.get_participant_type()
        # print('Selected Agent: %s\t\t(Type: %s)' % (agent, agent_type))

        known_types = ['human', 'psyonix', 'rlbot', 'party_member_bot']
        assert agent_type in known_types, 'Bot has unknown type: %s' % agent_type

        self.bot_type_combobox.setCurrentIndex(known_types.index(agent_type))
        if not agent.get_team():
            self.blue_radiobutton.setChecked(True)
        else:
            self.orange_radiobutton.setChecked(True)
        self.ign_lineedit.setText(agent.ingame_name)

        self.loadout_preset_combobox.setCurrentText(agent.get_loadout_preset().get_name())
        self.agent_preset_combobox.setCurrentText(agent.get_agent_preset().get_name())

        self.statusbar.showMessage("Selected bot '%s' with ingame name '%s'" % (agent.get_name(), item_name), 2000)

    def get_selected_bot(self, sender: QtWidgets.QListWidget, print_err=True):
        if sender is self.blue_listwidget:
            bots_list = self.blue_bots
            self.orange_listwidget.clearSelection()
        elif sender is self.orange_listwidget:
            bots_list = self.orange_bots
            self.blue_listwidget.clearSelection()
        agent_i = sender.currentRow()
        try:
            agent = bots_list[agent_i]
        except IndexError:
            if print_err:
                print("\nI am printing this error manually. It can be hidden easily:")
                import traceback
                traceback.print_exc()
            return

        return agent

    def gui_add_bot(self, team_index):
        agent = self.load_agent()
        if agent is None:
            # All 10 agent slots filled already
            self.statusbar.showMessage("Could not add bot, already ten bots", 5000)
        else:
            agent.set_team(team_index)
            bot_name = self.validate_name(agent.get_name(), agent)
            self.bot_names_to_agent_dict[bot_name] = agent
            self.update_teams_listwidgets()
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, PARTICIPANT_COUNT_KEY, self.agents.__len__())
            self.statusbar.showMessage('Added bot: %s.' % agent, 5000)

    def gui_remove_bot(self, team_index):
        if not team_index:
            listwidget = self.blue_listwidget
        else:
            listwidget = self.orange_listwidget
        agent = self.get_selected_bot(listwidget)
        self.remove_agent(agent)
        self.update_teams_listwidgets()
        self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, PARTICIPANT_COUNT_KEY, self.agents.__len__())
        self.statusbar.showMessage('Deleted bot: %s.' % agent, 5000)

    def show_status_message(self, message):
        self.statusbar.showMessage(message)

    def start_match(self):
        agent_configs = []
        loadout_configs = []
        for agent in self.agents:
            i, agent_config, loadout_config = agent.get_configs()
            agent_configs.insert(i, agent_config)
            loadout_configs.insert(i, loadout_config)
        manager = SetupManager()
        manager.startup()
        manager.load_config(self.overall_config, self.overall_config_path, agent_configs, loadout_configs)
        manager.launch_bot_processes()
        manager.run()
        manager.shut_down()



    @staticmethod
    def main():
        app = QtWidgets.QApplication(sys.argv)
        window = RLBotQTGui()
        window.show()
        app.exec_()

