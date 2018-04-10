import os
import sys
import json
from PyQt5 import QtWidgets, QtCore, QtGui

from RLBotFramework.gui.qt_gui.car_customisation import Ui_LoadoutPresetCustomiser
from RLBotFramework.gui.qt_gui.agent_customisation import Ui_AgentPresetCustomiser

class CarCustomisationDialog(QtWidgets.QDialog, Ui_LoadoutPresetCustomiser):

    def __init__(self, qt_gui):
        super().__init__()
        self.setupUi(self)
        self.qt_gui = qt_gui
        # this new variable is not a copy. it's the same dict.
        self.loadout_presets = self.qt_gui.loadout_presets

        self.create_config_headers_dicts()
        self.item_dicts = self.get_item_dicts()
        self.prefill_boxes()
        self.connect_functions()

        self.update_presets_listwidget()

        # TESTING
        # TODO: Remove the testing bit.
        self.presets_listwidget.setCurrentRow(0)
        # self.load_selected_loadout_preset()

    def create_config_headers_dicts(self):
        """
        Creates the config_headers_to_widgets and config_widgets_to_headers and config_headers_to_categories dicts
        :return:
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
        self.preset_save_pushbutton.clicked.connect(self.save_preset)

    def update_spinbox_and_combobox(self):
        # Updates the corresponding widget (ie update spinbox if combobox edited)
        updated_widget = self.sender()
        # print(updated_widget.objectName())
        config_headers = self.config_widgets_to_headers[updated_widget]

        widget_list = self.config_headers_to_widgets[config_headers[0]][config_headers[1]]
        if len(widget_list) == 1:
            # there is no associated thing to update (e.g. team_color_id)
            return
        for widget_to_update in widget_list:
            if widget_to_update is updated_widget:
                # don't bother updating yourself
                continue
            if isinstance(widget_to_update, QtWidgets.QComboBox):
                # update combobox by selecting decal_labels.index(self.categorised_items[updated_widget.value()])
                try:
                    # try to get item name from id in self.item_dicts
                    item_id = updated_widget.value()
                    item_name = self.item_dicts['id_to_items'][item_id]['LongLabel']
                    try:
                        # try to select item in combobox
                        config_headers = self.config_widgets_to_headers[widget_to_update]
                        category = self.config_headers_to_categories[config_headers[1]]
                        _index = self.item_dicts['categorised_items'][category].index(item_name)
                        widget_to_update.setCurrentIndex(_index)
                    except ValueError:
                        print('Error: Item ID entered does not belong in this category. (%s)' % item_name)
                        # import traceback
                        # traceback.print_exc()
                except KeyError:
                    # unknown item selected
                    print('Unknown item ID entered (%s)' % item_id)
                    widget_to_update.setCurrentText('Unknown')
            elif isinstance(widget_to_update, QtWidgets.QAbstractSpinBox):
                # update spinbox by widget.setValue(item_id where label = label)
                item_longlabel = updated_widget.currentText()
                item_id = self.item_dicts['longlabels_to_id'][item_longlabel]
                widget_to_update.setValue(item_id)

    def load_selected_loadout_preset(self):
        preset_name = self.presets_listwidget.currentItem().text()
        preset = self.loadout_presets[preset_name]

        # print(preset)
        # print(str(preset.config))
        # print(preset.config.headers.values)
        for _key, config_header in preset.config.headers.items():
            # print(_key)
            # print(config_header.values)

            # for config_header in config, update widget value
            for config_header_key in config_header.values:
                try:
                    widgets = self.config_headers_to_widgets[_key][config_header_key]
                    try:
                        for widget in widgets:
                            # only update spinboxes - let comboboxes update.
                            if isinstance(widget, QtWidgets.QAbstractSpinBox):
                                # widget.setValue(config_header_value.value)
                                widget.setValue(config_header.get(config_header_key))
                    except:
                        import traceback
                        traceback.print_exc()
                except KeyError:
                    print('Unknown loadout config header entry: %s' % config_header_key)

        # update file path manually
        self.preset_path_lineedit.setText(preset.config_path)
        # print(header.values)

    def add_new_preset(self):
        # TODO: Something. Maybe let user create file?
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Create Loadout CFG', '', 'Config Files (*.cfg)')
        print(file_name)
        pass

    def load_preset_cfg(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Loadout CFG', '', 'Config Files (*.cfg)')
        print(file_name)
        # TODO: Add selected preset to self.loadout_presets then refresh listwidget

    def save_preset(self):
        preset_name = self.presets_listwidget.currentItem().text()
        preset = self.loadout_presets[preset_name]
        print('save to %s' % preset.config_path)
        print('Is preset cfg path same as the path in lineconfig?')
        print('%s' % self.preset_path_lineedit.text() == preset.config_path)
        # TODO: Save preset. idk what you want to do if lineedit.text != preset.config_path.

    def update_presets_listwidget(self):
        # for loadout_preset_name, loadout_preset in self.loadout_presets.items():  # Essentially the same as
        # print('loadouts:', loadout_preset_name, str(loadout_preset))

        self.presets_listwidget.clear()
        self.presets_listwidget.addItems(list(self.loadout_presets.keys()))
        # print(list(self.loadout_presets.keys()))


class AgentCustomisationDialog(QtWidgets.QDialog, Ui_AgentPresetCustomiser):

    def __init__(self, qt_gui):
        super().__init__()
        self.setupUi(self)
        self.grid_layout = QtWidgets.QGridLayout(self.agent_parameters_groupbox)

        self.qt_gui = qt_gui
        self.agent_presets = self.qt_gui.agent_presets
        self.extra_parameter_widgets = []

        self.update_presets_listwidget()

        # TEST STUFF
        self.presets_listwidget.setCurrentRow(0)
        self.load_selected_agent_preset()



    def connect_functions(self):
        self.presets_listwidget.itemSelectionChanged.connect(self.load_selected_agent_preset)

        self.preset_new_pushbutton.clicked.connect(self.add_new_preset)
        self.preset_load_pushbutton.clicked.connect(self.load_preset_cfg)
        self.preset_save_pushbutton.clicked.connect(self.save_preset)

    def load_selected_agent_preset(self):
        preset_name = self.presets_listwidget.currentItem().text()
        preset = self.agent_presets[preset_name]
        print(preset)
        print(preset.config.get_header('Locations').get('python_file'))

        self.preset_path_lineedit.setText(preset.config_path)
        self.preset_python_file_lineedit.setText(preset.config.get_header('Locations').get('python_file'))

        bot_parameters = preset.config.raw_config_parser['Bot Parameters']

        self.add_parameters_to_gui(bot_parameters)

    def add_parameters_to_gui(self, bot_parameters):
        # clear layout
        while self.grid_layout.count():
            child_widget = self.grid_layout.takeAt(0).widget()
            self.grid_layout.removeWidget(child_widget)
            child_widget.setParent(None)
            child_widget.deleteLater()

        params = list(bot_parameters.items())
        params_count = len(params)

        parent = self.agent_parameters_groupbox
        for row_no, (key, value) in enumerate(params):
            label = QtWidgets.QLabel(str(key) + ':', parent)
            label.setObjectName("label_%s" % key)
            self.grid_layout.addWidget(label, row_no, 0)

            self.extra_parameter_widgets.append(label)
            try:
                bot_parameters.getint(key)
                _value_type = int
            except ValueError:
                try:
                    bot_parameters.getboolean(key)
                    _value_type = bool
                except ValueError:
                    try:
                        bot_parameters.getfloat(key)
                        _value_type = float
                    except ValueError:
                        print("Unknown value type for %s (key: %s)" % value, key)
            if _value_type is int:
                print("INT")
                value_widget = QtWidgets.QSpinBox(parent)
                value_widget.setValue(int(value))
            elif _value_type is bool:
                print("BOOL")
                value_widget = QtWidgets.QCheckBox(parent)
                value_widget.setChecked(bool(value))
            elif _value_type is float:
                print("FLOAT")
                value_widget = QtWidgets.QDoubleSpinBox(parent)
                value_widget.setValue(float(value))

            value_widget.setObjectName('value_%s' % key)
            self.grid_layout.addWidget(value_widget, row_no, 1)

            # print(value.type, 'asfaasf')


        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        # print(self.grid_layout.geometry().height(), self.grid_layout.geometry().width())
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 2)
        self.resize(self.minimumSizeHint())



    def update_presets_listwidget(self):
        self.presets_listwidget.clear()
        self.presets_listwidget.addItems(list(self.agent_presets.keys()))


    def add_new_preset(self):
        # TODO: Something. Maybe let user create file?
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Create Agent CFG', '', 'Config Files (*.cfg)')
        print(file_name)
        pass

    def load_preset_cfg(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Agent CFG', '', 'Config Files (*.cfg)')
        print(file_name)
        # TODO: Add selected preset to self.agent_presets then refresh listwidget

    def save_preset(self):
        preset_name = self.presets_listwidget.currentItem().text()
        preset = self.agent_presets[preset_name]
        print('save to %s' % preset.config_path)
        print('Is preset cfg path same as the path in lineconfig?')
        print('%s' % self.preset_path_lineedit.text() == preset.config_path)
        # TODO: Save preset. idk what you want to do if lineedit.text != preset.config_path.

