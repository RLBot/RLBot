import os
import sys
import json
from PyQt5 import QtWidgets, QtCore, QtGui

from RLBotFramework.gui.qt_gui.car_customisation import Ui_Form



class CarCustomisationDialog(QtWidgets.QDialog, Ui_Form):

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

    def create_config_headers_dicts(self):
        """
        Creates the config_headers_to_widgets and config_widgets_to_headers dicts
        :return:
        """
        self.config_headers_to_widgets = {
            # blue stuff
            'Bot Loadout': {
                'team_color_id': (self.blue_primary_spinbox, ),
                'custom_color_id': (self.blue_secondary_spinbox, ),
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
                'team_color_id': (self.orange_primary_spinbox, ),
                'custom_color_id': (self.orange_secondary_spinbox, ),
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
                widget.addItems(self.item_dicts['categorised_items'][config_category])



    def connect_functions(self):
        for config_widget in self.config_widgets_to_headers:
            if isinstance(config_widget, QtWidgets.QComboBox):
                config_widget.currentIndexChanged.connect(self.update_spinbox_and_combobox)
            elif isinstance(config_widget, QtWidgets.QAbstractSpinBox):
                config_widget.editingFinished.connect(self.update_spinbox_and_combobox)
        pass

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

    def load_loadout_preset(self):
        pass

    def update_presets_listwidget(self):
        loadout_presets_names = self.loadout_presets

        for loadout_preset_name, loadout_preset in self.loadout_presets.items():
            print('loadouts:', loadout_preset_name, str(loadout_preset))
            # print(str(loadout_preset.config))
            # print(loadout_preset.config.sections)