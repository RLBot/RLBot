# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_gui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(746, 603)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setSpacing(15)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_6 = QtWidgets.QLabel(self.groupBox_5)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_9.addWidget(self.label_6)
        self.cfg_file_path_lineedit = QtWidgets.QLineEdit(self.groupBox_5)
        self.cfg_file_path_lineedit.setReadOnly(True)
        self.cfg_file_path_lineedit.setObjectName("cfg_file_path_lineedit")
        self.horizontalLayout_9.addWidget(self.cfg_file_path_lineedit)
        self.cfg_load_pushbutton = QtWidgets.QPushButton(self.groupBox_5)
        self.cfg_load_pushbutton.setObjectName("cfg_load_pushbutton")
        self.horizontalLayout_9.addWidget(self.cfg_load_pushbutton)
        self.cfg_save_pushbutton = QtWidgets.QPushButton(self.groupBox_5)
        self.cfg_save_pushbutton.setObjectName("cfg_save_pushbutton")
        self.horizontalLayout_9.addWidget(self.cfg_save_pushbutton)
        self.cfg_autosave_checkbutton = QtWidgets.QCheckBox(self.groupBox_5)
        self.cfg_autosave_checkbutton.setObjectName("cfg_autosave_checkbutton")
        self.horizontalLayout_9.addWidget(self.cfg_autosave_checkbutton)
        self.verticalLayout_4.addWidget(self.groupBox_5)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_4.addWidget(self.line_2)
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.groupBox = QtWidgets.QGroupBox(self.frame_3)
        self.groupBox.setMinimumSize(QtCore.QSize(150, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_9 = QtWidgets.QFrame(self.groupBox)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame_9)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_17 = QtWidgets.QLabel(self.frame_9)
        self.label_17.setObjectName("label_17")
        self.gridLayout_4.addWidget(self.label_17, 0, 0, 1, 1)
        self.blue_name_lineedit = QtWidgets.QLineEdit(self.frame_9)
        self.blue_name_lineedit.setObjectName("blue_name_lineedit")
        self.gridLayout_4.addWidget(self.blue_name_lineedit, 0, 1, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.frame_9)
        self.label_18.setObjectName("label_18")
        self.gridLayout_4.addWidget(self.label_18, 1, 0, 1, 1)
        self.blue_color_spinbox = QtWidgets.QSpinBox(self.frame_9)
        self.blue_color_spinbox.setObjectName("blue_color_spinbox")
        self.gridLayout_4.addWidget(self.blue_color_spinbox, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame_9)
        self.blue_listwidget = QtWidgets.QListWidget(self.groupBox)
        self.blue_listwidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.blue_listwidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.blue_listwidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.blue_listwidget.setObjectName("blue_listwidget")
        self.verticalLayout.addWidget(self.blue_listwidget)
        self.frame_4 = QtWidgets.QFrame(self.groupBox)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.blue_plus_toolbutton = QtWidgets.QToolButton(self.frame_4)
        self.blue_plus_toolbutton.setObjectName("blue_plus_toolbutton")
        self.horizontalLayout_7.addWidget(self.blue_plus_toolbutton)
        self.blue_minus_toolbutton = QtWidgets.QToolButton(self.frame_4)
        self.blue_minus_toolbutton.setPopupMode(QtWidgets.QToolButton.DelayedPopup)
        self.blue_minus_toolbutton.setObjectName("blue_minus_toolbutton")
        self.horizontalLayout_7.addWidget(self.blue_minus_toolbutton)
        self.verticalLayout.addWidget(self.frame_4)
        self.horizontalLayout_6.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame_3)
        self.groupBox_2.setMinimumSize(QtCore.QSize(150, 0))
        self.groupBox_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_10 = QtWidgets.QFrame(self.groupBox_2)
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.frame_10)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_19 = QtWidgets.QLabel(self.frame_10)
        self.label_19.setObjectName("label_19")
        self.gridLayout_5.addWidget(self.label_19, 0, 0, 1, 1)
        self.orange_name_lineedit = QtWidgets.QLineEdit(self.frame_10)
        self.orange_name_lineedit.setObjectName("orange_name_lineedit")
        self.gridLayout_5.addWidget(self.orange_name_lineedit, 0, 1, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.frame_10)
        self.label_20.setObjectName("label_20")
        self.gridLayout_5.addWidget(self.label_20, 1, 0, 1, 1)
        self.orange_color_spinbox = QtWidgets.QSpinBox(self.frame_10)
        self.orange_color_spinbox.setObjectName("orange_color_spinbox")
        self.gridLayout_5.addWidget(self.orange_color_spinbox, 1, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.frame_10)
        self.orange_listwidget = QtWidgets.QListWidget(self.groupBox_2)
        self.orange_listwidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.orange_listwidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.orange_listwidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.orange_listwidget.setObjectName("orange_listwidget")
        self.verticalLayout_2.addWidget(self.orange_listwidget)
        self.frame_5 = QtWidgets.QFrame(self.groupBox_2)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.orange_plus_toolbutton = QtWidgets.QToolButton(self.frame_5)
        self.orange_plus_toolbutton.setObjectName("orange_plus_toolbutton")
        self.horizontalLayout_8.addWidget(self.orange_plus_toolbutton)
        self.orange_minus_toolbutton = QtWidgets.QToolButton(self.frame_5)
        self.orange_minus_toolbutton.setObjectName("orange_minus_toolbutton")
        self.horizontalLayout_8.addWidget(self.orange_minus_toolbutton)
        self.verticalLayout_2.addWidget(self.frame_5)
        self.horizontalLayout_6.addWidget(self.groupBox_2)
        self.bot_config_groupbox = QtWidgets.QGroupBox(self.frame_3)
        self.bot_config_groupbox.setEnabled(True)
        self.bot_config_groupbox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.bot_config_groupbox.setCheckable(False)
        self.bot_config_groupbox.setObjectName("bot_config_groupbox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.bot_config_groupbox)
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.bot_type_frame = QtWidgets.QFrame(self.bot_config_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bot_type_frame.sizePolicy().hasHeightForWidth())
        self.bot_type_frame.setSizePolicy(sizePolicy)
        self.bot_type_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.bot_type_frame.setObjectName("bot_type_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.bot_type_frame)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.bot_type_frame)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.bot_type_combobox = QtWidgets.QComboBox(self.bot_type_frame)
        self.bot_type_combobox.setObjectName("bot_type_combobox")
        self.bot_type_combobox.addItem("")
        self.bot_type_combobox.addItem("")
        self.bot_type_combobox.addItem("")
        self.bot_type_combobox.addItem("")
        self.horizontalLayout_2.addWidget(self.bot_type_combobox)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 3)
        self.verticalLayout_3.addWidget(self.bot_type_frame)
        self.line = QtWidgets.QFrame(self.bot_config_groupbox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.team_frame = QtWidgets.QFrame(self.bot_config_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.team_frame.sizePolicy().hasHeightForWidth())
        self.team_frame.setSizePolicy(sizePolicy)
        self.team_frame.setMinimumSize(QtCore.QSize(0, 30))
        self.team_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.team_frame.setObjectName("team_frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.team_frame)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.blue_radiobutton = QtWidgets.QRadioButton(self.team_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.blue_radiobutton.sizePolicy().hasHeightForWidth())
        self.blue_radiobutton.setSizePolicy(sizePolicy)
        self.blue_radiobutton.setMinimumSize(QtCore.QSize(50, 0))
        self.blue_radiobutton.setObjectName("blue_radiobutton")
        self.horizontalLayout_4.addWidget(self.blue_radiobutton)
        self.orange_radiobutton = QtWidgets.QRadioButton(self.team_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.orange_radiobutton.sizePolicy().hasHeightForWidth())
        self.orange_radiobutton.setSizePolicy(sizePolicy)
        self.orange_radiobutton.setObjectName("orange_radiobutton")
        self.horizontalLayout_4.addWidget(self.orange_radiobutton)
        self.verticalLayout_3.addWidget(self.team_frame)
        self.line_4 = QtWidgets.QFrame(self.bot_config_groupbox)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout_3.addWidget(self.line_4)
        self.rlbot_frame = QtWidgets.QFrame(self.bot_config_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rlbot_frame.sizePolicy().hasHeightForWidth())
        self.rlbot_frame.setSizePolicy(sizePolicy)
        self.rlbot_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.rlbot_frame.setLineWidth(1)
        self.rlbot_frame.setObjectName("rlbot_frame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.rlbot_frame)
        self.gridLayout_3.setVerticalSpacing(2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.agent_preset_toolbutton = QtWidgets.QPushButton(self.rlbot_frame)
        self.agent_preset_toolbutton.setObjectName("agent_preset_toolbutton")
        self.gridLayout_3.addWidget(self.agent_preset_toolbutton, 2, 1, 1, 2)
        self.agent_preset_combobox = QtWidgets.QComboBox(self.rlbot_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.agent_preset_combobox.sizePolicy().hasHeightForWidth())
        self.agent_preset_combobox.setSizePolicy(sizePolicy)
        self.agent_preset_combobox.setObjectName("agent_preset_combobox")
        self.gridLayout_3.addWidget(self.agent_preset_combobox, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.rlbot_frame)
        self.label_2.setMinimumSize(QtCore.QSize(0, 32))
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.preset_load_toplevel_pushbutton = QtWidgets.QPushButton(self.rlbot_frame)
        self.preset_load_toplevel_pushbutton.setObjectName("preset_load_toplevel_pushbutton")
        self.gridLayout_3.addWidget(self.preset_load_toplevel_pushbutton, 0, 2, 1, 1)
        self.verticalLayout_3.addWidget(self.rlbot_frame)
        self.psyonix_bot_frame = QtWidgets.QFrame(self.bot_config_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.psyonix_bot_frame.sizePolicy().hasHeightForWidth())
        self.psyonix_bot_frame.setSizePolicy(sizePolicy)
        self.psyonix_bot_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.psyonix_bot_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.psyonix_bot_frame.setObjectName("psyonix_bot_frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.psyonix_bot_frame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QtWidgets.QLabel(self.psyonix_bot_frame)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.bot_level_slider = QtWidgets.QSlider(self.psyonix_bot_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bot_level_slider.sizePolicy().hasHeightForWidth())
        self.bot_level_slider.setSizePolicy(sizePolicy)
        self.bot_level_slider.setLocale(QtCore.QLocale(QtCore.QLocale.Dutch, QtCore.QLocale.Netherlands))
        self.bot_level_slider.setMaximum(100)
        self.bot_level_slider.setTracking(False)
        self.bot_level_slider.setOrientation(QtCore.Qt.Horizontal)
        self.bot_level_slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.bot_level_slider.setTickInterval(50)
        self.bot_level_slider.setObjectName("bot_level_slider")
        self.horizontalLayout_3.addWidget(self.bot_level_slider)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 5)
        self.verticalLayout_3.addWidget(self.psyonix_bot_frame)
        self.extra_line = QtWidgets.QFrame(self.bot_config_groupbox)
        self.extra_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.extra_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.extra_line.setObjectName("extra_line")
        self.verticalLayout_3.addWidget(self.extra_line)
        self.appearance_frame = QtWidgets.QFrame(self.bot_config_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.appearance_frame.sizePolicy().hasHeightForWidth())
        self.appearance_frame.setSizePolicy(sizePolicy)
        self.appearance_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.appearance_frame.setObjectName("appearance_frame")
        self.gridLayout = QtWidgets.QGridLayout(self.appearance_frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.appearance_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.appearance_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.loadout_preset_combobox = QtWidgets.QComboBox(self.appearance_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadout_preset_combobox.sizePolicy().hasHeightForWidth())
        self.loadout_preset_combobox.setSizePolicy(sizePolicy)
        self.loadout_preset_combobox.setObjectName("loadout_preset_combobox")
        self.gridLayout.addWidget(self.loadout_preset_combobox, 1, 1, 1, 1)
        self.loadout_preset_toolbutton = QtWidgets.QPushButton(self.appearance_frame)
        self.loadout_preset_toolbutton.setObjectName("loadout_preset_toolbutton")
        self.gridLayout.addWidget(self.loadout_preset_toolbutton, 1, 2, 1, 1)
        self.ign_lineedit = QtWidgets.QLineEdit(self.appearance_frame)
        self.ign_lineedit.setObjectName("ign_lineedit")
        self.gridLayout.addWidget(self.ign_lineedit, 0, 1, 1, 2)
        self.verticalLayout_3.addWidget(self.appearance_frame)
        self.button_frame = QtWidgets.QFrame(self.bot_config_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_frame.sizePolicy().hasHeightForWidth())
        self.button_frame.setSizePolicy(sizePolicy)
        self.button_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.button_frame.setObjectName("button_frame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.button_frame)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_3.addWidget(self.button_frame)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_6.addWidget(self.bot_config_groupbox)
        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 1)
        self.horizontalLayout_6.setStretch(2, 2)
        self.verticalLayout_4.addWidget(self.frame_3)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_4.addWidget(self.line_3)
        self.match_settings_groupbox = QtWidgets.QGroupBox(self.centralwidget)
        self.match_settings_groupbox.setAlignment(QtCore.Qt.AlignCenter)
        self.match_settings_groupbox.setObjectName("match_settings_groupbox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.match_settings_groupbox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mode_type_combobox = QtWidgets.QComboBox(self.match_settings_groupbox)
        self.mode_type_combobox.setObjectName("mode_type_combobox")
        self.gridLayout_2.addWidget(self.mode_type_combobox, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.match_settings_groupbox)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)
        self.map_type_combobox = QtWidgets.QComboBox(self.match_settings_groupbox)
        self.map_type_combobox.setObjectName("map_type_combobox")
        self.gridLayout_2.addWidget(self.map_type_combobox, 1, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.match_settings_groupbox)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 1, 0, 1, 1)
        self.skip_replays_checkbox = QtWidgets.QCheckBox(self.match_settings_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.skip_replays_checkbox.sizePolicy().hasHeightForWidth())
        self.skip_replays_checkbox.setSizePolicy(sizePolicy)
        self.skip_replays_checkbox.setObjectName("skip_replays_checkbox")
        self.gridLayout_2.addWidget(self.skip_replays_checkbox, 0, 4, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.match_settings_groupbox)
        self.label_14.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 1, 3, 1, 1)
        self.instant_start_checkbox = QtWidgets.QCheckBox(self.match_settings_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.instant_start_checkbox.sizePolicy().hasHeightForWidth())
        self.instant_start_checkbox.setSizePolicy(sizePolicy)
        self.instant_start_checkbox.setObjectName("instant_start_checkbox")
        self.gridLayout_2.addWidget(self.instant_start_checkbox, 1, 4, 1, 1)
        self.line_6 = QtWidgets.QFrame(self.match_settings_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_6.sizePolicy().hasHeightForWidth())
        self.line_6.setSizePolicy(sizePolicy)
        self.line_6.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.gridLayout_2.addWidget(self.line_6, 0, 2, 2, 1)
        self.line_7 = QtWidgets.QFrame(self.match_settings_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_7.sizePolicy().hasHeightForWidth())
        self.line_7.setSizePolicy(sizePolicy)
        self.line_7.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.gridLayout_2.addWidget(self.line_7, 0, 5, 2, 1)
        self.frame_7 = QtWidgets.QFrame(self.match_settings_groupbox)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.edit_mutators_pushbutton = QtWidgets.QPushButton(self.frame_7)
        self.edit_mutators_pushbutton.setObjectName("edit_mutators_pushbutton")
        self.horizontalLayout_11.addWidget(self.edit_mutators_pushbutton)
        self.gridLayout_2.addWidget(self.frame_7, 0, 6, 2, 1)
        self.label_13 = QtWidgets.QLabel(self.match_settings_groupbox)
        self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 0, 3, 1, 1)
        self.gridLayout_2.setColumnStretch(1, 2)
        self.gridLayout_2.setColumnStretch(2, 1)
        self.gridLayout_2.setColumnStretch(4, 2)
        self.gridLayout_2.setColumnStretch(5, 1)
        self.gridLayout_2.setColumnStretch(6, 5)
        self.verticalLayout_4.addWidget(self.match_settings_groupbox)
        self.frame_6 = QtWidgets.QFrame(self.centralwidget)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_10.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.kill_bots_pushbutton = QtWidgets.QPushButton(self.frame_6)
        self.kill_bots_pushbutton.setObjectName("kill_bots_pushbutton")
        self.horizontalLayout_10.addWidget(self.kill_bots_pushbutton)
        spacerItem1 = QtWidgets.QSpacerItem(489, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem1)
        self.run_button = QtWidgets.QCommandLinkButton(self.frame_6)
        self.run_button.setStyleSheet("")
        self.run_button.setObjectName("run_button")
        self.horizontalLayout_10.addWidget(self.run_button)
        self.verticalLayout_4.addWidget(self.frame_6)
        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_4.setStretch(2, 5)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.bot_type_combobox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RLBot"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Overall Config"))
        self.label_6.setText(_translate("MainWindow", "CFG File Path:"))
        self.cfg_load_pushbutton.setText(_translate("MainWindow", "Load"))
        self.cfg_save_pushbutton.setText(_translate("MainWindow", "Save"))
        self.cfg_autosave_checkbutton.setText(_translate("MainWindow", "Autosave"))
        self.groupBox.setTitle(_translate("MainWindow", "Blue"))
        self.label_17.setText(_translate("MainWindow", "Name:"))
        self.blue_name_lineedit.setText(_translate("MainWindow", "Blue"))
        self.label_18.setText(_translate("MainWindow", "Colour:"))
        self.blue_plus_toolbutton.setText(_translate("MainWindow", "+"))
        self.blue_minus_toolbutton.setText(_translate("MainWindow", "−"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Orange"))
        self.label_19.setText(_translate("MainWindow", "Name:"))
        self.orange_name_lineedit.setText(_translate("MainWindow", "Orange"))
        self.label_20.setText(_translate("MainWindow", "Colour:"))
        self.orange_plus_toolbutton.setText(_translate("MainWindow", "+"))
        self.orange_minus_toolbutton.setText(_translate("MainWindow", "−"))
        self.bot_config_groupbox.setTitle(_translate("MainWindow", "Bot Config"))
        self.label.setText(_translate("MainWindow", "Bot Type:"))
        self.bot_type_combobox.setToolTip(_translate("MainWindow", "Select bot"))
        self.bot_type_combobox.setItemText(0, _translate("MainWindow", "Human"))
        self.bot_type_combobox.setItemText(1, _translate("MainWindow", "Psyonix"))
        self.bot_type_combobox.setItemText(2, _translate("MainWindow", "RLBot"))
        self.bot_type_combobox.setItemText(3, _translate("MainWindow", "Party Member Bot"))
        self.blue_radiobutton.setText(_translate("MainWindow", "Blue"))
        self.orange_radiobutton.setText(_translate("MainWindow", "Orange"))
        self.agent_preset_toolbutton.setText(_translate("MainWindow", "Customize Presets..."))
        self.label_2.setText(_translate("MainWindow", "Agent Preset:"))
        self.preset_load_toplevel_pushbutton.setText(_translate("MainWindow", "Load..."))
        self.label_5.setText(_translate("MainWindow", "Bot Level:"))
        self.label_4.setText(_translate("MainWindow", "Appearance Override"))
        self.label_3.setText(_translate("MainWindow", "In-Game Name"))
        self.loadout_preset_toolbutton.setText(_translate("MainWindow", "..."))
        self.match_settings_groupbox.setTitle(_translate("MainWindow", "Match Settings"))
        self.label_11.setText(_translate("MainWindow", "Mode:"))
        self.label_12.setText(_translate("MainWindow", "Map:"))
        self.label_14.setText(_translate("MainWindow", "Instant Start:"))
        self.edit_mutators_pushbutton.setText(_translate("MainWindow", "Edit Mutators"))
        self.label_13.setText(_translate("MainWindow", "Skip Replays:"))
        self.kill_bots_pushbutton.setText(_translate("MainWindow", "Kill Bots"))
        self.run_button.setText(_translate("MainWindow", "RUN"))

