from PyQt4 import QtCore, QtGui
from lib.Utils.SlideEdit import SlideEdit
from UI_Control_System.ui_control_system import Ui_Form
from lib.ExternalDevices.previous_state_logging import Previous_State_Logging
import copy


class ControlSystemWidget(QtCore.QObject):
    
    def __init__(self, externalComm):
        QtCore.QObject.__init__(self)
        self.slideEditList = []
        self.ui_controlSystemWidget = Ui_Form()
        self.controlSystemThread = None
        self.labelNames = ["Kp", "Ki", "Kd", "Controller", "Integration Min", "Integration Max"]
        self.tabLayoutList = None
        self.externalComm = externalComm
        self.PIDVals = {}
        self.previous_state_logging = Previous_State_Logging
        self.tabLayoutNames = []
        
        for i,v in enumerate(self.labelNames):
            self.PIDVals["YawForward_"+v] = float(self.externalComm.previous_state_logging.getValue("YawForward_" + v))
            self.PIDVals["YawBackward_"+v] = float(self.externalComm.previous_state_logging.getValue("YawBackward_" + v))
            self.PIDVals["Pitch_"+v] = float(self.externalComm.previous_state_logging.getValue("Pitch_" + v))
            self.PIDVals["Roll_"+v] = float(self.externalComm.previous_state_logging.getValue("Roll_" + v))
            self.PIDVals["Depth_"+v] = float(self.externalComm.previous_state_logging.getValue("Depth_" + v))
            self.PIDVals["XPosition_"+v] = float(self.externalComm.previous_state_logging.getValue("XPosition_" + v))
            self.PIDVals["ZPosition_"+v] = float(self.externalComm.previous_state_logging.getValue("ZPosition_" + v))
            

        

    def connectSignals(self):
        """
        Connects signals and slots.  Also calls setup functions that need
        to be called after the ui is created.
        :return:
        """
        self.tabLayoutList = [self.ui_controlSystemWidget.verticalLayout_4, self.ui_controlSystemWidget.verticalLayout_5,
                              self.ui_controlSystemWidget.verticalLayout_6, self.ui_controlSystemWidget.verticalLayout_7,
                              self.ui_controlSystemWidget.verticalLayout_8, self.ui_controlSystemWidget.verticalLayout_9,
                              self.ui_controlSystemWidget.verticalLayout_10]

        self.tabLayoutNames = ["YawForward", "YawBackward", "Pitch", "Roll", "Depth", "XPosition", "ZPosition"]
        self._createSlideEdit()
        self._setSavedValues()

    def _setSavedValues(self):
        """
        Sets all the sliders to the saved values from previous state logging.

        Connects valueChanged  ----> saveValues
        :return:
        """
        
        for slideEdit in self.slideEditList:
            slideEdit.setCurrentValue(self.PIDVals[str(slideEdit._assignedLabel)])
            slideEdit.valueChanged.connect(self.saveValues)
        

    def _createSlideEdit(self):
        """
        Loops through the layout list and sets all the sliders and labels.
        Also connects all the slider signals.
        :return:
        """
        for j in range(0, len(self.tabLayoutList)):
            for i in range(0, 6):
                slideEdit = SlideEdit()
                if i == 0 or i ==1:
                    slideEdit.updateMax(7)
                elif i== 2:
                    slideEdit.updateMax(15)
                elif i==3:
                    slideEdit.updateMax(1)
                elif i==4 or i==5:
                    slideEdit.updateMax(40)
                    
                slideEdit._integerStep = False
                slideEdit._lockBounds = True
                label = QtGui.QLabel(self.labelNames[i])
                slideEdit._assignedLabel = self.tabLayoutNames[j] + "_" + label.text()
                self.tabLayoutList[j].addWidget(label)
                self.tabLayoutList[j].addWidget(slideEdit)
                self.slideEditList.append(slideEdit)

    def saveValues(self):
        """
        Writes the values to a csv file.
        :return:
        """
        values = []
        inValues = []
        for slide_edit in self.slideEditList:
            previousVal = str(self.externalComm.previous_state_logging.getValue(slide_edit._assignedLabel))
            val = slide_edit._currentValue

            inValues.append(val)
            if len(inValues) == 6:
                values.append(copy.copy(inValues))
                inValues = []
            if previousVal != slide_edit._currentValue:
                self.externalComm.previous_state_logging.add(str(slide_edit._assignedLabel), slide_edit._currentValue)
                self.PIDVals[slide_edit._assignedLabel] = float(slide_edit._currentValue)
        self.emit(QtCore.SIGNAL("updatePIDValues(PyQt_PyObject)"), values)


