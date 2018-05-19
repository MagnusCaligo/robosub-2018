# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_updateGraphs.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayoutWidget = QtGui.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 401, 231))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.formLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.comboBox = QtGui.QComboBox(self.formLayoutWidget)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.comboBox)
        self.label_3 = QtGui.QLabel(self.formLayoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.comboBox_2 = QtGui.QComboBox(self.formLayoutWidget)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.comboBox_2)
        self.graphNameLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.graphNameLineEdit.setObjectName(_fromUtf8("graphNameLineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.graphNameLineEdit)
        self.removeGraphButton = QtGui.QPushButton(Dialog)
        self.removeGraphButton.setGeometry(QtCore.QRect(80, 240, 112, 29))
        self.removeGraphButton.setObjectName(_fromUtf8("removeGraphButton"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Graph Name:", None))
        self.label_2.setText(_translate("Dialog", "X Axis:", None))
        self.comboBox.setItemText(0, _translate("Dialog", "ahrsheading", None))
        self.comboBox.setItemText(1, _translate("Dialog", "ahrsyaw", None))
        self.comboBox.setItemText(2, _translate("Dialog", "ahrspitch", None))
        self.comboBox.setItemText(3, _translate("Dialog", "dvlx", None))
        self.comboBox.setItemText(4, _translate("Dialog", "dvly", None))
        self.comboBox.setItemText(5, _translate("Dialog", "dvlz", None))
        self.comboBox.setItemText(6, _translate("Dialog", "Time", None))
        self.label_3.setText(_translate("Dialog", "Y Axis:", None))
        self.comboBox_2.setItemText(0, _translate("Dialog", "ahrsheading", None))
        self.comboBox_2.setItemText(1, _translate("Dialog", "ahrsyaw", None))
        self.comboBox_2.setItemText(2, _translate("Dialog", "ahrspitch", None))
        self.comboBox_2.setItemText(3, _translate("Dialog", "dvlx", None))
        self.comboBox_2.setItemText(4, _translate("Dialog", "dvly", None))
        self.comboBox_2.setItemText(5, _translate("Dialog", "dvlz", None))
        self.removeGraphButton.setText(_translate("Dialog", "Remove ", None))

