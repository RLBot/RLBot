from PyQt5 import QtWidgets, QtCore
from rlbot.parsing.match_settings_config_parser import *
from rlbot.gui.design.mutator_customisation import Ui_MutatorCustomiser
import os


class MutatorEditor(QtWidgets.QMainWindow, Ui_MutatorCustomiser):
    def __init__(self, qt_gui):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qt_gui.windowIcon())
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.qt_gui = qt_gui
        self.create_linking_dicts()
        self.prefill_comboboxes()
        self.connect_functions()

    def connect_functions(self):
        for widget, config_name in self.mutator_widget_to_config_name.items():
            def update_value(value, n=config_name):
                self.qt_gui.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, n, value)
                if self.qt_gui.cfg_autosave_checkbutton.isChecked() and os.path.isfile(self.qt_gui.overall_config_path):
                    self.qt_gui.save_overall_config(10)

            widget.currentTextChanged.connect(update_value)
        self.reset_default_pushbutton.clicked.connect(self.set_default_mutators)
        self.close_pushbutton.clicked.connect(lambda: self.hide())

    def set_default_mutators(self):
        for mutator, options in self.config_name_to_options_list.items():
            self.qt_gui.overall_config.set_value(MUTATOR_CONFIGURATION_HEADER, mutator, options[0])
            self.update_comboboxes()

    def update_comboboxes(self):
        for widget, config_name in self.mutator_widget_to_config_name.items():
            widget.setCurrentText(self.qt_gui.overall_config.get(MUTATOR_CONFIGURATION_HEADER, config_name))

    def prefill_comboboxes(self):
        for widget, config_name in self.mutator_widget_to_config_name.items():
            if isinstance(widget, QtWidgets.QComboBox):
                widget.addItems(self.config_name_to_options_list[config_name])

    def popup(self):
        self.show()

    def create_linking_dicts(self):
        self.config_name_to_mutator_widget = {
            MUTATOR_MATCH_LENGTH: self.match_length_combobox,
            MUTATOR_MAX_SCORE: self.max_score_combobox,
            MUTATOR_OVERTIME: self.overtime_combobox,
            MUTATOR_SERIES_LENGTH: self.series_length_combobox,
            MUTATOR_GAME_SPEED: self.game_speed_combobox,
            MUTATOR_BALL_MAX_SPEED: self.ball_max_speed_combobox,
            MUTATOR_BALL_TYPE: self.ball_type_combobox,
            MUTATOR_BALL_WEIGHT: self.ball_weight_combobox,
            MUTATOR_BALL_SIZE: self.ball_size_combobox,
            MUTATOR_BALL_BOUNCINESS: self.ball_bounciness_combobox,
            MUTATOR_BOOST_AMOUNT: self.boost_amount_combobox,
            MUTATOR_RUMBLE: self.rumble_combobox,
            MUTATOR_BOOST_STRENGTH: self.boost_strength_combobox,
            MUTATOR_GRAVITY: self.gravity_combobox,
            MUTATOR_DEMOLISH: self.demolish_combobox,
            MUTATOR_RESPAWN_TIME: self.respawn_time_combobox
        }

        self.mutator_widget_to_config_name = {}
        for config_name, widget in self.config_name_to_mutator_widget.items():
            self.mutator_widget_to_config_name[widget] = config_name

        self.config_name_to_options_list = {
            MUTATOR_MATCH_LENGTH: match_length_types,
            MUTATOR_MAX_SCORE: max_score_types,
            MUTATOR_OVERTIME: overtime_mutator_types,
            MUTATOR_SERIES_LENGTH: series_length_mutator_types,
            MUTATOR_GAME_SPEED: game_speed_mutator_types,
            MUTATOR_BALL_MAX_SPEED: ball_max_speed_mutator_types,
            MUTATOR_BALL_TYPE: ball_type_mutator_types,
            MUTATOR_BALL_WEIGHT: ball_weight_mutator_types,
            MUTATOR_BALL_SIZE: ball_size_mutator_types,
            MUTATOR_BALL_BOUNCINESS: ball_bounciness_mutator_types,
            MUTATOR_BOOST_AMOUNT: boost_amount_mutator_types,
            MUTATOR_RUMBLE: rumble_mutator_types,
            MUTATOR_BOOST_STRENGTH: boost_strength_mutator_types,
            MUTATOR_GRAVITY: gravity_mutator_types,
            MUTATOR_DEMOLISH: demolish_mutator_types,
            MUTATOR_RESPAWN_TIME: respawn_time_mutator_types
        }
