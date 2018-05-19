# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dataGraphing.ui'
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

class Ui_DataGraphing(object):
    def setupUi(self, DataGraphing):
        DataGraphing.setObjectName(_fromUtf8("DataGraphing"))
        DataGraphing.resize(761, 459)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(DataGraphing)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.graphLayout = QtGui.QVBoxLayout()
        self.graphLayout.setObjectName(_fromUtf8("graphLayout"))
        self.horizontalLayout.addLayout(self.graphLayout)
        self.line = QtGui.QFrame(DataGraphing)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.settingsLayout = QtGui.QFormLayout()
        self.settingsLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.settingsLayout.setObjectName(_fromUtf8("settingsLayout"))
        self.label = QtGui.QLabel(DataGraphing)
        self.label.setObjectName(_fromUtf8("label"))
        self.settingsLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(DataGraphing)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.settingsLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.xAxisCB = QtGui.QComboBox(DataGraphing)
        self.xAxisCB.setObjectName(_fromUtf8("xAxisCB"))
        self.xAxisCB.addItem(_fromUtf8(""))
        self.settingsLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.xAxisCB)
        self.yAxisCB = QtGui.QComboBox(DataGraphing)
        self.yAxisCB.setObjectName(_fromUtf8("yAxisCB"))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.yAxisCB.addItem(_fromUtf8(""))
        self.settingsLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.yAxisCB)
        self.loadFileButton = QtGui.QPushButton(DataGraphing)
        self.loadFileButton.setObjectName(_fromUtf8("loadFileButton"))
        self.settingsLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.loadFileButton)
        self.horizontalLayout.addLayout(self.settingsLayout)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(DataGraphing)
        QtCore.QMetaObject.connectSlotsByName(DataGraphing)

    def retranslateUi(self, DataGraphing):
        DataGraphing.setWindowTitle(_translate("DataGraphing", "Form", None))
        self.label.setText(_translate("DataGraphing", "X Axis", None))
        self.label_2.setText(_translate("DataGraphing", "Y Axis", None))
        self.xAxisCB.setItemText(0, _translate("DataGraphing", "time", None))
        self.yAxisCB.setItemText(0, _translate("DataGraphing", "Ahrs Yaw", None))
        self.yAxisCB.setItemText(1, _translate("DataGraphing", "Ahrs Pitch", None))
        self.yAxisCB.setItemText(2, _translate("DataGraphing", "Ahrs Roll", None))
        self.yAxisCB.setItemText(3, _translate("DataGraphing", "Dvl X", None))
        self.yAxisCB.setItemText(4, _translate("DataGraphing", "Dvl Y", None))
        self.yAxisCB.setItemText(5, _translate("DataGraphing", "Dvl Z", None))
        self.yAxisCB.setItemText(6, _translate("DataGraphing", "Dvl dX", None))
        self.yAxisCB.setItemText(7, _translate("DataGraphing", "Dvl dY", None))
        self.yAxisCB.setItemText(8, _translate("DataGraphing", "Dvl dZ", None))
        self.yAxisCB.setItemText(9, _translate("DataGraphing", "Depth", None))
        self.loadFileButton.setText(_translate("DataGraphing", "Load File", None))

