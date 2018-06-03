# Main python file to call
from PyQt4 import QtGui, QtCore
from lib.GuiComponents.MainWindow.mainWindow import MainWindow
from lib.GuiComponents.ComputerVision.computerVision import ComputerVision
from lib.GuiComponents.Map.map import Map
from lib.GuiComponents.Embedded.embedded import EmbeddedWidget
from lib.GuiComponents.ManualControl.manualControl import ManualControl
from lib.ExternalDevices.external_communication import ExternalComm
from lib.GuiComponents.MissionCommander.missionCommander import MissionCommander
from lib.GuiComponents.DataGraphing.dataGraphing import DataGraphing
from lib.GuiComponents.ControlSystemWidget.controlSystemWidget import ControlSystemWidget

import sys



def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    roboSubGui = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.gui = roboSubGui

    if False:
        roboSubGui.setStyle(QtGui.QStyleFactory.create("plastique"))
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
        pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        pal.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
        pal.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
        pal.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        pal.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
        pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
        pal.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
        pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(144, 216, 255).darker())
        roboSubGui.setPalette(pal)
        roboSubGui.setStyleSheet("QSeparator { foreground-color: white }")

    externalCommClass = ExternalComm(window)
    manualControlClass = ManualControl(externalCommClass)
    computerVisionClass = ComputerVision(externalCommClass)
    mapClass = Map(externalCommClass)
    embeddedWidgetClass = EmbeddedWidget(externalCommClass)
    missionCommanderClass = MissionCommander(externalCommClass)
    dataGraphingClass = DataGraphing(externalCommClass)
    controlSystemClass = ControlSystemWidget(externalCommClass)
    
    #Passes the mission commander class into Mission Planner to connect signals
    externalCommClass.missionPlanner.setReferences(missionCommanderClass, controlSystemClass)

    window.setClasses([manualControlClass, computerVisionClass, mapClass, embeddedWidgetClass,
                       externalCommClass, missionCommanderClass, dataGraphingClass, controlSystemClass])
    window.show()
    window.add_mainWidget()
    roboSubGui.aboutToQuit.connect(window.exitHandler)
    sys.exit(roboSubGui.exec_())


main()
