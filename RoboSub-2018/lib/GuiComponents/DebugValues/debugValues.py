from PyQt4 import QtCore, QtGui
from lib.Utils.SlideEdit import SlideEdit
from UI_DebugValues.ui_debugValues import Ui_Form

class DebugValues(QtCore.QObject):
    
    def __init__(self, externalComm):
        QtCore.QObject.__init__(self)
        self.ui_DebugValues = Ui_Form()
        self.externalComm = externalComm
        
        self.yawValue = SlideEdit()
        self.yawValue.updateMin(0)
        self.yawValue.updateMax(360)
        self.yawValue.setCurrentValue(0)

        self.pitchValue = SlideEdit()
        self.pitchValue.updateMin(0)
        self.pitchValue.updateMax(90)
        self.pitchValue.setCurrentValue(45)

        self.rollValue = SlideEdit()
        self.rollValue.updateMin(0)
        self.rollValue.updateMax(90)
        self.rollValue.setCurrentValue(45)
        

        
    def connectSignals(self):
        self.ui_DebugValues.northValue.valueChanged.connect(self.sendValues)
        self.ui_DebugValues.eastValue.valueChanged.connect(self.sendValues)
        self.ui_DebugValues.upValue.valueChanged.connect(self.sendValues)
        self.yawValue.valueChanged.connect(self.sendValues)
        self.pitchValue.valueChanged.connect(self.sendValues)
        self.rollValue.valueChanged.connect(self.sendValues)

        self.ui_DebugValues.verticalLayout_3.addWidget(QtGui.QLabel("Yaw"))
        self.ui_DebugValues.verticalLayout_3.addWidget(self.yawValue, 1)
        self.ui_DebugValues.verticalLayout_3.addWidget(QtGui.QLabel("Pitch"))
        self.ui_DebugValues.verticalLayout_3.addWidget(self.pitchValue, 3)
        self.ui_DebugValues.verticalLayout_3.addWidget(QtGui.QLabel("Roll"))
        self.ui_DebugValues.verticalLayout_3.addWidget(self.rollValue, 5)

    def sendValues(self):
        if self.ui_DebugValues.useDebugCheckBox.isChecked():
            data = []
            data.append(self.ui_DebugValues.northValue.value())
            data.append(self.ui_DebugValues.eastValue.value())
            data.append(self.ui_DebugValues.upValue.value())
            
            data.append(self.yawValue._currentValue)
            data.append(self.pitchValue._currentValue-45)
            data.append(self.rollValue._currentValue-45)
            
            self.emit(QtCore.SIGNAL("debugPositionValues(PyQt_PyObject)"), data)