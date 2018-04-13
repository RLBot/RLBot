import os
import sys
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QWidget, QComboBox, QLineEdit, QRadioButton, QSlider, QCheckBox

from RLBotFramework.gui.presets import AgentPreset, LoadoutPreset
from RLBotFramework.gui.index_manager import IndexManager
from RLBotFramework.gui.design.qt_gui import Ui_MainWindow
from RLBotFramework.gui.gui_agent import Agent
from RLBotFramework.gui.preset_editors import CarCustomisationDialog, AgentCustomisationDialog

from RLBotFramework.utils.class_importer import get_python_root
from RLBotFramework.agents.base_agent import BOT_CONFIG_MODULE_HEADER
from RLBotFramework.setup_manager import SetupManager, DEFAULT_RLBOT_CONFIG_LOCATION

from RLBotFramework.parsing.rlbot_config_parser import create_bot_config_layout, get_num_players, TEAM_CONFIGURATION_HEADER
from RLBotFramework.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY, LOOKS_CONFIG_KEY
from RLBotFramework.parsing.match_settings_config_parser import *


class RLBotQTGui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.overall_config = None
        self.index_manager = IndexManager(10)

        self.agents = []
        self.agent_presets = {}
        self.bot_names_to_agent_dict = {}
        self.loadout_presets = {}
        self.current_bot = None
        self.overall_config_timer = None

        self.car_customisation = CarCustomisationDialog(self)
        self.agent_customisation = AgentCustomisationDialog(self)

        self.load_overall_config(DEFAULT_RLBOT_CONFIG_LOCATION)

        self.init_match_settings()
        self.update_match_settings()

        self.connect_functions()
        self.update_bot_type_combobox()

    def start_match(self):
        """
        Starts a match with the current configuration
        :return:
        """
        # TODO hook this up to the SetupManager and actually run the match

    def connect_functions(self):
        """
        Connects all events to the functions which should be called
        :return:
        """
        self.cfg_load_pushbutton.clicked.connect(lambda: self.load_overall_config())  # Lambda because it is going to pass the event parameter otherwise
        self.cfg_save_pushbutton.clicked.connect(lambda: self.save_overall_config())  # Same story here

        self.blue_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        self.orange_listwidget.itemSelectionChanged.connect(self.load_selected_bot)

        self.blue_name_lineedit.editingFinished.connect(self.team_settings_edit_event)
        self.orange_name_lineedit.editingFinished.connect(self.team_settings_edit_event)
        self.blue_color_spinbox.valueChanged.connect(self.team_settings_edit_event)
        self.orange_color_spinbox.valueChanged.connect(self.team_settings_edit_event)

        self.blue_minus_toolbutton.clicked.connect(lambda e: self.remove_agent(self.current_bot))
        self.orange_minus_toolbutton.clicked.connect(lambda e: self.remove_agent(self.current_bot))
        self.blue_plus_toolbutton.clicked.connect(lambda e: self.add_agent(team_index=0))
        self.orange_plus_toolbutton.clicked.connect(lambda e: self.add_agent(team_index=1))

        for child in self.bot_config_groupbox.findChildren(QWidget):
            if isinstance(child, QLineEdit):
                child.editingFinished.connect(self.bot_config_edit_event)
            elif isinstance(child, QSlider):
                child.sliderMoved.connect(self.bot_config_edit_event)
            elif isinstance(child, QRadioButton):
                child.toggled.connect(self.bot_config_edit_event)
            elif isinstance(child, QComboBox):
                child.currentTextChanged.connect(self.bot_config_edit_event)
        self.loadout_preset_toolbutton.clicked.connect(self.car_customisation.popup)
        self.agent_preset_toolbutton.clicked.connect(self.agent_customisation.popup)

        for child in self.match_settings_groupbox.findChildren(QWidget):
            if isinstance(child, QComboBox):
                child.currentTextChanged.connect(self.match_settings_edit_event)
            elif isinstance(child, QCheckBox):
                child.toggled.connect(self.match_settings_edit_event)

        self.run_button.clicked.connect(self.start_match)

    def bot_config_edit_event(self, value=None):
        """
        Handles the events called when editing a value regarding the bot configuration
        :param value: the new value to store in the config
        :return:
        """
        sender = self.sender()
        if value is None:
            value = sender.text()
        agent = self.current_bot

        if sender is self.bot_type_combobox:
            self.update_bot_type_combobox()

        elif sender is self.blue_radiobutton and value:  # 'and value' check to make sure that one got selected
            if agent.get_team() != 0:
                agent.set_team(0)
                self.update_teams_listwidgets()
                self.blue_listwidget.setCurrentItem(self.blue_listwidget.findItems(self.validate_name(agent.get_name(), agent), QtCore.Qt.MatchExactly)[0])

        elif sender is self.orange_radiobutton and value:
            if agent.get_team() != 1:
                agent.set_team(1)
                self.update_teams_listwidgets()
                self.orange_listwidget.setCurrentItem(self.orange_listwidget.findItems(self.validate_name(agent.get_name(), agent), QtCore.Qt.MatchExactly)[0])

        elif sender is self.ign_lineedit:
            if not agent.get_team():
                listwidget = self.blue_listwidget
            else:
                listwidget = self.orange_listwidget
            # if not listwidget.selectedItems():  # happens when you 'finish editing' by click delete [-]
            #     return
            # TODO catch the real [-]
            name = self.validate_name(value, agent)
            old_name = self.validate_name(agent.ingame_name, agent)
            listwidget.findItems(old_name, QtCore.Qt.MatchExactly)[0].setText(name)
            del self.bot_names_to_agent_dict[old_name]
            agent.set_name(value)
            self.bot_names_to_agent_dict[name] = agent
        elif sender is self.loadout_preset_combobox:
            pass
        elif sender is self.agent_preset_combobox:
            pass
        elif sender is self.bot_level_slider:
            agent.set_bot_skill(value / 100)

    def update_bot_type_combobox(self):
        """
        Handles selecting another bot type in the combobox, hides some frames and shows others depending on the setting
        Also saves the new type if there is a bot selected
        :return:
        """
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
        if self.bot_config_groupbox.isEnabled():
            if self.bot_type_combobox.currentText() == 'RLBot':
                self.current_bot.set_participant_type("rlbot")
            elif self.bot_type_combobox.currentText() == 'Human':
                self.current_bot.set_participant_type("human")
            elif self.bot_type_combobox.currentText() == 'Psyonix':
                self.current_bot.set_participant_type("psyonix")
            elif self.bot_type_combobox.currentText() == 'Possessed Human':
                self.current_bot.set_participant_type("party_member_bot")

    def team_settings_edit_event(self, value=None):
        """
        Handles the events when editing a value regarding the team settings
        :param value: the new value to store in the config
        :return:
        """
        sender = self.sender()
        if value is None:
            value = sender.text()

        if sender is self.blue_name_lineedit:
                self.overall_config.set_value(TEAM_CONFIGURATION_HEADER, "Team Blue Name", value)
        elif sender is self.orange_name_lineedit:
            self.overall_config.set_value(TEAM_CONFIGURATION_HEADER, "Team Orange Name", value)
        elif sender is self.blue_color_spinbox:
            self.overall_config.set_value(TEAM_CONFIGURATION_HEADER, "Team Blue Color", value)
        elif sender is self.orange_color_spinbox:
            self.overall_config.set_value(TEAM_CONFIGURATION_HEADER, "Team Orange Color", value)

    def update_team_settings(self):
        self.blue_name_lineedit.setText(self.overall_config.get(TEAM_CONFIGURATION_HEADER, "Team Blue Name"))
        self.orange_name_lineedit.setText(self.overall_config.get(TEAM_CONFIGURATION_HEADER, "Team Orange Name"))
        self.blue_color_spinbox.setValue(self.overall_config.getint(TEAM_CONFIGURATION_HEADER, "Team Blue Color"))
        self.orange_color_spinbox.setValue(self.overall_config.getint(TEAM_CONFIGURATION_HEADER, "Team Orange Color"))

    def load_overall_config(self, config_path=None):
        """
        Loads the overall config from the config path, or asks for a path if config_path is None
        :param config_path: the path to load the overall_config from, if None a path is requested
        :return:
        """
        if self.overall_config is None:
            self.overall_config = create_bot_config_layout()
        Agent.overall_config = self.overall_config
        if config_path is None:
            config_path = QFileDialog.getOpenFileName(self, "Load Overall Config", "", "Config Files (*.cfg)")[0]
            if not config_path:
                self.statusbar.showMessage("No file selected, not loading config", 5000)
                return
        if not os.path.isfile(config_path):
            raise FileNotFoundError("The file " + config_path + " does not exist, not loading config")
        self.overall_config_path = config_path
        self.overall_config.parse_file(config_path, 10)
        self.load_agents()
        self.update_teams_listwidgets()
        self.cfg_file_path_lineedit.setText(self.overall_config_path)
        self.update_team_settings()
        self.car_customisation.update_presets_widgets()
        self.agent_customisation.update_presets_widgets()

    def save_overall_config(self, time_out=0):
        """
        Schedules a save after given time_out
        :param time_out: The amound of milliseconds it should wait before saving
        :return:
        """
        # TODO make sure the preset paths also save/always get updated, also make sure the order is correct
        def save():
            if not os.path.exists(self.overall_config_path):
                return
            with open(self.overall_config_path, "w") as f:
                f.write(str(self.overall_config))
        if self.overall_config_timer is None:
            self.overall_config_timer = QTimer()
            self.overall_config_timer.setSingleShot(True)
            self.overall_config_timer.timeout.connect(save)
        save_path = self.overall_config_path
        if save_path is None or not os.path.exists(save_path):
            save_path = QFileDialog.getSaveFileName(self, "Save Overall Config", "", "Config Files (*.cfg)")[0]
            if not save_path:
                self.statusbar.showMessage("Unable to save a config without location", 5000)
                return
            self.overall_config_path = save_path
        self.overall_config_timer.start(time_out)

    def load_selected_bot(self):
        # prevent proccing from itself (clearing the other one processes this)
        if not self.sender().selectedItems():
            return

        blue = True if self.sender() is self.blue_listwidget else False

        if blue:  # deselect the other listbox
            self.orange_listwidget.clearSelection()
        else:
            self.blue_listwidget.clearSelection()
        item_name = self.sender().selectedItems()[0].text()
        agent = self.bot_names_to_agent_dict[item_name]
        if agent is None:  # something went wrong if agent is None
            return

        self.current_bot = agent

        self.bot_config_groupbox.setEnabled(True)  # Make sure that you can edit the bot
        # enable [-] for right listwidget
        if blue:
            self.blue_minus_toolbutton.setDisabled(False)
            self.orange_minus_toolbutton.setDisabled(True)
        else:
            self.orange_minus_toolbutton.setDisabled(False)
            self.blue_minus_toolbutton.setDisabled(True)

        # load the bot parameters into the edit frame
        agent_type = agent.get_participant_type()

        known_types = ['human', 'psyonix', 'rlbot', 'party_member_bot']
        assert agent_type in known_types, 'Bot has unknown type: %s' % agent_type

        self.bot_type_combobox.setCurrentIndex(known_types.index(agent_type))
        if blue:
            self.blue_radiobutton.setChecked(True)
        else:
            self.orange_radiobutton.setChecked(True)
        self.ign_lineedit.setText(agent.ingame_name)
        self.loadout_preset_combobox.setCurrentText(agent.get_loadout_preset().get_name())
        self.agent_preset_combobox.setCurrentText(agent.get_agent_preset().get_name())

    def update_teams_listwidgets(self):
        self.bot_names_to_agent_dict.clear()
        self.blue_listwidget.clear()
        self.orange_listwidget.clear()
        for agent in self.agents:
            name = self.validate_name(agent.ingame_name, agent)
            if not agent.get_team():
                self.blue_listwidget.addItem(name)
            else:
                self.orange_listwidget.addItem(name)

            self.bot_names_to_agent_dict[name] = agent

        self.enable_disable_on_bot_select_deselect()

        # if max bot count reached: disable + button
        if not self.index_manager.has_free_slots():
            self.blue_plus_toolbutton.setDisabled(True)
            self.orange_plus_toolbutton.setDisabled(True)
        else:
            self.blue_plus_toolbutton.setDisabled(False)
            self.orange_plus_toolbutton.setDisabled(False)

    def enable_disable_on_bot_select_deselect(self):
        # if no bot selected, disable botconfig groupbox and minus buttons
        if not self.blue_listwidget.selectedItems() and not self.orange_listwidget.selectedItems():
            self.bot_config_groupbox.setDisabled(True)
            self.blue_minus_toolbutton.setDisabled(True)
            self.orange_minus_toolbutton.setDisabled(True)
            return
        else:
            self.bot_config_groupbox.setDisabled(False)

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

    def load_agents(self, config_file=None):
        """
        Loads all agents for this team from the rlbot.cfg
        :param config_file:  A config file that is similar to rlbot.cfg
        """
        if config_file is not None:
            self.overall_config = config_file
        self.agents.clear()
        num_participants = get_num_players(self.overall_config)
        for i in range(num_participants):
            self.load_agent(i)

    def load_agent(self, overall_index=None):
        if not self.index_manager.has_free_slots():
            return None
        if overall_index is None:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.use_index(overall_index)
        agent = self.add_agent(overall_index=overall_index)

        agent_preset = self.add_agent_preset(agent.get_agent_config_path())
        agent.set_agent_preset(agent_preset)

        loadout_file = self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY, overall_index)
        if loadout_file is None or loadout_file == "None":
            directory = os.path.dirname(os.path.realpath(agent.get_agent_config_path()))
            file_path = agent_preset.config.get(BOT_CONFIG_MODULE_HEADER, LOOKS_CONFIG_KEY)
            loadout_file = os.path.realpath(os.path.join(directory, file_path))
        else:
            directory = get_python_root()
            file_path = loadout_file
            loadout_file = os.path.realpath(os.path.join(directory, file_path))
        loadout_preset = self.add_loadout_preset(loadout_file)
        agent.set_loadout_preset(loadout_preset)
        return agent

    def add_agent(self, overall_index=None, team_index=None):
        """
        Creates the agent using self.agent_class and adds it to the index manager.
        :param overall_index: The index of the bot in the config file if it already exists.
        :param team_index: The index of the team to place the agent in
        :return agent:
        """
        if not self.index_manager.has_free_slots():
            return
        if overall_index is None:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.use_index(overall_index)
        agent = Agent(overall_index=overall_index)
        if team_index is not None:
            agent.set_team(team_index)

        self.agents.append(agent)
        return agent

    def remove_agent(self, agent: Agent):
        """
        Removes the given agent.
        """
        self.index_manager.free_index(agent.overall_index)
        self.agents.remove(agent)
        self.update_teams_listwidgets()

    def add_loadout_preset(self, file_path):
        if os.path.isfile(file_path):
            name = os.path.basename(file_path).replace(".cfg", "")
        else:
            name = "new preset"
        if name in self.loadout_presets:
            return self.loadout_presets[name]
        preset = LoadoutPreset(name, file_path)
        self.loadout_presets[preset.get_name()] = preset
        return preset

    def add_agent_preset(self, file_path):
        if os.path.isfile(file_path):
            name = os.path.basename(file_path).replace(".cfg", "")
        else:
            name = "new preset"
        if name in self.agent_presets:
            return self.agent_presets[name]
        preset = AgentPreset(name, file_path)
        self.agent_presets[preset.get_name()] = preset
        return preset

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

    def match_settings_edit_event(self, value):
        sender = self.sender()

        if sender is self.mode_type_combobox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, GAME_MODE, value)
        elif sender is self.map_type_combobox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, GAME_MAP, value)
        elif sender is self.skip_replays_checkbox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, SKIP_REPLAYS, value)
        elif sender is self.instant_start_checkbox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, INSTANT_START, value)
        elif sender is self.match_length_combobox:
            self.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, MUTATOR_MATCH_LENGTH, value)
        elif sender is self.boost_type_combobox:
            self.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BOOST_AMOUNT, value)

    @staticmethod
    def main():
        app = QApplication(sys.argv)
        window = RLBotQTGui()
        window.show()
        app.exec_()
