# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_updateMissionDialog.ui'
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

class Ui_Ui_UpdateMissionDialog(object):
    def setupUi(self, Ui_UpdateMissionDialog):
        Ui_UpdateMissionDialog.setObjectName(_fromUtf8("Ui_UpdateMissionDialog"))
        Ui_UpdateMissionDialog.resize(400, 316)
        self.verticalLayout = QtGui.QVBoxLayout(Ui_UpdateMissionDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.missionComboBox = QtGui.QComboBox(Ui_UpdateMissionDialog)
        self.missionComboBox.setObjectName(_fromUtf8("missionComboBox"))
        self.missionComboBox.addItem(_fromUtf8(""))
        self.missionComboBox.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.missionComboBox)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(Ui_UpdateMissionDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(Ui_UpdateMissionDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.stopTimeLineEdit = QtGui.QLineEdit(Ui_UpdateMissionDialog)
        self.stopTimeLineEdit.setObjectName(_fromUtf8("stopTimeLineEdit"))
        self.gridLayout.addWidget(self.stopTimeLineEdit, 1, 1, 1, 1)
        self.nameLineEdit = QtGui.QLineEdit(Ui_UpdateMissionDialog)
        self.nameLineEdit.setObjectName(_fromUtf8("nameLineEdit"))
        self.gridLayout.addWidget(self.nameLineEdit, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Ui_UpdateMissionDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.lineEdit_3 = QtGui.QLineEdit(Ui_UpdateMissionDialog)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.gridLayout.addWidget(self.lineEdit_3, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.searchPatterComboBox = QtGui.QComboBox(Ui_UpdateMissionDialog)
        self.searchPatterComboBox.setObjectName(_fromUtf8("searchPatterComboBox"))
        self.searchPatterComboBox.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.searchPatterComboBox)
        self.buttonBox = QtGui.QDialogButtonBox(Ui_UpdateMissionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Ui_UpdateMissionDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Ui_UpdateMissionDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Ui_UpdateMissionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Ui_UpdateMissionDialog)

    def retranslateUi(self, Ui_UpdateMissionDialog):
        Ui_UpdateMissionDialog.setWindowTitle(_translate("Ui_UpdateMissionDialog", "Dialog", None))
        self.missionComboBox.setItemText(0, _translate("Ui_UpdateMissionDialog", "Torpedo Search", None))
        self.missionComboBox.setItemText(1, _translate("Ui_UpdateMissionDialog", "Buoy Search", None))
        self.label_2.setText(_translate("Ui_UpdateMissionDialog", "TextLabel", None))
        self.label_4.setText(_translate("Ui_UpdateMissionDialog", "Name", None))
        self.label_3.setText(_translate("Ui_UpdateMissionDialog", "Stop Time", None))
        self.searchPatterComboBox.setItemText(0, _translate("Ui_UpdateMissionDialog", "Look at previous location first", None))

