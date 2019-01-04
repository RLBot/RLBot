import os
import json
from PyQt5 import QtWidgets, QtCore
import configparser
import pathlib

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem

from rlbot.gui.design.car_customisation import Ui_LoadoutPresetCustomiser
from rlbot.gui.design.agent_customisation import Ui_AgentPresetCustomiser
from rlbot.gui.presets import AgentPreset, LoadoutPreset
from rlbot.utils.file_util import get_python_root


def index_of_config_path_in_combobox(combobox, config_path):
    for i in range(combobox.count()):
        preset = combobox.itemData(i)
        if preset.config_path == config_path:
            return i
    return None


def index_of_config_path_in_listwidget(listwidget, config_path):
    for i in range(listwidget.count()):
        list_item = listwidget.item(i)
        if list_item.data(Qt.UserRole).config_path == config_path:
            return i
    return None


class BasePresetEditor(QtWidgets.QMainWindow):
    """
    The Base of the popup windows to modify a Preset, handles the basic method of editing the preset
    """

    def __init__(self, qt_gui, presets: dict, root_combobox: QtWidgets.QComboBox, preset_class):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qt_gui.windowIcon())
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.qt_gui = qt_gui
        self.presets = presets
        self.root_combobox = root_combobox
        self.preset_class = preset_class

        self.load_variables()

        self.connect_functions()
        self.update_presets_widgets()

    def popup(self):
        self.show()
        self.presets_listwidget.setCurrentRow(0)

    def load_variables(self):
        pass

    def get_current_preset(self):
        return self.presets_listwidget.currentItem().data(Qt.UserRole)

    def connect_functions(self):
        self.presets_listwidget.itemSelectionChanged.connect(self.load_selected_preset)

        self.preset_name_lineedit.editingFinished.connect(self.preset_name_changed)
        self.preset_new_pushbutton.clicked.connect(self.add_new_preset)
        self.preset_load_pushbutton.clicked.connect(self.load_preset_cfg)
        self.preset_save_pushbutton.clicked.connect(self.save_preset_cfg)

    def load_selected_preset(self):
        if len(self.presets_listwidget.selectedItems()) == 0:
            self.right_frame.setEnabled(False)
            return
        self.right_frame.setEnabled(True)
        preset = self.get_current_preset()

        self.preset_name_lineedit.setText(preset.get_name())
        self.preset_path_lineedit.setText(preset.config_path)

    def update_presets_widgets(self):
        self.presets_listwidget.clear()

        for config_path, preset in self.presets.items():
            item = QListWidgetItem(preset.get_name(), self.presets_listwidget)
            item.setData(Qt.UserRole, preset)
            self.presets_listwidget.addItem(item)

        # Also updates the combobox which you can select the agent preset for the bot through
        current_text = self.root_combobox.currentText()
        self.root_combobox.blockSignals(True)
        self.root_combobox.clear()
        for config_path, preset in self.presets.items():
            self.root_combobox.addItem(preset.get_name(), preset)
        self.root_combobox.setCurrentText(current_text)
        self.root_combobox.blockSignals(False)

    def preset_name_changed(self):
        new_name = self.preset_name_lineedit.text()
        self.update_preset_name(self.get_current_preset(), new_name)

    def update_preset_name(self, preset, new_name):

        preset_index = index_of_config_path_in_listwidget(self.presets_listwidget, preset.config_path)

        if preset_index is not None:
            self.presets_listwidget.item(preset_index).setText(new_name)

        preset.name = new_name

    def add_new_preset(self):
        name = self.validate_name("new preset", None)
        preset = self.preset_class(name)
        preset_key = "temp:" + name
        self.presets[preset_key] = preset
        self.update_presets_widgets()

        for i in range(self.presets_listwidget.count()):
            list_item = self.presets_listwidget.item(i)
            if list_item.data(Qt.UserRole) == preset:
                self.presets_listwidget.setCurrentRow(i)

    def load_preset_cfg(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Config', '', 'Config Files (*.cfg)')[0]
        if not os.path.isfile(file_path):
            return
        if pathlib.Path(file_path).suffix != '.cfg':
            self.popup_message("This file is not a config file!", "Invalid File Extension",
                               QtWidgets.QMessageBox.Warning)
            return
        try:
            preset = self.preset_class(self.validate_name(pathlib.Path(file_path).stem, None), file_path)
        except configparser.NoSectionError:
            self.popup_message("This file does not have the right sections!", "Invalid Config File",
                               QtWidgets.QMessageBox.Warning)
            return
        self.presets[preset.get_name()] = preset
        self.update_presets_widgets()
        self.presets_listwidget.setCurrentItem(
            self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0])
        return preset

    def save_preset_cfg(self, time_out=0):
        preset = self.get_current_preset()
        if preset.config_path is None:
            file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Config', '', 'Config Files (*.cfg)')[0]
            if file_path is None or not file_path:
                return

            preset.config_path = os.path.realpath(file_path)

            # Remove this preset from the dict since it is not currently keyed by config path
            self.presets = {k: v for k, v in self.presets.items() if v != preset}
            for key in list(self.presets.keys()):
                if self.presets[key] == preset:
                    del self.presets[key]

            # Add it back keyed by config path
            self.presets[preset.config_path] = preset

            new_name = self.validate_name(pathlib.Path(preset.config_path).stem, preset)
            self.update_preset_name(preset, new_name)

            preset.save_config(time_out=time_out, message_out=self.statusbar.showMessage)

            self.load_selected_preset()
            self.update_presets_widgets()

        else:
            preset.save_config(time_out=time_out, message_out=self.statusbar.showMessage)

    def validate_name(self, name, preset, copy_index=None):

        value = name
        if copy_index is not None:
            value += " (" + str(copy_index) + ")"

        for key, p in self.presets.items():
            if p.get_name() == value:
                if p is preset:
                    return value
                return self.validate_name(name, preset, (copy_index or 1) + 1)

        return value

    def popup_message(self, message: str, title: str, icon=QtWidgets.QMessageBox.Warning):
        popup = QtWidgets.QMessageBox(self)
        popup.setIcon(icon)
        popup.setWindowTitle(title)
        popup.setText(message)
        popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
        popup.exec_()
        return


class CarCustomisationDialog(BasePresetEditor, Ui_LoadoutPresetCustomiser):
    """
    The class extending BasePresetEditor to allow some loadout preset specific preset editing, like handling item names
    """

    def __init__(self, qt_gui):
        super().__init__(qt_gui, qt_gui.loadout_presets, qt_gui.loadout_preset_combobox, LoadoutPreset)

    def load_variables(self):
        super().load_variables()
        self.create_config_headers_dicts()
        self.longlabel_to_id, self.id_to_longlabel = self.get_item_dicts()
        self.prefill_comboboxes()

    def load_preset_cfg(self) -> LoadoutPreset:
        return super().load_preset_cfg()

    def connect_functions(self):
        super().connect_functions()
        for config_widget in self.config_widgets_to_headers:
            if isinstance(config_widget, QtWidgets.QComboBox):
                config_widget.currentIndexChanged.connect(self.update_spinbox_and_combobox)
            elif isinstance(config_widget, QtWidgets.QAbstractSpinBox):
                config_widget.valueChanged.connect(self.update_spinbox_and_combobox)

    def update_spinbox_and_combobox(self):
        # Updates the corresponding widget (ie update spinbox if combobox edited)
        updated_widget = self.sender()
        # config_headers contains the config_header (team) and the config_item (ie decal)
        config_headers = self.config_widgets_to_headers[updated_widget]

        # widget_list contains the spinbox and combobox (if it exists) associated with that item
        widget_list = self.config_headers_to_widgets[config_headers[0]][config_headers[1]]

        item_id = 0
        if len(widget_list) != 1:
            # there is a widget to update
            for widget_to_update in widget_list:
                if widget_to_update is updated_widget:
                    # no need to update itself, therefore continue
                    continue
                config_headers = self.config_widgets_to_headers[widget_to_update]
                category = self.config_headers_to_categories[config_headers[1]]
                if isinstance(widget_to_update, QtWidgets.QComboBox):
                    # update combobox by selecting decal_labels.index(self.categorised_items[updated_widget.value()])
                    item_id = updated_widget.value()
                    try:
                        # try to get item name from id in self.id_to_longlabel
                        item_name = self.id_to_longlabel[category][item_id]
                        try:
                            # try to select item in combobox
                            widget_to_update.setCurrentText(item_name)
                        except ValueError:
                            # print('Error: Item ID entered does not belong in this category. (%s)' % item_name)
                            widget_to_update.setCurrentText('Unknown')
                    except KeyError:
                        # unknown item selected, the id exists in no category
                        # print('Unknown item ID entered (%s) in %s' % (item_id, widget_to_update.objectName()))
                        widget_to_update.setCurrentText('Unknown')

                elif isinstance(widget_to_update, QtWidgets.QAbstractSpinBox):
                    item_longlabel = updated_widget.currentText()
                    if item_longlabel == "Unknown":
                        item_id = 0
                        continue
                        # get the id of the item, if this throws an error the dict got somehow messed up,
                        # since the combobox was originally loaded from the same dict
                    item_id = self.longlabel_to_id[category][item_longlabel]
                    # set the spinbox to the new value
                    widget_to_update.setValue(item_id)
        else:
            item_id = updated_widget.value()

        preset = self.get_current_preset()
        preset.config.set_value(config_headers[0], config_headers[1], item_id)
        if self.preset_autosave_checkbox.isChecked() and preset.config_path is not None and os.path.isfile(
                preset.config_path):
            self.save_preset_cfg(10)

    def load_selected_preset(self):
        super().load_selected_preset()
        for config_header_key, config_header in self.get_current_preset().config.headers.items():
            # for config_header in config, update widget value
            for config_value_key in config_header.values:
                if config_value_key == "name":
                    continue
                try:
                    widgets = self.config_headers_to_widgets[config_header_key][config_value_key]
                    try:
                        for widget in widgets:
                            # only update spinboxes - let comboboxes update through spinbox update detection.
                            if isinstance(widget, QtWidgets.QAbstractSpinBox):
                                # widget.setValue(config_header_value.value)
                                widget.setValue(config_header.get(config_value_key))
                    except:
                        # print("An error occurred")
                        pass
                except KeyError:
                    # print('Unknown loadout config header entry: %s' % config_value_key)
                    pass

    def create_config_headers_dicts(self):
        """
        Creates the config_headers_to_widgets and config_widgets_to_headers and config_headers_to_categories dicts
        """
        self.config_headers_to_widgets = {
            # blue stuff
            'Bot Loadout': {
                'team_color_id': (self.blue_primary_spinbox,),
                'custom_color_id': (self.blue_secondary_spinbox,),
                'car_id': (self.blue_car_spinbox, self.blue_car_combobox),
                'decal_id': (self.blue_decal_spinbox, self.blue_decal_combobox),
                'wheels_id': (self.blue_wheels_spinbox, self.blue_wheels_combobox),
                'boost_id': (self.blue_boost_spinbox, self.blue_boost_combobox),
                'antenna_id': (self.blue_antenna_spinbox, self.blue_antenna_combobox),
                'hat_id': (self.blue_hat_spinbox, self.blue_hat_combobox),
                'paint_finish_id': (self.blue_paint_finish_spinbox, self.blue_paint_finish_combobox),
                'custom_finish_id': (self.blue_custom_finish_spinbox, self.blue_custom_finish_combobox),
                'engine_audio_id': (self.blue_engine_spinbox, self.blue_engine_combobox),
                'trails_id': (self.blue_trails_spinbox, self.blue_trails_combobox),
                'goal_explosion_id': (self.blue_goal_explosion_spinbox, self.blue_goal_explosion_combobox)
            },
            'Bot Loadout Orange': {
                'team_color_id': (self.orange_primary_spinbox,),
                'custom_color_id': (self.orange_secondary_spinbox,),
                'car_id': (self.orange_car_spinbox, self.orange_car_combobox),
                'decal_id': (self.orange_decal_spinbox, self.orange_decal_combobox),
                'wheels_id': (self.orange_wheels_spinbox, self.orange_wheels_combobox),
                'boost_id': (self.orange_boost_spinbox, self.orange_boost_combobox),
                'antenna_id': (self.orange_antenna_spinbox, self.orange_antenna_combobox),
                'hat_id': (self.orange_hat_spinbox, self.orange_hat_combobox),
                'paint_finish_id': (self.orange_paint_finish_spinbox, self.orange_paint_finish_combobox),
                'custom_finish_id': (self.orange_custom_finish_spinbox, self.orange_custom_finish_combobox),
                'engine_audio_id': (self.orange_engine_spinbox, self.orange_engine_combobox),
                'trails_id': (self.orange_trails_spinbox, self.orange_trails_combobox),
                'goal_explosion_id': (self.orange_goal_explosion_spinbox, self.orange_goal_explosion_combobox)
            },
        }
        self.config_widgets_to_headers = {}
        for header_1, _field_dict in self.config_headers_to_widgets.items():
            for header_2, _widgets in _field_dict.items():
                for _widget in _widgets:
                    self.config_widgets_to_headers[_widget] = (header_1, header_2)

        self.config_headers_to_categories = {
            'car_id': 'Body',
            'decal_id': 'Decal',
            'wheels_id': 'Wheels',
            'boost_id': 'Rocket Boost',
            'antenna_id': 'Antenna',
            'hat_id': 'Topper',
            'paint_finish_id': 'Paint Finish',
            'custom_finish_id': 'Paint Finish',
            'engine_audio_id': 'Engine Audio',
            'trails_id': 'Trail',
            'goal_explosion_id': 'Goal Explosion'
        }

    def prefill_comboboxes(self):
        for widget, config_headers in self.config_widgets_to_headers.items():
            if isinstance(widget, QtWidgets.QComboBox):
                config_headers = self.config_widgets_to_headers[widget]
                config_category = self.config_headers_to_categories[config_headers[1]]
                sorted_list = list(self.longlabel_to_id[config_category].keys())
                sorted_list.sort()
                widget.addItems(sorted_list + ['Unknown'])

    @staticmethod
    def get_item_dicts():
        """
        Creates two item dicts and returns them, both are sorted by the Slot type
        :return: First dict is LongLabel to ID, second is ID to LongLabel
        """

        json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rocket_league_items.json')
        with open(json_path, 'r', encoding='utf8') as f:
            sorted_items = json.load(f, parse_int=True).items()

        longlabel_to_id = {}
        id_to_longlabel = {}
        for slot, items in sorted_items:
            type_longlabel_to_id = {item['LongLabel']: int(item['ID']) for item in items}
            type_id_to_longlabel = {int(item['ID']): item['LongLabel'] for item in items}
            longlabel_to_id[slot] = type_longlabel_to_id
            id_to_longlabel[slot] = type_id_to_longlabel

        return longlabel_to_id, id_to_longlabel


class AgentCustomisationDialog(BasePresetEditor, Ui_AgentPresetCustomiser):
    """
    The class extending BasePresetEditor for some agent config specific edits, e.g. selecting the agent file
    """

    def __init__(self, qt_gui):
        super().__init__(qt_gui, qt_gui.agent_presets, qt_gui.agent_preset_combobox, AgentPreset)

    def load_variables(self):
        super().load_variables()
        self.grid_layout = QtWidgets.QGridLayout(self.agent_parameters_groupbox)
        self.extra_parameter_widgets = []

    def load_preset_cfg(self) -> AgentPreset:
        return super().load_preset_cfg()

    def connect_functions(self):
        super().connect_functions()
        self.python_file_select_button.clicked.connect(self.load_python_file)

    def load_selected_preset(self):
        super().load_selected_preset()
        preset = self.get_current_preset()

        bot_parameters = preset.config["Bot Parameters"]
        self.preset_python_file_lineedit.setText(preset.config.get("Locations", "python_file"))

        self.add_parameters_to_gui(bot_parameters)

    def add_parameters_to_gui(self, bot_parameters):
        # clear layout
        while self.grid_layout.count():
            child_widget = self.grid_layout.takeAt(0).widget()
            self.grid_layout.removeWidget(child_widget)
            child_widget.setParent(None)
            child_widget.deleteLater()

        config_values = bot_parameters.values

        parent = self.agent_parameters_groupbox
        for row_no, (key, config_value) in enumerate(config_values.items()):
            label = QtWidgets.QLabel(str(key) + ':', parent)
            label.setObjectName("label_%s" % key)
            self.grid_layout.addWidget(label, row_no, 0)

            self.extra_parameter_widgets.append(label)

            def update_event(new_value, config_item=config_value):
                config_item.set_value(new_value)
                preset = self.get_current_preset()
                if self.preset_autosave_checkbox.isChecked() and preset.config_path is not None and os.path.isfile(
                        preset.config_path):
                    self.save_preset_cfg(10)

            if config_value.type is int:
                value_widget = QtWidgets.QSpinBox(parent)
                value_widget.setValue(int(config_value.get_value()))
                value_widget.valueChanged.connect(update_event)

            elif config_value.type is bool:
                value_widget = QtWidgets.QCheckBox(parent)
                value_widget.setChecked(bool(config_value.get_value()))
                value_widget.clicked.connect(update_event)

            elif config_value.type is float:
                value_widget = QtWidgets.QDoubleSpinBox(parent)
                value_widget.setValue(float(config_value.get_value()))
                value_widget.valueChanged.connect(update_event)

            else:
                # handle everything else as a string
                value_widget = QtWidgets.QLineEdit(parent)
                value_widget.setText(config_value.get_value())
                value_widget.textChanged.connect(update_event)

            value_widget.setObjectName('value_%s' % key)
            label.setToolTip(config_value.description)
            value_widget.setToolTip(config_value.description)
            self.grid_layout.addWidget(value_widget, row_no, 1)

        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 2)
        self.resize(self.minimumSizeHint())

    def load_python_file(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Agent Class', '', 'Python Files (*.py)')[0]
        if not file_path or not os.path.exists(file_path):
            return
        preset = self.get_current_preset()
        try:
            preset.load_agent_class(file_path)
        except (FileNotFoundError, ModuleNotFoundError) as e:
            self.popup_message(str(e), "Invalid Python File", QtWidgets.QMessageBox.Information)
            return

        if preset.config_path is None or not os.path.isfile(preset.config_path):
            start = get_python_root()
        else:
            start = os.path.dirname(preset.config_path)

        try:
            rel_path = os.path.relpath(file_path, start)
        except ValueError:
            rel_path = file_path

        preset.config.set_value("Locations", "python_file", rel_path)
        self.preset_python_file_lineedit.setText(rel_path)

        bot_parameters = preset.config["Bot Parameters"]
        self.add_parameters_to_gui(bot_parameters)
