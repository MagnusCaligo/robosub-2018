from PyQt4 import QtCore
from lib.GuiComponents.ComputerVision.computerVision import ComputerVisionThread

'''
This class will be used to controll all the threads and keep them separate from
the widgets that are using them. When creating a new widget that uses a thread, the mainWindowWidget
must emit a signal signifying a new widget with widget as a parameter

'''
class ThreadController(QtCore.QObject):
    
    def __init__(self, mainWindowObject, parent = None):
        super(ThreadController, self).__init__(parent)
        self. mainWindowObject = mainWindowObject
        
        #Keeps a list of all the widgets accessing the threads
        self.widgets = [0,0,0,0,0,0]
    
    
        #The threads being run
        self.computerVisionThread = ComputerVisionThread()        
        
        #Dictionaries for easy reference 
        self.threadDictionary = {0:self.computerVisionThread}
        self.widgetDictionary = {"ComputerVisionWidget":0}
        
    def checkThreadUse(self):
        for index, widget in enumerate(widgets):
            if widget < 1:
                self.threadDictionary.get(index).wait()
            elif widget > 0:
                if not self.threadDictionary.get(index).isRunning:
                    self.threadDictionary.get(index).start()
        
    def connectNewWidget(self, WidgetType):
        index = self.widgetDictionary.get(WidgetType)
        self.widgets[index] = self.widget[index + 1]
        self.checkThreadUse()
        
    def removeConnectedWidget(self, WidgetType):
        index = self.widgetDictionary.get(WidgetType)
        if self.widgets[index] >0:
            self.widgets[index] = self.widgets[index] - 1
        self.checkThreadUse()
        
    def connectSignals(self):
        self.connect(self.mainWindowObject, QtCore.SIGNAL("newWidget(QString)"), self.connectNewWidget)
        self.connect(self.mainWindowObject, QtCore.SIGNAL("removedWidget(QString)"), self.removeConnectedWidget)
        
        self.connect(self.computerVisionThread, QtCore.SIGNAL("finished(QString)"), lambda string: self.computerVisionThread.start())
        

    def stopThreads(self):
        for thread in self.threads:
            thread.wait()
            thread.stop()
        
        