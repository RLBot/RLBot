import configparser
import os
import pathlib
import sys
import threading

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QCheckBox, QMessageBox
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QWidget, QComboBox, QLineEdit, QRadioButton, QSlider
from rlbot.agents.base_agent import BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY
from rlbot.gui.design.qt_gui import Ui_MainWindow
from rlbot.gui.gui_agent import GUIAgent
from rlbot.gui.index_manager import IndexManager
from rlbot.gui.mutator_editor import MutatorEditor
from rlbot.gui.preset_editors import CarCustomisationDialog, AgentCustomisationDialog, index_of_config_path_in_combobox
from rlbot.gui.presets import AgentPreset, LoadoutPreset
from rlbot.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY, \
    PARTICIPANT_CONFIG_KEY
from rlbot.parsing.bot_config_bundle import BotConfigBundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs
from rlbot.parsing.match_settings_config_parser import *
from rlbot.parsing.rlbot_config_parser import create_bot_config_layout, TEAM_CONFIGURATION_HEADER
from rlbot.setup_manager import SetupManager, DEFAULT_RLBOT_CONFIG_LOCATION
from rlbot.utils.file_util import get_python_root, get_rlbot_directory
from rlbot.utils.structures.start_match_structures import MAX_PLAYERS


class RLBotQTGui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        """
        Creates a new QT mainwindow with the GUI
        """
        super().__init__()
        self.setupUi(self)
        self.overall_config = None
        self.index_manager = IndexManager(MAX_PLAYERS)

        self.agents = []
        self.agent_presets = {}
        self.bot_names_to_agent_dict = {}
        self.loadout_presets = {}
        self.current_bot = None
        self.overall_config_timer = None
        self.setup_manager = None
        self.match_process = None
        self.overall_config = None
        self.overall_config_path = None
        self.launch_in_progress = False

        self.car_customisation = CarCustomisationDialog(self)
        self.agent_customisation = AgentCustomisationDialog(self)
        self.mutator_customisation = MutatorEditor(self)

        if os.path.isfile(DEFAULT_RLBOT_CONFIG_LOCATION):
            self.load_overall_config(DEFAULT_RLBOT_CONFIG_LOCATION)
        else:
            self.load_off_disk_overall_config()

        self.init_match_settings()
        self.update_match_settings()

        self.connect_functions()
        self.update_bot_type_combobox()

    def bot_item_drop_event(self, dropped_listwidget, event):
        """
        Switches the team for the dropped agent to the other team
        :param dropped_listwidget: The listwidget belonging to the new team for the agent
        :param event: The QDropEvent containing the source
        :return:
        """
        dragged_listwidget = event.source()
        if dragged_listwidget is dropped_listwidget:  # drops in the same widget
            return
        self.current_bot.set_team(0 if dropped_listwidget == self.blue_listwidget else 1)
        self.update_teams_listwidgets()

    def fixed_indices(self):
        """
        Agents in the GUI might not have following overall indices,
        thereby a file saved through the GUI would cause other bots to start than the GUI when ran
        :return: CustomConfig instance, copy of the overall config which has the indices sorted out
        """
        config = self.overall_config.copy()

        used_indices = sorted(self.index_manager.numbers)
        not_used_indices = [e for e in range(MAX_PLAYERS) if e not in used_indices]
        order = used_indices + not_used_indices
        header = config[PARTICIPANT_CONFIGURATION_HEADER]
        for name, config_value in header.values.items():
            old_values = list(config_value.value)
            for i in range(MAX_PLAYERS):
                config_value.set_value(old_values[order[i]], index=i)
        return config

    def run_button_pressed(self):
        if self.launch_in_progress:
            # Do nothing if we're already in the process of launching a configuration.
            # Attempting to run again when we're in this state can result in duplicate processes.
            # TODO: Add a mutex around this variable here for safety.
            return
        self.launch_in_progress = True
        if self.setup_manager is not None:
            self.setup_manager.shut_down(time_limit=5, kill_all_pids=False)
            # Leave any external processes alive, e.g. Java or C#, since it can
            # be useful to keep them around. The user can kill them with the
            # Kill Bots button instead.

        self.match_process = threading.Thread(target=self.start_match)
        self.match_process.start()

    def start_match(self):
        """
        Starts a match with the current configuration
        :return:
        """

        agent_configs_dict = {}
        loadout_configs_dict = {}
        for agent in self.agents:
            i, agent_config, loadout_config = agent.get_configs()
            agent_configs_dict[i] = agent_config
            loadout_configs_dict[i] = loadout_config
        agent_configs = {}
        loadout_configs = {}
        index = 0
        for i in range(MAX_PLAYERS):
            if i in agent_configs_dict:
                agent_configs[index] = agent_configs_dict[i]
                loadout_configs[index] = loadout_configs_dict[i]
                index += 1

        if self.setup_manager is None:
            self.setup_manager = SetupManager()

        self.setup_manager.load_config(self.overall_config, self.overall_config_path, agent_configs, loadout_configs)
        self.setup_manager.connect_to_game()
        self.setup_manager.launch_quick_chat_manager()
        self.setup_manager.start_match()
        self.setup_manager.launch_bot_processes()
        self.launch_in_progress = False
        self.setup_manager.infinite_loop()  # Runs forever until interrupted

    def connect_functions(self):
        """
        Connects all events to the functions which should be called
        :return:
        """
        # Lambda is sometimes used to prevent passing the event parameter.
        self.cfg_load_pushbutton.clicked.connect(lambda: self.load_overall_config())
        self.cfg_save_pushbutton.clicked.connect(lambda: self.save_overall_config())

        self.blue_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        self.orange_listwidget.itemSelectionChanged.connect(self.load_selected_bot)
        self.blue_listwidget.dropEvent = lambda event: self.bot_item_drop_event(self.blue_listwidget, event)
        self.orange_listwidget.dropEvent = lambda event: self.bot_item_drop_event(self.orange_listwidget, event)

        self.blue_name_lineedit.editingFinished.connect(self.team_settings_edit_event)
        self.orange_name_lineedit.editingFinished.connect(self.team_settings_edit_event)
        self.blue_color_spinbox.valueChanged.connect(self.team_settings_edit_event)
        self.orange_color_spinbox.valueChanged.connect(self.team_settings_edit_event)

        self.blue_minus_toolbutton.clicked.connect(lambda e: self.remove_agent(self.current_bot))
        self.orange_minus_toolbutton.clicked.connect(lambda e: self.remove_agent(self.current_bot))
        self.blue_plus_toolbutton.clicked.connect(lambda e: self.add_agent_button(team_index=0))
        self.orange_plus_toolbutton.clicked.connect(lambda e: self.add_agent_button(team_index=1))

        for child in self.bot_config_groupbox.findChildren(QWidget):
            if isinstance(child, QLineEdit):
                child.editingFinished.connect(self.bot_config_edit_event)
            elif isinstance(child, QSlider):
                child.valueChanged.connect(self.bot_config_edit_event)
            elif isinstance(child, QRadioButton):
                child.toggled.connect(self.bot_config_edit_event)
            elif isinstance(child, QComboBox):
                child.currentTextChanged.connect(self.bot_config_edit_event)
        self.loadout_preset_toolbutton.clicked.connect(self.car_customisation.popup)
        self.agent_preset_toolbutton.clicked.connect(self.agent_customisation.popup)
        self.preset_load_toplevel_pushbutton.clicked.connect(self.load_preset_toplevel)

        for child in self.match_settings_groupbox.findChildren(QWidget):
            if isinstance(child, QComboBox):
                child.currentTextChanged.connect(self.match_settings_edit_event)
            elif isinstance(child, QCheckBox):
                child.toggled.connect(self.match_settings_edit_event)

        self.edit_mutators_pushbutton.clicked.connect(self.mutator_customisation.popup)
        self.kill_bots_pushbutton.clicked.connect(self.kill_bots)
        self.run_button.clicked.connect(self.run_button_pressed)

    def load_preset_toplevel(self):
        preset = self.agent_customisation.load_preset_cfg()
        if preset is None:
            return

        self.agent_preset_combobox.setCurrentText(preset.get_name())

        loadout_preset = self.add_loadout_preset(preset.looks_path)
        self.car_customisation.update_presets_widgets()

        loadout_index = index_of_config_path_in_combobox(self.loadout_preset_combobox, loadout_preset.config_path)
        self.loadout_preset_combobox.setCurrentIndex(loadout_index)

        self.current_bot.set_loadout_preset(loadout_preset)

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
                self.blue_listwidget.setCurrentItem(self.blue_listwidget.findItems(
                    self.validate_name(agent.get_name(), agent), QtCore.Qt.MatchExactly)[0])

        elif sender is self.orange_radiobutton and value:
            if agent.get_team() != 1:
                agent.set_team(1)
                self.update_teams_listwidgets()
                self.orange_listwidget.setCurrentItem(self.orange_listwidget.findItems(
                    self.validate_name(agent.get_name(), agent), QtCore.Qt.MatchExactly)[0])

        elif sender is self.ign_lineedit:
            if agent not in self.agents:
                return
            if not agent.get_team():
                listwidget = self.blue_listwidget
            else:
                listwidget = self.orange_listwidget
            name = self.validate_name(value, agent)
            old_name = self.validate_name(agent.ingame_name, agent)
            row = listwidget.currentRow()
            del self.bot_names_to_agent_dict[old_name]
            agent.set_name(value)
            self.bot_names_to_agent_dict[name] = agent
            self.update_teams_listwidgets()
            listwidget.setCurrentRow(row)
        elif sender is self.loadout_preset_combobox:
            if self.bot_config_groupbox.isEnabled() and self.current_bot is not None:

                index = self.loadout_preset_combobox.currentIndex()
                preset = self.loadout_preset_combobox.itemData(index)

                self.current_bot.set_loadout_preset(preset)
        elif sender is self.agent_preset_combobox:
            if value and self.bot_config_groupbox.isEnabled() and self.current_bot is not None:

                preset = self.agent_preset_combobox.currentData()

                self.current_bot.set_agent_preset(preset)
                agent.set_name(agent.agent_preset.config.get(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY))
                self.ign_lineedit.setText(agent.ingame_name)
                if not agent.get_team():
                    listwidget = self.blue_listwidget
                else:
                    listwidget = self.orange_listwidget
                row = listwidget.currentRow()
                self.update_teams_listwidgets()
                listwidget.setCurrentRow(row)

                loadout_index = index_of_config_path_in_combobox(self.loadout_preset_combobox, preset.looks_path)
                if loadout_index is not None:
                    self.loadout_preset_combobox.setCurrentIndex(loadout_index)

        elif sender is self.bot_level_slider:
            agent.set_bot_skill(value / 100)

        if self.cfg_autosave_checkbutton.isChecked() and os.path.isfile(self.overall_config_path):
            self.save_overall_config(10)

    def update_bot_type_combobox(self):
        """
        Handles selecting another bot type in the combobox, hides some frames and shows others depending on the setting
        Also saves the new type if there is a bot selected
        :return:
        """
        bot_type = self.bot_type_combobox.currentText()
        if bot_type == 'RLBot':
            self.rlbot_frame.setHidden(False)
            self.extra_line.setHidden(False)
            self.psyonix_bot_frame.setHidden(True)
            self.appearance_frame.setHidden(False)
            self.label_3.setHidden(False)
            self.ign_lineedit.setHidden(False)
        elif bot_type == 'Psyonix':
            self.psyonix_bot_frame.setHidden(False)
            self.rlbot_frame.setHidden(True)
            self.extra_line.setHidden(False)
            self.appearance_frame.setHidden(False)
            self.label_3.setHidden(False)
            self.ign_lineedit.setHidden(False)
        elif bot_type == 'Human':
            self.psyonix_bot_frame.setHidden(True)
            self.rlbot_frame.setHidden(True)
            self.extra_line.setHidden(True)
            self.appearance_frame.setHidden(False)
            self.label_3.setHidden(True)
            self.ign_lineedit.setHidden(True)
        elif bot_type == 'Party Member Bot':
            self.rlbot_frame.setHidden(False)
            self.extra_line.setHidden(False)
            self.psyonix_bot_frame.setHidden(True)
            self.appearance_frame.setHidden(False)
            self.label_3.setHidden(True)
            self.ign_lineedit.setHidden(True)

        if self.bot_config_groupbox.isEnabled() and self.current_bot is not None:
            config_type = bot_type.lower().replace(" ", "_")
            self.current_bot.set_participant_type(config_type)

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

        if self.cfg_autosave_checkbutton.isChecked() and os.path.isfile(self.overall_config_path):
            self.save_overall_config(10)

    def update_team_settings(self):
        """
        Sets all team settings widgets to the value in the overall config
        :return:
        """
        self.blue_name_lineedit.setText(self.overall_config.get(TEAM_CONFIGURATION_HEADER, "Team Blue Name"))
        self.orange_name_lineedit.setText(self.overall_config.get(TEAM_CONFIGURATION_HEADER, "Team Orange Name"))
        self.blue_color_spinbox.setValue(self.overall_config.getint(TEAM_CONFIGURATION_HEADER, "Team Blue Color"))
        self.orange_color_spinbox.setValue(self.overall_config.getint(TEAM_CONFIGURATION_HEADER, "Team Orange Color"))

    def load_off_disk_overall_config(self):
        self.cfg_autosave_checkbutton.setChecked(False)
        self.cfg_autosave_checkbutton.setDisabled(True)
        if self.overall_config is None:
            self.overall_config = create_bot_config_layout()
        GUIAgent.overall_config = self.overall_config
        self.overall_config.init_indices(MAX_PLAYERS)
        self.overall_config_path = ""
        self.load_agents()
        # self.load_bot_directory(".")
        self.update_teams_listwidgets()
        if not self.overall_config_path:
            self.cfg_file_path_lineedit.setStyleSheet("border: 1px solid red;")
            self.cfg_file_path_lineedit.setText("Please load a configuration file")
            self.blue_plus_toolbutton.setEnabled(False)
            self.orange_plus_toolbutton.setEnabled(False)
            self.run_button.setEnabled(False)
        else:
            self.cfg_file_path_lineedit.setText(self.overall_config_path)
        self.update_team_settings()
        self.car_customisation.update_presets_widgets()
        self.agent_customisation.update_presets_widgets()
        self.mutator_customisation.update_comboboxes()

    def load_overall_config(self, config_path=None):
        """
        Loads the overall config from the config path, or asks for a path if config_path is None
        :param config_path: the path to load the overall_config from, if None a path is requested
        :return:
        """
        if self.overall_config is None:
            self.overall_config = create_bot_config_layout()
        GUIAgent.overall_config = self.overall_config
        if config_path is None:
            config_path = QFileDialog.getOpenFileName(self, "Load Overall Config", "", "Config Files (*.cfg)")[0]
            if not config_path:
                self.statusbar.showMessage("No file selected, not loading config", 5000)
                return
        if config_path is None or not os.path.isfile(config_path):
            return
        if pathlib.Path(config_path).suffix != '.cfg':
            self.popup_message("This file is not a config file!", "Invalid File Extension", QMessageBox.Warning)
            return
        raw_parser = configparser.RawConfigParser()
        raw_parser.read(config_path, encoding='utf8')
        for section in ['Match Configuration', 'Participant Configuration']:
            if not raw_parser.has_section(section):
                self.popup_message(f"Config file is missing the section {section}, not loading it!",
                                   "Invalid Config File", QMessageBox.Warning)
                return
        self.overall_config_path = config_path
        self.overall_config.parse_file(raw_parser, MAX_PLAYERS, config_directory=os.path.dirname(self.overall_config_path))
        self.load_agents()
        # self.load_bot_directory(".")
        self.update_teams_listwidgets()
        self.cfg_file_path_lineedit.setText(self.overall_config_path)
        self.cfg_file_path_lineedit.setStyleSheet("")
        self.run_button.setEnabled(True)
        self.update_team_settings()
        self.car_customisation.update_presets_widgets()
        self.agent_customisation.update_presets_widgets()
        self.mutator_customisation.update_comboboxes()

    def save_overall_config(self, time_out=0):
        """
        Schedules a save after given time_out
        :param time_out: The amount of seconds it should wait before saving
        :return:
        """
        def save():
            if not os.path.exists(self.overall_config_path):
                return
            self.overall_config_timer.setInterval(1000)
            if self.remaining_save_timer > 0:
                self.statusbar.showMessage("Saving Overall Config in " + str(self.remaining_save_timer) + " seconds")
                self.remaining_save_timer -= 1
            else:
                self.clean_overall_config_loadouts()
                with open(self.overall_config_path, "w", encoding='utf8') as f:
                    f.write(str(self.fixed_indices()))
                self.statusbar.showMessage("Saved Overall Config to " + self.overall_config_path, 5000)
                self.overall_config_timer.stop()
        if self.overall_config_timer is None:
            self.overall_config_timer = QTimer()
            self.overall_config_timer.timeout.connect(save)
        save_path = self.overall_config_path
        if save_path is None or not os.path.isfile(save_path):
            save_path = QFileDialog.getSaveFileName(self, "Save Overall Config", "", "Config Files (*.cfg)")[0]
            if not save_path:
                self.statusbar.showMessage("Unable to save the configuration without a path", 5000)
                return
            self.overall_config_path = save_path
        self.remaining_save_timer = time_out
        self.overall_config_timer.start(0)

    def clean_overall_config_loadouts(self):
        """
        Set all unusued loadout paths to None. This makes sure agents don't have a custom loadout when new agents
        are added in the gui.
        """
        for i in range(MAX_PLAYERS):
            if i not in self.index_manager.numbers:
                self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY, "None", i)

    def load_selected_bot(self):
        """
        Loads all the values belonging to the new selected agent into the bot_config_groupbox
        :return:
        """
        # prevent processing from itself (clearing the other one processes this)
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

        loadout_index = index_of_config_path_in_combobox(
            self.loadout_preset_combobox, agent.get_loadout_preset().config_path)
        self.loadout_preset_combobox.setCurrentIndex(loadout_index or 0)

        self.agent_preset_combobox.blockSignals(True)
        self.agent_preset_combobox.setCurrentText(agent.get_agent_preset().get_name())
        self.agent_preset_combobox.blockSignals(False)
        self.bot_level_slider.setValue(int(agent.get_bot_skill() * 100))

    def update_teams_listwidgets(self):
        """
        Clears all items from the listwidgets and then adds everything from the self.agents list again to the right team
        :return:
        """
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
        """
        Disables the botconfig groupbox and minus buttons when no bot is selected
        :return:
        """
        if not self.blue_listwidget.selectedItems() and not self.orange_listwidget.selectedItems():
            self.bot_config_groupbox.setDisabled(True)
            self.blue_minus_toolbutton.setDisabled(True)
            self.orange_minus_toolbutton.setDisabled(True)
        else:
            self.bot_config_groupbox.setDisabled(False)

    def validate_name(self, name, agent):
        """
        Finds the modification of name which is not yet in the list
        :param name: the (new) name for the agent
        :param agent: the agent instance to allow the same name as the previous one if necessary
        :return: the best modification of name not yet in a listwidget
        """
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

    def add_agent_button(self, team_index: int):
        """
        The method to handle the [+] button press, adds an agent to the team
        :param team_index: the team to set for the new agent, 0 for blue and 1 for orange
        :return:
        """
        agent = self.load_agent()
        if agent is None:
            return
        agent.set_team(team_index)
        self.car_customisation.update_presets_widgets()
        self.agent_customisation.update_presets_widgets()
        self.update_teams_listwidgets()
        if agent.get_team() == 0:
            self.blue_listwidget.setCurrentItem(self.blue_listwidget.findItems(
                self.validate_name(agent.get_name(), agent), QtCore.Qt.MatchExactly)[0])
        else:
            self.orange_listwidget.setCurrentItem(self.orange_listwidget.findItems(
                self.validate_name(agent.get_name(), agent), QtCore.Qt.MatchExactly)[0])

    def load_agents(self, config_file=None):
        """
        Loads all agents for this team from the rlbot.cfg
        :param config_file:  A config file that is similar to rlbot.cfg
        """
        if config_file is not None:
            self.overall_config = config_file
        self.agents.clear()
        num_participants = get_num_players(self.overall_config)
        try:
            for i in range(num_participants):
                self.load_agent(i)
        except BaseException as e:
            raise ValueError(f"{str(e)}\nPlease check your config files! {self.overall_config_path}")

    def load_agent(self, overall_index: int=None):
        """
        Loads all data for overall_index from the overall config and also loads both presets
        :param overall_index: the index of the targeted agent
        :return agent: an Agent (gui_agent) class with all loaded values
        """
        if not self.index_manager.has_free_slots():
            return None
        if overall_index is None:
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.use_index(overall_index)
        agent = self.add_agent(overall_index=overall_index)

        path_in_overall_config = agent.get_agent_config_path()
        if path_in_overall_config is None:
            # Fall back to the path of the first agent if there's nothing configured.
            path_in_overall_config = self.overall_config.getpath(PARTICIPANT_CONFIGURATION_HEADER,
                                                                 PARTICIPANT_CONFIG_KEY, 0)
        agent_preset = self.add_agent_preset(path_in_overall_config)
        agent.set_agent_preset(agent_preset)
        agent.set_name(agent_preset.config.get(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY))

        # Add the preset's loadout as a loadout
        own_loadout = self.add_loadout_preset(agent_preset.looks_path)

        # Agent has a loadout defined in overall config, load that if it is not None
        loadout_file_in_overall_config = self.overall_config.get(PARTICIPANT_CONFIGURATION_HEADER,
                                               PARTICIPANT_LOADOUT_CONFIG_KEY, overall_index)
        if loadout_file_in_overall_config is None or loadout_file_in_overall_config == "None":
            agent.set_loadout_preset(own_loadout)
        else:
            directory = get_python_root()
            file_path = loadout_file_in_overall_config
            loadout_file_in_overall_config = os.path.realpath(os.path.join(directory, file_path))
            loadout_preset = self.add_loadout_preset(loadout_file_in_overall_config)
            agent.set_loadout_preset(loadout_preset)

        return agent

    def load_bot_config_bundle(self, config_bundle: BotConfigBundle):
        self.add_agent_preset(config_bundle.config_path)
        self.add_loadout_preset(config_bundle.looks_path)

    def load_bot_directory(self, directory):
        for bundle in scan_directory_for_bot_configs(directory):
            try:
                self.load_bot_config_bundle(bundle)
            except Exception as e:
                print(e)

    def add_agent(self, overall_index=None, team_index=None):
        """
        Creates the agent using self.agent_class and adds it to the index manager.
        :param overall_index: The index of the bot in the config file if it already exists.
        :param team_index: The index of the team to place the agent in
        :return agent: an Agent (gui_agent) with either given index or a free one, returns None if there is no index given and all indices are occupied
        """
        if overall_index is None:
            if not self.index_manager.has_free_slots():
                return
            overall_index = self.index_manager.get_new_index()
        else:
            self.index_manager.use_index(overall_index)
        agent = GUIAgent(overall_index=overall_index)
        if team_index is not None:
            agent.set_team(team_index)

        self.agents.append(agent)
        self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, PARTICIPANT_COUNT_KEY, len(self.agents))
        return agent

    def remove_agent(self, agent: GUIAgent):
        """
        Removes the given agent.
        :param agent: the agent to remove
        :return:
        """
        self.index_manager.free_index(agent.overall_index)
        self.agents.remove(agent)
        self.update_teams_listwidgets()
        self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, PARTICIPANT_COUNT_KEY, len(self.agents))
        self.overall_config.set_value(PARTICIPANT_CONFIGURATION_HEADER, PARTICIPANT_LOADOUT_CONFIG_KEY, "None", agent.overall_index)
        if len(self.agents) == 0:
            return
        if agent.get_team() == 0:
            if self.blue_listwidget.count() != 0:
                self.blue_listwidget.setCurrentRow(self.blue_listwidget.count() - 1)
            else:
                self.orange_listwidget.setCurrentRow(self.orange_listwidget.count() - 1)
        else:
            if self.orange_listwidget.count() != 0:
                self.orange_listwidget.setCurrentRow(self.orange_listwidget.count() - 1)
            else:
                self.blue_listwidget.setCurrentRow(self.blue_listwidget.count() - 1)

    def add_loadout_preset(self, file_path: str):
        """
        Loads a preset using file_path with all values from that path loaded
        :param file_path: the path to load the preset from, if invalid a default preset is returned
        :return preset: the loadout preset created
        """
        if file_path is not None and os.path.isfile(file_path):
            name = pathlib.Path(file_path).stem
        else:
            name = "new preset"
        if file_path in self.loadout_presets:
            return self.loadout_presets[file_path]
        preset = LoadoutPreset(name, file_path)
        self.loadout_presets[preset.config_path] = preset
        return preset

    def add_agent_preset(self, file_path):
        """
        Loads a preset using file_path with all values from that path loaded
        :param file_path: the path to load the preset from. We'll throw an exception if it's invalid.
        :return preset: the agent preset created
        """
        if file_path is not None and os.path.isfile(file_path):
            name = pathlib.Path(file_path).stem
        else:
            raise FileNotFoundError(f"File path {file_path} is not found!")

        if name in self.agent_presets:
            if self.agent_presets[name].config_path == file_path:
                return self.agent_presets[name]
            else:
                i = 1
                for preset_name in self.agent_presets:
                    if name in preset_name:
                        i += 1
                name = f"{name} ({i})"
        preset = AgentPreset(name, file_path)
        self.agent_presets[preset.get_name()] = preset
        return preset

    def init_match_settings(self):
        """
        Adds all items to the match settings comboboxes
        :return:
        """
        self.mode_type_combobox.addItems(game_mode_types)
        self.map_type_combobox.addItems(map_types)

    def update_match_settings(self):
        """
        Sets all match setting widgets to the values in the overall config
        :return:
        """
        self.mode_type_combobox.setCurrentText(self.overall_config.get(MATCH_CONFIGURATION_HEADER, GAME_MODE))
        self.map_type_combobox.setCurrentText(self.overall_config.get(MATCH_CONFIGURATION_HEADER, GAME_MAP))
        self.skip_replays_checkbox.setChecked(self.overall_config.getboolean(MATCH_CONFIGURATION_HEADER, SKIP_REPLAYS))
        self.instant_start_checkbox.setChecked(self.overall_config.getboolean(MATCH_CONFIGURATION_HEADER, INSTANT_START))
        self.enable_lockstep_checkbox.setChecked(self.overall_config.getboolean(MATCH_CONFIGURATION_HEADER, ENABLE_LOCKSTEP))

    def match_settings_edit_event(self, value):
        """
        Handles all edits to match settings and sets the config value to the new value
        :param value: the value to apply to the overall config
        :return:
        """
        sender = self.sender()

        if sender is self.mode_type_combobox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, GAME_MODE, value)
        elif sender is self.map_type_combobox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, GAME_MAP, value)
        elif sender is self.skip_replays_checkbox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, SKIP_REPLAYS, value)
        elif sender is self.instant_start_checkbox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, INSTANT_START, value)
        elif sender is self.enable_lockstep_checkbox:
            self.overall_config.set_value(MATCH_CONFIGURATION_HEADER, ENABLE_LOCKSTEP, value)
        elif sender is self.match_length_combobox:
            self.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, MUTATOR_MATCH_LENGTH, value)
        elif sender is self.boost_type_combobox:
            self.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, MUTATOR_BOOST_AMOUNT, value)

        if self.cfg_autosave_checkbutton.isChecked() and os.path.isfile(self.overall_config_path):
            self.save_overall_config(10)

    def popup_message(self, message: str, title: str, icon=QMessageBox.Warning):
        popup = QMessageBox(self)
        popup.setIcon(icon)
        popup.setWindowTitle(title)
        popup.setText(message)
        popup.setStandardButtons(QMessageBox.Ok)
        popup.exec_()

    def kill_bots(self):
        if self.setup_manager is not None:
            self.setup_manager.shut_down(time_limit=5, kill_all_pids=True)
        else:
            print("There gotta be some setup manager already")

    @staticmethod
    def main():
        """
        Start the GUI
        :return:
        """
        app = QApplication(sys.argv)
        rlbot_icon = QtGui.QIcon(os.path.join(get_rlbot_directory(), 'img', 'rlbot_icon.png'))
        app.setWindowIcon(rlbot_icon)
        window = RLBotQTGui()
        window.show()
        app.exec_()
