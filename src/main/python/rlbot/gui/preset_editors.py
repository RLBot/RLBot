import os
import json
from PyQt5 import QtWidgets, QtCore
import configparser
import pathlib

from rlbot.gui.design.car_customisation import Ui_LoadoutPresetCustomiser
from rlbot.gui.design.agent_customisation import Ui_AgentPresetCustomiser
from rlbot.gui.presets import AgentPreset, LoadoutPreset
from rlbot.utils.file_util import get_python_root


class BasePresetEditor(QtWidgets.QWidget):
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
        return self.presets[self.presets_listwidget.currentItem().text()]

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
        self.presets_listwidget.addItems(list(self.presets.keys()))

        # Also updates the combobox which you can select the agent preset for the bot through
        current_text = self.root_combobox.currentText()
        self.root_combobox.clear()
        for s in self.presets:
            self.root_combobox.addItem(s)
        self.root_combobox.setCurrentText(current_text)

    def preset_name_changed(self):
        new_name = self.preset_name_lineedit.text()
        preset = self.get_current_preset()
        if preset.name == new_name:
            return
        del self.presets[preset.get_name()]
        self.presets[new_name] = preset
        old_index = self.root_combobox.currentIndex()
        current_index = self.root_combobox.findText(preset.get_name())
        self.root_combobox.removeItem(current_index)
        self.root_combobox.insertItem(current_index, new_name)
        self.root_combobox.setCurrentIndex(old_index)

        self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0].setText(new_name)
        preset.name = new_name

    def add_new_preset(self):
        preset = self.preset_class(self.validate_name("new preset", None))
        self.presets[preset.get_name()] = preset
        self.update_presets_widgets()
        self.presets_listwidget.setCurrentItem((self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0]))

    def load_preset_cfg(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Config', '', 'Config Files (*.cfg)')[0]
        if not os.path.isfile(file_path):
            return
        if pathlib.Path(file_path).suffix != '.cfg':
            self.popup_message("This file is not a config file!", "Invalid File Extension", QtWidgets.QMessageBox.Warning)
            return
        try:
            preset = self.preset_class(self.validate_name(pathlib.Path(file_path).stem, None), file_path)
        except configparser.NoSectionError:
            self.popup_message("This file does not have the right sections!", "Invalid Config File", QtWidgets.QMessageBox.Warning)
            return
        self.presets[preset.get_name()] = preset
        self.update_presets_widgets()
        self.presets_listwidget.setCurrentItem(self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0])

    def save_preset_cfg(self):
        preset = self.get_current_preset()
        if preset.config_path is None:
            file_path = os.path.realpath(QtWidgets.QFileDialog.getSaveFileName(self, 'Save Config', '', 'Config Files (*.cfg)')[0])
            if file_path is None or not file_path:
                return
            preset.config_path = file_path
            del self.presets[preset.get_name()]
            old_name = preset.name
            new_name = self.validate_name(pathlib.Path(preset.config_path).stem, preset)
            preset.name = new_name
            self.presets[preset.get_name()] = preset
            preset.save_config(time_out=0)
            old_index = self.root_combobox.currentIndex()
            current_index = self.root_combobox.findText(old_name)
            self.root_combobox.removeItem(current_index)
            self.root_combobox.insertItem(current_index, new_name)
            self.root_combobox.setCurrentIndex(old_index)

            self.presets_listwidget.findItems(old_name, QtCore.Qt.MatchExactly)[0].setText(new_name)
            self.load_selected_preset()

        else:
            preset.save_config(time_out=0)

    def validate_name(self, name, preset):
        if name in self.presets and self.presets[name] is not preset:
            i = 0
            while True:
                if name + " (" + str(i) + ")" in self.presets and self.presets[name + " (" + str(i) + ")"] is not preset:
                    i += 1
                else:
                    value = name + " (" + str(i) + ")"
                    return value
        else:
            return name

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
        self.item_dicts = self.get_item_dicts()
        self.prefill_boxes()

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
                if isinstance(widget_to_update, QtWidgets.QComboBox):
                    # update combobox by selecting decal_labels.index(self.categorised_items[updated_widget.value()])
                    item_id = updated_widget.value()
                    try:
                        # try to get item name from id in self.item_dicts
                        item_name = self.item_dicts['id_to_items'][item_id]['LongLabel']
                        try:
                            # try to select item in combobox
                            config_headers = self.config_widgets_to_headers[widget_to_update]
                            category = self.config_headers_to_categories[config_headers[1]]
                            _index = self.item_dicts['categorised_items'][category].index(item_name)
                            widget_to_update.setCurrentIndex(_index)
                        except ValueError:
                            # print('Error: Item ID entered does not belong in this category. (%s)' % item_name)
                            pass
                    except KeyError:
                        # unknown item selected, the id exists in no category
                        # print('Unknown item ID entered (%s) in %s' % (item_id, widget_to_update.objectName()))
                        pass
                        widget_to_update.setCurrentText('Unknown')

                elif isinstance(widget_to_update, QtWidgets.QAbstractSpinBox):
                    # update spinbox by widget.setValue(item_id where label = label)
                    item_longlabel = updated_widget.currentText()
                    if item_longlabel == "Unknown":
                        item_id = 0
                        continue
                    item_id = self.item_dicts['longlabels_to_id'][item_longlabel]
                    widget_to_update.setValue(item_id)
        else:
            item_id = updated_widget.value()
        preset_name = self.presets_listwidget.currentItem().text()
        preset = self.presets[preset_name]
        preset.config.set_value(config_headers[0], config_headers[1], item_id)

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
            'car_id': 'Bodies',
            'decal_id': 'Decals',
            'wheels_id': 'Wheels',
            'boost_id': 'Boosts',
            'antenna_id': 'Antennas',
            'hat_id': 'Toppers',
            'paint_finish_id': 'Paints',
            'custom_finish_id': 'Paints',
            'engine_audio_id': 'EngineAudio',
            'trails_id': 'Trails',
            'goal_explosion_id': 'GoalExplosions'
        }

    def prefill_boxes(self):
        for widget, config_headers in self.config_widgets_to_headers.items():
            if isinstance(widget, QtWidgets.QComboBox):
                config_headers = self.config_widgets_to_headers[widget]
                config_category = self.config_headers_to_categories[config_headers[1]]
                widget.addItems(self.item_dicts['categorised_items'][config_category] + ['Unknown'])

    @staticmethod
    def get_item_dicts():
        """
        Creates the id_to_items and items_to_id and categorised_items dicts.
        items_to_id is LongLabel: ID
        categorised_items is {category: [LongLabels]}
        :return:
        """

        json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'categorised_items.json')
        with open(json_path, 'r') as f:
            _id_to_items = json.load(f, parse_int=True)
            # convert keys to ints
            id_to_items = {int(_id): _item for _id, _item in _id_to_items.items()}

        longlabels_to_id = {_item_dict["LongLabel"]: int(_id) for _id, _item_dict in id_to_items.items()}

        categorised_items = {}
        for item in id_to_items.values():
            try:
                categorised_items[item['Category']].append(item['LongLabel'])
            except KeyError:
                # item['Category'] not in categorised_items yet.
                categorised_items[item['Category']] = [item['LongLabel']]

        dicts = {
            'id_to_items': id_to_items,
            'longlabels_to_id': longlabels_to_id,
            'categorised_items': categorised_items,
        }
        return dicts


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
                # if self.preset_autosave_checkbox.isChecked():
                #     self.save_preset()

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
        if not preset.load_agent_class(file_path):
            self.popup_message("This file does not extend BaseAgent, using BaseAgent", "Invalid Python File", QtWidgets.QMessageBox.Information)
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
