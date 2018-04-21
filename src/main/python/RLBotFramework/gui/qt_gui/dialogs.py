import os
import json
from PyQt5 import QtWidgets, QtCore

from RLBotFramework.gui.qt_gui.design.car_customisation import Ui_LoadoutPresetCustomiser
from RLBotFramework.gui.qt_gui.design.agent_customisation import Ui_AgentPresetCustomiser
from RLBotFramework.gui.presets import LoadoutPreset, AgentPreset


class CarCustomisationDialog(QtWidgets.QDialog, Ui_LoadoutPresetCustomiser):

    def __init__(self, qt_gui):
        super().__init__()
        self.setupUi(self)
        self.qt_gui = qt_gui
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        # this new variable is not a copy. it's the same dict.
        self.loadout_presets = self.qt_gui.loadout_presets

        self.create_config_headers_dicts()
        self.item_dicts = self.get_item_dicts()
        self.prefill_boxes()
        self.connect_functions()

        self.update_presets_widgets()

        # TESTING
        # TODO: Remove the testing bit.
        self.presets_listwidget.setCurrentRow(0)
        # self.load_selected_loadout_preset()

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

    def get_item_dicts(self):
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

    def get_current_preset(self):
        return self.loadout_presets[self.presets_listwidget.currentItem().text()]

    def prefill_boxes(self):
        for widget, config_headers in self.config_widgets_to_headers.items():
            if isinstance(widget, QtWidgets.QComboBox):
                config_headers = self.config_widgets_to_headers[widget]
                config_category = self.config_headers_to_categories[config_headers[1]]
                widget.addItems(self.item_dicts['categorised_items'][config_category] + ['Unknown'])

    def connect_functions(self):
        for config_widget in self.config_widgets_to_headers:
            if isinstance(config_widget, QtWidgets.QComboBox):
                config_widget.currentIndexChanged.connect(self.update_spinbox_and_combobox)
            elif isinstance(config_widget, QtWidgets.QAbstractSpinBox):
                # config_widget.editingFinished.connect(self.update_spinbox_and_combobox)
                config_widget.valueChanged.connect(self.update_spinbox_and_combobox)
        self.presets_listwidget.itemSelectionChanged.connect(self.load_selected_loadout_preset)
        self.preset_new_pushbutton.clicked.connect(self.add_new_preset)
        self.preset_load_pushbutton.clicked.connect(self.load_preset_cfg)
        self.preset_save_pushbutton.clicked.connect(lambda e: self.save_preset(time_out=0))

    def update_spinbox_and_combobox(self):
        # Updates the corresponding widget (ie update spinbox if combobox edited)
        updated_widget = self.sender()
        # config_headers contains the config_header (team) and the config_item (ie decal)
        config_headers = self.config_widgets_to_headers[updated_widget]

        # widget_list contains the spinbox and combobox (if it exists) associated with that item
        widget_list = self.config_headers_to_widgets[config_headers[0]][config_headers[1]]

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
                            print('Error: Item ID entered does not belong in this category. (%s)' % item_name)
                    except KeyError:
                        # unknown item selected, the id exists in no category
                        print('Unknown item ID entered (%s) in %s' % (item_id, widget_to_update.objectName()))
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
        preset = self.loadout_presets[preset_name]
        preset.config.set_value(config_headers[0], config_headers[1], item_id)

        if self.preset_autosave_checkbox.isChecked():
            self.save_preset(preset, 5000)

    def load_selected_loadout_preset(self):
        self.preset_autosave_checkbox.setChecked(False)

        preset = self.get_current_preset()

        for config_header_key, config_header in preset.config.headers.items():
            # for config_header in config, update widget value
            for config_value_key in config_header.values:
                try:
                    widgets = self.config_headers_to_widgets[config_header_key][config_value_key]
                    try:
                        for widget in widgets:
                            # only update spinboxes - let comboboxes update through spinbox update detection.
                            if isinstance(widget, QtWidgets.QAbstractSpinBox):
                                # widget.setValue(config_header_value.value)
                                widget.setValue(config_header.get(config_value_key))
                    except:
                        import traceback
                        traceback.print_exc()
                except KeyError:
                    print('Unknown loadout config header entry: %s' % config_value_key)

        # update file path manually
        self.preset_path_lineedit.setText(preset.config_path)
        self.preset_autosave_checkbox.setChecked(preset.auto_save)

    def add_new_preset(self):
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Create Loadout CFG', '', 'Config Files (*.cfg)', options=QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
        if not file_path or os.path.exists(file_path) or os.path.basename(file_path).replace(".cfg", "") in self.loadout_presets:
            return
        preset = LoadoutPreset(file_path)
        self.loadout_presets[preset.get_name()] = preset
        self.update_presets_widgets()
        self.presets_listwidget.setCurrentItem((self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0]))

    def load_preset_cfg(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Loadout CFG', '', 'Config Files (*.cfg)')[0]
        if not os.path.exists(file_path):
            return
        if os.path.basename(file_path).replace(".cfg", "") in self.loadout_presets:
            return
        preset = LoadoutPreset(file_path)
        self.loadout_presets[preset.get_name()] = preset
        self.update_presets_widgets()
        self.presets_listwidget.setCurrentItem((self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0]))

    def save_preset(self, preset=None, time_out=5000):
        if preset is None:
            preset_name = self.presets_listwidget.currentItem().text()
            preset = self.loadout_presets[preset_name]
        preset.save_config(time_out=time_out)

    def update_presets_widgets(self):
        # Resets the listwidget and then adds the items from the dictionary
        self.presets_listwidget.clear()
        self.presets_listwidget.addItems(list(self.loadout_presets.keys()))

        # Also updates the combobox which you can select the loadout preset for the bot through
        current_index = self.qt_gui.loadout_preset_combobox.currentIndex()
        current_text = self.qt_gui.loadout_preset_combobox.currentText()
        for i in range(self.qt_gui.loadout_preset_combobox.count()):
            if i != current_index:
                self.qt_gui.loadout_preset_combobox.removeItem(i)
        for s in self.loadout_presets:
            if s != current_text:
                self.qt_gui.loadout_preset_combobox.addItem(s)



class AgentCustomisationDialog(QtWidgets.QDialog, Ui_AgentPresetCustomiser):

    def __init__(self, qt_gui):
        super().__init__()
        self.setupUi(self)
        self.grid_layout = QtWidgets.QGridLayout(self.agent_parameters_groupbox)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.qt_gui = qt_gui
        self.agent_presets = self.qt_gui.agent_presets
        self.extra_parameter_widgets = []
        self.connect_functions()

        self.update_presets_widgets()

        self.presets_listwidget.setCurrentRow(0)

    def get_current_preset(self):
        return self.agent_presets[self.presets_listwidget.currentItem().text()]

    def connect_functions(self):
        self.presets_listwidget.itemSelectionChanged.connect(self.load_selected_agent_preset)

        self.preset_autosave_checkbox.clicked.connect(lambda e: self.get_current_preset().set_auto_save(e))

        self.preset_new_pushbutton.clicked.connect(self.add_new_preset)
        self.preset_load_pushbutton.clicked.connect(self.load_preset_cfg)
        self.preset_save_pushbutton.clicked.connect(lambda v: self.save_preset(time_out=0))
        self.python_file_select_button.clicked.connect(self.load_python_file)

    def load_selected_agent_preset(self):
        # Prevent unnecessary save by loading the values
        self.preset_autosave_checkbox.setChecked(False)

        preset = self.get_current_preset()

        self.preset_path_lineedit.setText(preset.config_path)
        self.preset_python_file_lineedit.setText(preset.config.get('Locations', 'python_file'))

        bot_parameters = preset.config["Bot Parameters"]

        self.add_parameters_to_gui(bot_parameters)

        self.preset_autosave_checkbox.setChecked(preset.auto_save)

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
                if self.preset_autosave_checkbox.isChecked():
                    self.save_preset()

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

        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        # print(self.grid_layout.geometry().height(), self.grid_layout.geometry().width())
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 2)
        self.resize(self.minimumSizeHint())

    def update_presets_widgets(self):
        self.presets_listwidget.clear()
        self.presets_listwidget.addItems(list(self.agent_presets.keys()))

        # Also updates the combobox which you can select the agent preset for the bot through
        current_preset = self.qt_gui.agent_preset_combobox.currentText()
        self.qt_gui.agent_preset_combobox.clear()
        self.qt_gui.agent_preset_combobox.addItems(list(self.agent_presets.keys()))
        self.qt_gui.agent_preset_combobox.setCurrentText(current_preset)

    def load_python_file(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Agent Class', '', 'Python Files (*.py)')[0]
        if not file_path or not os.path.exists(file_path) or self.get_current_preset().python_file_path == file_path:
            return
        preset = self.get_current_preset()
        preset.load_agent_class(file_path)
        preset.load()
        rel_path = os.path.relpath(file_path, os.path.dirname(preset.config_path))
        preset.config.set_value("Locations", "python_file", rel_path)
        self.preset_python_file_lineedit.setText(rel_path)

        bot_parameters = preset.config["Bot Parameters"]
        self.add_parameters_to_gui(bot_parameters)

    def add_new_preset(self):
        # First item of list is path, second is selected file type, which is always .cfg in our case
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Create Agent CFG', '', 'Config Files (*.cfg)', options=QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
        if not file_path or os.path.exists(file_path) or os.path.basename(file_path).replace(".cfg", "") in self.agent_presets:
            return
        preset = AgentPreset(file_path)
        self.agent_presets[preset.get_name()] = preset
        self.update_presets_widgets()
        self.presets_listwidget.setCurrentItem((self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0]))

    def load_preset_cfg(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Agent CFG', '', 'Config Files (*.cfg)')[0]
        if not os.path.exists(file_path):
            return
        if os.path.basename(file_path).replace(".cfg", "") in self.agent_presets:
            return
        preset = AgentPreset(file_path)
        self.agent_presets[preset.get_name()] = preset
        self.update_presets_widgets()
        self.presets_listwidget.setCurrentItem(self.presets_listwidget.findItems(preset.get_name(), QtCore.Qt.MatchExactly)[0])

    def save_preset(self, preset=None, time_out=5000):
        if preset is None:
            preset = self.get_current_preset()
        preset.save_config(time_out=time_out)

