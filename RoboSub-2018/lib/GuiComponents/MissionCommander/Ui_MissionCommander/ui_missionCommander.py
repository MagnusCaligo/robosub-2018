# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_missionCommander.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MissionCommander(object):
    def setupUi(self, MissionCommander):
        MissionCommander.setObjectName(_fromUtf8("MissionCommander"))
        MissionCommander.resize(1088, 626)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(MissionCommander)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout_5.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.saveMissionList = QtGui.QPushButton(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveMissionList.sizePolicy().hasHeightForWidth())
        self.saveMissionList.setSizePolicy(sizePolicy)
        self.saveMissionList.setObjectName(_fromUtf8("saveMissionList"))
        self.horizontalLayout_5.addWidget(self.saveMissionList)
        self.loadMissionList = QtGui.QPushButton(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadMissionList.sizePolicy().hasHeightForWidth())
        self.loadMissionList.setSizePolicy(sizePolicy)
        self.loadMissionList.setObjectName(_fromUtf8("loadMissionList"))
        self.horizontalLayout_5.addWidget(self.loadMissionList)
        self.gridLayout.addLayout(self.horizontalLayout_5, 8, 0, 1, 1)
        self.missionTypeCB = QtGui.QComboBox(MissionCommander)
        self.missionTypeCB.setObjectName(_fromUtf8("missionTypeCB"))
        self.missionTypeCB.addItem(_fromUtf8(""))
        self.missionTypeCB.addItem(_fromUtf8(""))
        self.missionTypeCB.addItem(_fromUtf8(""))
        self.missionTypeCB.addItem(_fromUtf8(""))
        self.missionTypeCB.addItem(_fromUtf8(""))
        self.missionTypeCB.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.missionTypeCB, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.lookLeft = QtGui.QRadioButton(MissionCommander)
        self.lookLeft.setChecked(True)
        self.lookLeft.setObjectName(_fromUtf8("lookLeft"))
        self.horizontalLayout_4.addWidget(self.lookLeft)
        self.lookRight = QtGui.QRadioButton(MissionCommander)
        self.lookRight.setObjectName(_fromUtf8("lookRight"))
        self.horizontalLayout_4.addWidget(self.lookRight)
        self.gridLayout.addLayout(self.horizontalLayout_4, 5, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.maxTimeLineEdit = QtGui.QLineEdit(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.maxTimeLineEdit.sizePolicy().hasHeightForWidth())
        self.maxTimeLineEdit.setSizePolicy(sizePolicy)
        self.maxTimeLineEdit.setObjectName(_fromUtf8("maxTimeLineEdit"))
        self.verticalLayout.addWidget(self.maxTimeLineEdit)
        self.gridLayout.addLayout(self.verticalLayout, 3, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.checkBox_3 = QtGui.QCheckBox(MissionCommander)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.gridLayout_2.addWidget(self.checkBox_3, 2, 0, 1, 1)
        self.checkBox_4 = QtGui.QCheckBox(MissionCommander)
        self.checkBox_4.setObjectName(_fromUtf8("checkBox_4"))
        self.gridLayout_2.addWidget(self.checkBox_4, 2, 1, 1, 1)
        self.useLaser = QtGui.QCheckBox(MissionCommander)
        self.useLaser.setObjectName(_fromUtf8("useLaser"))
        self.gridLayout_2.addWidget(self.useLaser, 1, 1, 1, 1)
        self.useKalmanFilter = QtGui.QCheckBox(MissionCommander)
        self.useKalmanFilter.setChecked(True)
        self.useKalmanFilter.setObjectName(_fromUtf8("useKalmanFilter"))
        self.gridLayout_2.addWidget(self.useKalmanFilter, 1, 0, 1, 1)
        self.parameterStringInputs = QtGui.QPlainTextEdit(MissionCommander)
        self.parameterStringInputs.setObjectName(_fromUtf8("parameterStringInputs"))
        self.gridLayout_2.addWidget(self.parameterStringInputs, 3, 0, 1, 2)
        self.gridLayout.addLayout(self.gridLayout_2, 6, 0, 1, 1)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.useGeneralWaypoint = QtGui.QLineEdit(MissionCommander)
        self.useGeneralWaypoint.setObjectName(_fromUtf8("useGeneralWaypoint"))
        self.verticalLayout_3.addWidget(self.useGeneralWaypoint)
        self.gridLayout.addLayout(self.verticalLayout_3, 4, 0, 1, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.missionNameLineEdit = QtGui.QLineEdit(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.missionNameLineEdit.sizePolicy().hasHeightForWidth())
        self.missionNameLineEdit.setSizePolicy(sizePolicy)
        self.missionNameLineEdit.setObjectName(_fromUtf8("missionNameLineEdit"))
        self.verticalLayout_2.addWidget(self.missionNameLineEdit)
        self.gridLayout.addLayout(self.verticalLayout_2, 2, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.addMissionButton = QtGui.QPushButton(MissionCommander)
        self.addMissionButton.setObjectName(_fromUtf8("addMissionButton"))
        self.horizontalLayout_3.addWidget(self.addMissionButton)
        self.removeMissionButton = QtGui.QPushButton(MissionCommander)
        self.removeMissionButton.setObjectName(_fromUtf8("removeMissionButton"))
        self.horizontalLayout_3.addWidget(self.removeMissionButton)
        self.gridLayout.addLayout(self.horizontalLayout_3, 7, 0, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_4 = QtGui.QLabel(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_7.addWidget(self.label_4)
        self.northTranslation = QtGui.QDoubleSpinBox(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.northTranslation.sizePolicy().hasHeightForWidth())
        self.northTranslation.setSizePolicy(sizePolicy)
        self.northTranslation.setObjectName(_fromUtf8("northTranslation"))
        self.verticalLayout_7.addWidget(self.northTranslation)
        self.eastTranslation = QtGui.QDoubleSpinBox(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.eastTranslation.sizePolicy().hasHeightForWidth())
        self.eastTranslation.setSizePolicy(sizePolicy)
        self.eastTranslation.setObjectName(_fromUtf8("eastTranslation"))
        self.verticalLayout_7.addWidget(self.eastTranslation)
        self.upTranslation = QtGui.QDoubleSpinBox(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.upTranslation.sizePolicy().hasHeightForWidth())
        self.upTranslation.setSizePolicy(sizePolicy)
        self.upTranslation.setObjectName(_fromUtf8("upTranslation"))
        self.verticalLayout_7.addWidget(self.upTranslation)
        self.horizontalLayout_7.addLayout(self.verticalLayout_7)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_5 = QtGui.QLabel(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_5.addWidget(self.label_5)
        self.horizontalLayout_7.addLayout(self.verticalLayout_5)
        self.verticalLayout_6.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.setWaypointButton = QtGui.QToolButton(MissionCommander)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.setWaypointButton.sizePolicy().hasHeightForWidth())
        self.setWaypointButton.setSizePolicy(sizePolicy)
        self.setWaypointButton.setObjectName(_fromUtf8("setWaypointButton"))
        self.horizontalLayout_8.addWidget(self.setWaypointButton)
        self.setRelativeHome = QtGui.QToolButton(MissionCommander)
        self.setRelativeHome.setObjectName(_fromUtf8("setRelativeHome"))
        self.horizontalLayout_8.addWidget(self.setRelativeHome)
        self.setRelativeWaypoint = QtGui.QToolButton(MissionCommander)
        self.setRelativeWaypoint.setObjectName(_fromUtf8("setRelativeWaypoint"))
        self.horizontalLayout_8.addWidget(self.setRelativeWaypoint)
        self.verticalLayout_6.addLayout(self.horizontalLayout_8)
        self.missionListWidget = QtGui.QListWidget(MissionCommander)
        self.missionListWidget.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.missionListWidget.sizePolicy().hasHeightForWidth())
        self.missionListWidget.setSizePolicy(sizePolicy)
        self.missionListWidget.setMaximumSize(QtCore.QSize(100050, 16777215))
        self.missionListWidget.setObjectName(_fromUtf8("missionListWidget"))
        self.verticalLayout_6.addWidget(self.missionListWidget)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.moveUp = QtGui.QPushButton(MissionCommander)
        self.moveUp.setObjectName(_fromUtf8("moveUp"))
        self.horizontalLayout_6.addWidget(self.moveUp)
        self.moveDown = QtGui.QPushButton(MissionCommander)
        self.moveDown.setObjectName(_fromUtf8("moveDown"))
        self.horizontalLayout_6.addWidget(self.moveDown)
        self.verticalLayout_6.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.previousMissionButton = QtGui.QPushButton(MissionCommander)
        self.previousMissionButton.setObjectName(_fromUtf8("previousMissionButton"))
        self.horizontalLayout_9.addWidget(self.previousMissionButton)
        self.nextMissionButton = QtGui.QPushButton(MissionCommander)
        self.nextMissionButton.setObjectName(_fromUtf8("nextMissionButton"))
        self.horizontalLayout_9.addWidget(self.nextMissionButton)
        self.verticalLayout_6.addLayout(self.horizontalLayout_9)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(MissionCommander)
        QtCore.QMetaObject.connectSlotsByName(MissionCommander)

    def retranslateUi(self, MissionCommander):
        MissionCommander.setWindowTitle(_translate("MissionCommander", "Mission Commander", None))
        self.saveMissionList.setText(_translate("MissionCommander", "Save Missions", None))
        self.loadMissionList.setText(_translate("MissionCommander", "Load Missions", None))
        self.missionTypeCB.setItemText(0, _translate("MissionCommander", "Select a Mission Type", None))
        self.missionTypeCB.setItemText(1, _translate("MissionCommander", "Navigation v3", None))
        self.missionTypeCB.setItemText(2, _translate("MissionCommander", "Dice Mission", None))
        self.missionTypeCB.setItemText(3, _translate("MissionCommander", "Entry Gate v3", None))
        self.missionTypeCB.setItemText(4, _translate("MissionCommander", "Roulette", None))
        self.missionTypeCB.setItemText(5, _translate("MissionCommander", "Torpedo", None))
        self.lookLeft.setText(_translate("MissionCommander", "Look to the Left", None))
        self.lookRight.setText(_translate("MissionCommander", "Look to the Right", None))
        self.label.setText(_translate("MissionCommander", "Max Time in Seconds", None))
        self.checkBox_3.setText(_translate("MissionCommander", "Relative Move (Polar)", None))
        self.checkBox_4.setText(_translate("MissionCommander", "One More Option", None))
        self.useLaser.setText(_translate("MissionCommander", "Relative Move (CART)", None))
        self.useKalmanFilter.setText(_translate("MissionCommander", "Absolute Move", None))
        self.label_3.setText(_translate("MissionCommander", "Use General Waypoint from Mission", None))
        self.label_2.setText(_translate("MissionCommander", "Mission Name", None))
        self.addMissionButton.setText(_translate("MissionCommander", "Add / Updated Mission", None))
        self.removeMissionButton.setText(_translate("MissionCommander", "Remove Mission", None))
        self.label_4.setText(_translate("MissionCommander", "Translation", None))
        self.label_5.setText(_translate("MissionCommander", "Rotation", None))
        self.setWaypointButton.setText(_translate("MissionCommander", "Set Waypoint", None))
        self.setRelativeHome.setText(_translate("MissionCommander", "Set Rel Home", None))
        self.setRelativeWaypoint.setText(_translate("MissionCommander", "Set Rel Waypoint", None))
        self.moveUp.setText(_translate("MissionCommander", "Up", None))
        self.moveDown.setText(_translate("MissionCommander", "Down", None))
        self.previousMissionButton.setText(_translate("MissionCommander", "Previous Mission", None))
        self.nextMissionButton.setText(_translate("MissionCommander", "Next Mission", None))

