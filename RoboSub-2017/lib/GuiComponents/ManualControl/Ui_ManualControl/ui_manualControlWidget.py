# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_manualControlWidget.ui'
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

class Ui_ManualControlWidget(object):
    def setupUi(self, ManualControlWidget):
        ManualControlWidget.setObjectName(_fromUtf8("ManualControlWidget"))
        ManualControlWidget.resize(864, 707)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ManualControlWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.startButton = QtGui.QPushButton(ManualControlWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())
        self.startButton.setSizePolicy(sizePolicy)
        self.startButton.setObjectName(_fromUtf8("startButton"))
        self.horizontalLayout_9.addWidget(self.startButton)
        self.controlOutput = QtGui.QPlainTextEdit(ManualControlWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.controlOutput.sizePolicy().hasHeightForWidth())
        self.controlOutput.setSizePolicy(sizePolicy)
        self.controlOutput.setObjectName(_fromUtf8("controlOutput"))
        self.horizontalLayout_9.addWidget(self.controlOutput)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.retranslateUi(ManualControlWidget)
        QtCore.QMetaObject.connectSlotsByName(ManualControlWidget)

    def retranslateUi(self, ManualControlWidget):
        ManualControlWidget.setWindowTitle(_translate("ManualControlWidget", "Form", None))
        self.startButton.setText(_translate("ManualControlWidget", "Start", None))

