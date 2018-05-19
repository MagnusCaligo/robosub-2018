from PyQt4 import QtCore, QtGui
import math
import time

#@author Nathan Danque. Widget originally present in SwingInnovation's Odessa Application.

class BoundsDialog(QtGui.QDialog):
    minChanged = QtCore.pyqtSignal(object)
    maxChanged = QtCore.pyqtSignal(object)

    def __init__(self):
        super(BoundsDialog, self).__init__()
        _minLbl = QtGui.QLabel("Min: ", self)
        self._minLE = QtGui.QLineEdit(self);
        _maxLbl = QtGui.QLabel("Max: ", self)
        self._maxLE = QtGui.QLineEdit(self)

        propLayout = QtGui.QGridLayout()
        propLayout.addWidget(_minLbl, 0, 0)
        propLayout.addWidget(self._minLE, 0, 2)
        propLayout.addWidget(_maxLbl, 1, 0)
        propLayout.addWidget(self._maxLE,  1, 2)

        grpBox = QtGui.QGroupBox(self)
        grpBox.setTitle("Properties: ")
        grpBox.setLayout(propLayout)

        _applyBtn = QtGui.QPushButton("Apply", self)
        _cancelBtn = QtGui.QPushButton("Cancel", self)

        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(_applyBtn)
        btnLayout.addWidget(_cancelBtn)

        centralLayout = QtGui.QVBoxLayout()
        centralLayout.addWidget(grpBox)
        centralLayout.addLayout(btnLayout)
        self.setLayout(centralLayout)

        _applyBtn.clicked.connect(self.applyAction)
        _cancelBtn.clicked.connect(self.closeDown)

    def setMin(self, value):
        self._minLE.setText(QtCore.QString.number(value))

    def setMax(self, value):
        self._maxLE.setText(QtCore.QString.number(value))

    def applyAction(self):
        newMin = self._minLE.text().toFloat()
        newMax = self._maxLE.text().toFloat()
        self.minChanged.emit(newMin[0])
        self.maxChanged.emit(newMax[0])
        self.setVisible(False)

    def closeDown(self):
        self.setVisible(False)


class SlideEdit(QtGui.QLineEdit):
    valueChanged_lbl = QtCore.pyqtSignal(object, object)
    valueChanged = QtCore.pyqtSignal(object)            #Yields the proper Current Value.

    def __init__(self):
        super(SlideEdit, self).__init__()
        self._boundsDiag = BoundsDialog()
        self.setAlignment(QtCore.Qt.AlignCenter)
        self._min = 0.0
        self._max = 10.0
        self._currentValue = 0.0
        self.setText("10")
        self._lockBounds = True
        self._integerStep = True
        self.handle = QtCore.QRect()
        self.progressed = QtCore.QRect()
        self._isDown = False
        self._foregroundColor = QtGui.QColor(200, 15, 0).lighter(115)
        self._foregroundColor.setAlphaF(0.3)
        self.editingFinished.connect(self.UpdateCurrentValue)
        self._assignedLabel = " "
        self.maxTime = .01
        self.previousTime = 0
        self.sent = False

        #Context Menu Actions
        self._resetBoundsAct = QtGui.QAction("Reset Bounds", self)
        self._lockBoundsAct = QtGui.QAction("Lock Bounds", self)
        self._lockBoundsAct.setCheckable(True)
        self._lockBoundsAct.triggered.connect(self.lockBoundsAction)
        self._resetMin = QtGui.QAction("Reset Min", self)
        self._resetMax = QtGui.QAction("Reset Max", self)
        self._intStep = QtGui.QAction("Int Step", self)
        self._boundsDiagAct = QtGui.QAction("Edit Bounds", self)
        self._boundsDiagAct.triggered.connect(self.showBoundsDialog)
        self._boundsDiag.minChanged.connect(self.updateMin)
        self._boundsDiag.maxChanged.connect(self.updateMax)



    def UpdateCurrentValue(self):
        f = self.text().toFloat()
        self.setCurrentValue(f[0])
        self.update()

    def updateMin(self, value):
        """
        :param value: New Minimum Value 
        :return: 
        """
        self._min = value
        if self._currentValue < value:
            self.setCurrentValue(value)

    def updateMax(self, value):
        """
        :param value: New Maximum Value
        :return: 
        """
        self._max = value
        if self._currentValue > value:
            self.setCurrentValue(value)

    def setCurrentValue(self, newValue):
        """
        Sets the current value of the slider, enforces bounds if necessary.
        :param newValue: New value of slider
        :return: 
        """
        curVal = 0
        if self._integerStep == False:
            curVal = newValue
        else:
            if newValue < 0.5:
                curVal = 0
            else:
                curVal = math.ceil(newValue)

        if self._currentValue > self._max and self._lockBounds is False:
            self._max = newValue
        elif self._currentValue > self._max and self._lockBounds is True:
            curVal = self._max
        self._currentValue = curVal
        self.setText(QtCore.QString.number(self._currentValue))
        self.valueChanged_lbl.emit(self._assignedLabel, self._currentValue);
        self.valueChanged.emit(self._currentValue)

    def setCurrentValueStr(self, value):
        if type(value) is QtCore.QString:
            f = value.toFloat()
            self.setCurrentValue(value.toFloat()[0])


    def mousePressEvent(self, QMouseEvent):
        if (QMouseEvent.button() == 1) and self.handle.contains(QMouseEvent.pos()):
            self._isDown = True

    def mouseReleaseEvent(self, QMouseEvent):
        if self._isDown is True:
            self._isDown = False

    def mouseMoveEvent(self, QMouseEvent):
        #Cursor Stuff
        if self.handle.contains(QMouseEvent.pos()):
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))

        if self._isDown:
            px = QMouseEvent.pos().x()
            if(px >= 0 and px <= self.width()):
                self.handle.setX(px)
                self._lockBounds = True
                if time.time() - self.previousTime > self.maxTime: 
                    self.setCurrentValue( (px / float(self.width())) * self._max )
                    self.previousTime = time.time()
                else:
                    pass
                self._lockBounds = False

    def wheelEvent(self, QWheelEvent):
        step = QWheelEvent.delta() / float(80.0)
        curVal = self._currentValue - step
        if self._lockBounds is True:
            if curVal > self._max:
                self.setCurrentValue(self._max)
                return
            elif curVal < self._min:
                self.setCurrentValue(self._min)
                return
            else:
                self.setCurrentValue(curVal)
                return
        self.setCurrentValue(curVal)

    def paintEvent(self, QPaintEvent):
        super(SlideEdit, self).paintEvent(QPaintEvent)
        ratio = self._currentValue / self._max
        pX = ratio * self.geometry().width()
        if(pX <= 6):
            self.handle.setX(self._min)
            self._currentValue = self._min
        else:
            self.handle.setX(pX - 6)

        self.handle.setY(0)
        self.handle.setWidth(6)
        self.handle.setHeight(self.height())

        self.progressed.setX(0)
        self.progressed.setY(0)
        self.progressed.setWidth(self.handle.x())
        self.progressed.setHeight(self.height())

        p = QtGui.QPainter(self)
        p.setCompositionMode(QtGui.QPainter.CompositionMode_Difference)
        p.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 0.8)))
        p.drawRect(self.handle)
        p.fillRect(self.handle, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        p.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        if(self.isEnabled()):
            p.setBrush(QtGui.QBrush(self._foregroundColor))
        else:
            p.setBrush(QtGui.QBrush(QtGui.QColor(200, 200, 200, 0.8)))
        p.drawRect(self.progressed)

    def lockBoundsAction(self):
        """
        Locks Current Bounds. 
        :return: 
        """
        self._lockBounds = self._lockBoundsAct.isChecked()
        print self._lockBounds

    def contextMenuEvent(self, QContextMenuEvent):
        self._lockBoundsAct.setChecked(self._lockBounds)
        menu = QtGui.QMenu(self)
        menu.addAction(self._resetBoundsAct)
        menu.addAction(self._lockBoundsAct)
        menu.addSeparator()
        menu.addAction(self._resetMin)
        menu.addAction(self._resetMax)
        menu.addSeparator()
        menu.addAction(self._boundsDiagAct)
        menu.exec_(QContextMenuEvent.globalPos())

    def showBoundsDialog(self):
        if self._boundsDiag.isVisible() is False:
            self._boundsDiag.setMin(self._min)
            self._boundsDiag.setMax(self._max)
            self._boundsDiag.setVisible(True)
