# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'car_customisation_3.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(660, 495)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.presets_listwidget = QtWidgets.QListWidget(self.groupBox_3)
        self.presets_listwidget.setObjectName("presets_listwidget")
        self.horizontalLayout_2.addWidget(self.presets_listwidget)
        self.horizontalLayout.addWidget(self.groupBox_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_16 = QtWidgets.QLabel(self.groupBox_2)
        self.label_16.setObjectName("label_16")
        self.gridLayout_2.addWidget(self.label_16, 5, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.groupBox_2)
        self.label_17.setObjectName("label_17")
        self.gridLayout_2.addWidget(self.label_17, 3, 0, 1, 1)
        self.preset_save_pushbutton = QtWidgets.QPushButton(self.groupBox_2)
        self.preset_save_pushbutton.setObjectName("preset_save_pushbutton")
        self.gridLayout_2.addWidget(self.preset_save_pushbutton, 5, 11, 1, 1)
        self.preset_load_pushbutton = QtWidgets.QPushButton(self.groupBox_2)
        self.preset_load_pushbutton.setObjectName("preset_load_pushbutton")
        self.gridLayout_2.addWidget(self.preset_load_pushbutton, 5, 10, 1, 1)
        self.preset_autosave_checkbox = QtWidgets.QCheckBox(self.groupBox_2)
        self.preset_autosave_checkbox.setChecked(True)
        self.preset_autosave_checkbox.setObjectName("preset_autosave_checkbox")
        self.gridLayout_2.addWidget(self.preset_autosave_checkbox, 5, 12, 1, 1)
        self.preset_path_lineedit = QtWidgets.QLineEdit(self.groupBox_2)
        self.preset_path_lineedit.setObjectName("preset_path_lineedit")
        self.gridLayout_2.addWidget(self.preset_path_lineedit, 3, 1, 1, 12)
        self.preset_name_lineedit = QtWidgets.QLineEdit(self.groupBox_2)
        self.preset_name_lineedit.setObjectName("preset_name_lineedit")
        self.gridLayout_2.addWidget(self.preset_name_lineedit, 5, 1, 1, 9)
        self.verticalLayout_4.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setContentsMargins(-1, 0, -1, 8)
        self.gridLayout.setObjectName("gridLayout")
        self.label_14 = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 0, 2, 1, 2)
        self.label_15 = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 0, 5, 1, 2)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.blue_primary_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_primary_spinbox.setObjectName("blue_primary_spinbox")
        self.gridLayout.addWidget(self.blue_primary_spinbox, 1, 2, 1, 2)
        self.orange_primary_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_primary_spinbox.setObjectName("orange_primary_spinbox")
        self.gridLayout.addWidget(self.orange_primary_spinbox, 1, 5, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.orange_secondary_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_secondary_spinbox.setObjectName("orange_secondary_spinbox")
        self.gridLayout.addWidget(self.orange_secondary_spinbox, 2, 5, 1, 2)
        self.blue_secondary_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_secondary_spinbox.setObjectName("blue_secondary_spinbox")
        self.gridLayout.addWidget(self.blue_secondary_spinbox, 2, 2, 1, 2)
        self.blue_car_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_car_spinbox.setObjectName("blue_car_spinbox")
        self.gridLayout.addWidget(self.blue_car_spinbox, 3, 2, 1, 1)
        self.orange_car_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_car_spinbox.setObjectName("orange_car_spinbox")
        self.gridLayout.addWidget(self.orange_car_spinbox, 3, 5, 1, 1)
        self.orange_car_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_car_combobox.setObjectName("orange_car_combobox")
        self.gridLayout.addWidget(self.orange_car_combobox, 3, 6, 1, 1)
        self.blue_car_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_car_combobox.setObjectName("blue_car_combobox")
        self.gridLayout.addWidget(self.blue_car_combobox, 3, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.blue_decal_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_decal_spinbox.setObjectName("blue_decal_spinbox")
        self.gridLayout.addWidget(self.blue_decal_spinbox, 4, 2, 1, 1)
        self.blue_decal_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_decal_combobox.setObjectName("blue_decal_combobox")
        self.gridLayout.addWidget(self.blue_decal_combobox, 4, 3, 1, 1)
        self.orange_decal_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_decal_spinbox.setObjectName("orange_decal_spinbox")
        self.gridLayout.addWidget(self.orange_decal_spinbox, 4, 5, 1, 1)
        self.blue_wheels_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_wheels_spinbox.setObjectName("blue_wheels_spinbox")
        self.gridLayout.addWidget(self.blue_wheels_spinbox, 5, 2, 1, 1)
        self.blue_wheels_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_wheels_combobox.setObjectName("blue_wheels_combobox")
        self.gridLayout.addWidget(self.blue_wheels_combobox, 5, 3, 1, 1)
        self.orange_wheels_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_wheels_spinbox.setObjectName("orange_wheels_spinbox")
        self.gridLayout.addWidget(self.orange_wheels_spinbox, 5, 5, 1, 1)
        self.orange_decal_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_decal_combobox.setObjectName("orange_decal_combobox")
        self.gridLayout.addWidget(self.orange_decal_combobox, 4, 6, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.orange_boost_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_boost_spinbox.setObjectName("orange_boost_spinbox")
        self.gridLayout.addWidget(self.orange_boost_spinbox, 6, 5, 1, 1)
        self.blue_boost_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_boost_combobox.setObjectName("blue_boost_combobox")
        self.gridLayout.addWidget(self.blue_boost_combobox, 6, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.orange_wheels_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_wheels_combobox.setObjectName("orange_wheels_combobox")
        self.gridLayout.addWidget(self.orange_wheels_combobox, 5, 6, 1, 1)
        self.blue_boost_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_boost_spinbox.setObjectName("blue_boost_spinbox")
        self.gridLayout.addWidget(self.blue_boost_spinbox, 6, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 7, 0, 1, 1)
        self.blue_antenna_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_antenna_combobox.setObjectName("blue_antenna_combobox")
        self.gridLayout.addWidget(self.blue_antenna_combobox, 7, 3, 1, 1)
        self.blue_antenna_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_antenna_spinbox.setObjectName("blue_antenna_spinbox")
        self.gridLayout.addWidget(self.blue_antenna_spinbox, 7, 2, 1, 1)
        self.orange_antenna_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_antenna_spinbox.setObjectName("orange_antenna_spinbox")
        self.gridLayout.addWidget(self.orange_antenna_spinbox, 7, 5, 1, 1)
        self.orange_boost_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_boost_combobox.setObjectName("orange_boost_combobox")
        self.gridLayout.addWidget(self.orange_boost_combobox, 6, 6, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 8, 0, 1, 1)
        self.blue_hat_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_hat_spinbox.setObjectName("blue_hat_spinbox")
        self.gridLayout.addWidget(self.blue_hat_spinbox, 8, 2, 1, 1)
        self.blue_hat_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_hat_combobox.setObjectName("blue_hat_combobox")
        self.gridLayout.addWidget(self.blue_hat_combobox, 8, 3, 1, 1)
        self.orange_hat_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_hat_spinbox.setObjectName("orange_hat_spinbox")
        self.gridLayout.addWidget(self.orange_hat_spinbox, 8, 5, 1, 1)
        self.orange_antenna_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_antenna_combobox.setObjectName("orange_antenna_combobox")
        self.gridLayout.addWidget(self.orange_antenna_combobox, 7, 6, 1, 1)
        self.orange_hat_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_hat_combobox.setObjectName("orange_hat_combobox")
        self.gridLayout.addWidget(self.orange_hat_combobox, 8, 6, 1, 1)
        self.blue_paint_finish_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_paint_finish_spinbox.setObjectName("blue_paint_finish_spinbox")
        self.gridLayout.addWidget(self.blue_paint_finish_spinbox, 9, 2, 1, 1)
        self.blue_paint_finish_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_paint_finish_combobox.setObjectName("blue_paint_finish_combobox")
        self.gridLayout.addWidget(self.blue_paint_finish_combobox, 9, 3, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 9, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 10, 0, 1, 1)
        self.blue_custom_finish_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_custom_finish_combobox.setObjectName("blue_custom_finish_combobox")
        self.gridLayout.addWidget(self.blue_custom_finish_combobox, 10, 3, 1, 1)
        self.orange_paint_finish_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_paint_finish_combobox.setObjectName("orange_paint_finish_combobox")
        self.gridLayout.addWidget(self.orange_paint_finish_combobox, 9, 6, 1, 1)
        self.blue_custom_finish_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_custom_finish_spinbox.setObjectName("blue_custom_finish_spinbox")
        self.gridLayout.addWidget(self.blue_custom_finish_spinbox, 10, 2, 1, 1)
        self.orange_paint_finish_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_paint_finish_spinbox.setObjectName("orange_paint_finish_spinbox")
        self.gridLayout.addWidget(self.orange_paint_finish_spinbox, 9, 5, 1, 1)
        self.blue_engine_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_engine_spinbox.setObjectName("blue_engine_spinbox")
        self.gridLayout.addWidget(self.blue_engine_spinbox, 11, 2, 1, 1)
        self.blue_engine_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_engine_combobox.setObjectName("blue_engine_combobox")
        self.gridLayout.addWidget(self.blue_engine_combobox, 11, 3, 1, 1)
        self.orange_engine_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_engine_spinbox.setObjectName("orange_engine_spinbox")
        self.gridLayout.addWidget(self.orange_engine_spinbox, 11, 5, 1, 1)
        self.orange_custom_finish_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_custom_finish_spinbox.setObjectName("orange_custom_finish_spinbox")
        self.gridLayout.addWidget(self.orange_custom_finish_spinbox, 10, 5, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 11, 0, 1, 1)
        self.orange_custom_finish_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_custom_finish_combobox.setObjectName("orange_custom_finish_combobox")
        self.gridLayout.addWidget(self.orange_custom_finish_combobox, 10, 6, 1, 1)
        self.orange_engine_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_engine_combobox.setObjectName("orange_engine_combobox")
        self.gridLayout.addWidget(self.orange_engine_combobox, 11, 6, 1, 1)
        self.blue_trails_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_trails_combobox.setObjectName("blue_trails_combobox")
        self.gridLayout.addWidget(self.blue_trails_combobox, 12, 3, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 12, 0, 1, 1)
        self.blue_trails_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_trails_spinbox.setObjectName("blue_trails_spinbox")
        self.gridLayout.addWidget(self.blue_trails_spinbox, 12, 2, 1, 1)
        self.orange_trails_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_trails_spinbox.setObjectName("orange_trails_spinbox")
        self.gridLayout.addWidget(self.orange_trails_spinbox, 12, 5, 1, 1)
        self.orange_trails_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_trails_combobox.setObjectName("orange_trails_combobox")
        self.gridLayout.addWidget(self.orange_trails_combobox, 12, 6, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 13, 0, 1, 1)
        self.blue_goal_explosion_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.blue_goal_explosion_spinbox.setObjectName("blue_goal_explosion_spinbox")
        self.gridLayout.addWidget(self.blue_goal_explosion_spinbox, 13, 2, 1, 1)
        self.blue_goal_explosion_combobox = QtWidgets.QComboBox(self.groupBox)
        self.blue_goal_explosion_combobox.setObjectName("blue_goal_explosion_combobox")
        self.gridLayout.addWidget(self.blue_goal_explosion_combobox, 13, 3, 1, 1)
        self.orange_goal_explosion_combobox = QtWidgets.QComboBox(self.groupBox)
        self.orange_goal_explosion_combobox.setObjectName("orange_goal_explosion_combobox")
        self.gridLayout.addWidget(self.orange_goal_explosion_combobox, 13, 6, 1, 1)
        self.orange_goal_explosion_spinbox = QtWidgets.QSpinBox(self.groupBox)
        self.orange_goal_explosion_spinbox.setObjectName("orange_goal_explosion_spinbox")
        self.gridLayout.addWidget(self.orange_goal_explosion_spinbox, 13, 5, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.groupBox)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 1, 13, 1)
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 4, 13, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setColumnStretch(3, 2)
        self.gridLayout.setColumnStretch(4, 1)
        self.gridLayout.setColumnStretch(5, 1)
        self.gridLayout.setColumnStretch(6, 2)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.verticalLayout_4.setStretch(1, 1)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Preset Loadout Customiser"))
        self.groupBox_3.setTitle(_translate("Form", "Loadout presets"))
        self.groupBox_2.setTitle(_translate("Form", "Preset Config"))
        self.label_16.setText(_translate("Form", "Preset name:"))
        self.label_17.setText(_translate("Form", "File path:"))
        self.preset_save_pushbutton.setText(_translate("Form", "Save"))
        self.preset_load_pushbutton.setText(_translate("Form", "Load"))
        self.preset_autosave_checkbox.setText(_translate("Form", "Autosave"))
        self.groupBox.setTitle(_translate("Form", "Preset Loadout"))
        self.label_14.setText(_translate("Form", "Blue"))
        self.label_15.setText(_translate("Form", "Orange"))
        self.label.setText(_translate("Form", "Primary color:"))
        self.label_2.setText(_translate("Form", "Secondary color:"))
        self.label_3.setText(_translate("Form", "Car:"))
        self.label_4.setText(_translate("Form", "Decal:"))
        self.label_5.setText(_translate("Form", "Wheels:"))
        self.label_6.setText(_translate("Form", "Boost:"))
        self.label_7.setText(_translate("Form", "Antenna:"))
        self.label_8.setText(_translate("Form", "Hat:"))
        self.label_9.setText(_translate("Form", "Paint finish:"))
        self.label_10.setText(_translate("Form", "Custom finish:"))
        self.label_11.setText(_translate("Form", "Engine audio:"))
        self.label_12.setText(_translate("Form", "Trails:"))
        self.label_13.setText(_translate("Form", "Goal explosion:"))

