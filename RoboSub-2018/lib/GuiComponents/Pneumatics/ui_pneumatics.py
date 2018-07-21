# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_pneumatics.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(190, 260)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.torpedo1Button = QtGui.QPushButton(Form)
        self.torpedo1Button.setObjectName(_fromUtf8("torpedo1Button"))
        self.verticalLayout_2.addWidget(self.torpedo1Button)
        self.torpedo2Button = QtGui.QPushButton(Form)
        self.torpedo2Button.setObjectName(_fromUtf8("torpedo2Button"))
        self.verticalLayout_2.addWidget(self.torpedo2Button)
        self.dropper1Button = QtGui.QPushButton(Form)
        self.dropper1Button.setObjectName(_fromUtf8("dropper1Button"))
        self.verticalLayout_2.addWidget(self.dropper1Button)
        self.dropper2Button = QtGui.QPushButton(Form)
        self.dropper2Button.setObjectName(_fromUtf8("dropper2Button"))
        self.verticalLayout_2.addWidget(self.dropper2Button)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.torpedo1Button.setText(_translate("Form", "Torpedo 1", None))
        self.torpedo2Button.setText(_translate("Form", "Torpedo 2", None))
        self.dropper1Button.setText(_translate("Form", "Dropper 1", None))
        self.dropper2Button.setText(_translate("Form", "Dropper 2", None))

