import csv
import os
from PyQt4 import QtCore
from PyQt4 import QtGui
from sys import platform

class Widget_Config_Logger:

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.path = 'savedLayoutConfigs'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def saveConfigs(self):
        listOfDicts = []
        if self.mainWindow.mainWindowWidget:
            # save mainWindowWidget info
            dict1 = {'widget': 'mainWindowWidget',
                     'X': self.mainWindow.mainWindowWidget.parent().x(),
                     'Y': self.mainWindow.mainWindowWidget.parent().y(),
                     'Height': self.mainWindow.mainWindowWidget.height(),
                     'Width': self.mainWindow.mainWindowWidget.width()}

            listOfDicts.append(dict1)

        if self.mainWindow.mapWidget:
            # save mapWidget info
            dict1 = {'widget': 'mapWidget',
                     'X': self.mainWindow.mapWidget.parent().x(),
                     'Y': self.mainWindow.mapWidget.parent().y(),
                     'Height': self.mainWindow.mapWidget.height(),
                     'Width': self.mainWindow.mapWidget.width()}

            listOfDicts.append(dict1)
        if self.mainWindow.embeddedWidget:
            # save embeddedWidget info
            dict1 = {'widget': 'embeddedWidget',
                     'X': self.mainWindow.embeddedWidget.parent().x(),
                     'Y': self.mainWindow.embeddedWidget.parent().y(),
                     'Height': self.mainWindow.embeddedWidget.height(),
                     'Width': self.mainWindow.embeddedWidget.width()}

            listOfDicts.append(dict1)
        if self.mainWindow.computerVisionWidget:
            # save computervisionWidget info
            dict1 = {'widget': 'computerVisionWidget',
                     'X': self.mainWindow.computerVisionWidget.parent().x(),
                     'Y': self.mainWindow.computerVisionWidget.parent().y(),
                     'Height': self.mainWindow.computerVisionWidget.height(),
                     'Width': self.mainWindow.computerVisionWidget.width()}

            listOfDicts.append(dict1)
        if self.mainWindow.manualControlWidget:
            # save manualControlWidget info
            dict1 = {'widget': 'manualControlWidget',
                     'X': self.mainWindow.manualControlWidget.parent().x(),
                     'Y': self.mainWindow.manualControlWidget.parent().y(),
                     'Height': self.mainWindow.manualControlWidget.height(),
                     'Width': self.mainWindow.manualControlWidget.width()}
            listOfDicts.append(dict1)
        if self.mainWindow.missionCommanderWidget:
            # save missionCommanderWidget info
            dict1 = {'widget': 'missionCommanderWidget',
                     'X': self.mainWindow.missionCommanderWidget.parent().x(),
                     'Y': self.mainWindow.missionCommanderWidget.parent().y(),
                     'Height': self.mainWindow.missionCommanderWidget.height(),
                     'Width': self.mainWindow.missionCommanderWidget.width()}
            listOfDicts.append(dict1)
        if self.mainWindow.dataGraphingWidget:
            # save dataGraphingWidget info
            dict1 = {'widget': 'dataGraphingWidget',
                     'X': self.mainWindow.dataGraphingWidget.parent().x(),
                     'Y': self.mainWindow.dataGraphingWidget.parent().y(),
                     'Height': self.mainWindow.dataGraphingWidget.height(),
                     'Width': self.mainWindow.dataGraphingWidget.width()}
            listOfDicts.append(dict1)
        if self.mainWindow.controlSystemWidget:
            # save dataGraphingWidget info
            dict1 = {'widget': 'controlSystemsWidget',
                     'X': self.mainWindow.controlSystemWidget.parent().x(),
                     'Y': self.mainWindow.controlSystemWidget.parent().y(),
                     'Height': self.mainWindow.controlSystemWidget.height(),
                     'Width': self.mainWindow.controlSystemWidget.width()}
            listOfDicts.append(dict1)
        #open a file dialog and pick a file to save in:
        fileWidget = QtGui.QWidget()
        fileWidget.resize(320, 240)
        # Sets dialog to open at a particular directory
        print ("Opening file dialog.")
        dialog = QtGui.QFileDialog()
        fileName = dialog.getSaveFileName(fileWidget, 'Save File', 'savedLayoutConfigs')
        fileName.append(".csv")
        try:
            if platform == "win32":
                fileName = fileName.replace('/', '\\')
            print "saving into: " + fileName
            with open(fileName, 'ab') as csvfile:
                fieldnames = ['key', 'x', 'y', 'height', 'width']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                for row in listOfDicts:
                    print row
                    writer.writerow({'key': row.values()[2], 'x': row.values()[1], 'y': row.values()[0]
                                        , 'height': row.values()[3], 'width': row.values()[4]})

        except:
            print ("file not found or not correct format.")
            
        self.mainWindow.externalCommClass.previous_state_logging.add("previousWidgetConfig", str(fileName))



    def loadConfigs(self, *file):
        # open a file dialog and pick a file to save in:
        fileWidget = QtGui.QWidget()
        fileWidget.resize(320, 240)
        # Sets dialog to open at a particular directory
        print ("Opening file dialog.")
        if len(file) == 0:
            fileName = QtGui.QFileDialog.getOpenFileName(fileWidget, 'Open File', 'savedLayoutConfigs')
        else:
            fileName = file[0]
        print fileName
        try:
            if platform == "win32":
                fileName = fileName.replace('/', '\\')
            print "loading configs from: " + fileName
            dictionary = {}
            with open(fileName, 'rb') as csvfile:
                fieldnames = ['key', 'x', 'y', 'height', 'width']
                reader = csv.DictReader(csvfile, fieldnames=fieldnames)

                #close all widgets first:

                if self.mainWindow.mapWidget:
                    self.mainWindow.mapWidget.parent().close()
                if self.mainWindow.embeddedWidget:
                    self.mainWindow.embeddedWidget.parent().close()
                if self.mainWindow.computerVisionWidget:
                    self.mainWindow.computerVisionWidget.parent().close()
                if self.mainWindow.manualControlWidget:
                    self.mainWindow.manualControlWidget.parent().close()
                if self.mainWindow.missionCommanderWidget:
                    self.mainWindow.missionCommanderWidget.parent().close()
                if self.mainWindow.dataGraphingWidget:
                    self.mainWindow.dataGraphingWidget.parent().close()
                if self.mainWindow.controlSystemWidget:
                    self.mainWindow.controlSystemWidget.parent().close()
                # Loop through the file to add the values into the dictionary from this file.
                for row in reader:
                    currentWidget = str(row.values()[3])


                    x = int(row.values()[1])
                    y = int(row.values()[0])
                    height = int(row.values()[2])
                    width = int(row.values()[4])
                    qrect = QtCore.QRect(x, y, width, height)
                    print currentWidget
                    print qrect
                    if currentWidget == "mainWindowWidget":
                        self.mainWindow.mainWindowWidget.parent().setGeometry(qrect)
                    if currentWidget == "mapWidget":
                        self.mainWindow.add_mapWidget()
                        self.mainWindow.mapWidget.parent().setGeometry(qrect)
                    if currentWidget == "embeddedWidget":
                        self.mainWindow.add_embeddedWidget()
                        self.mainWindow.embeddedWidget.parent().setGeometry(qrect)
                    if currentWidget == "computerVisionWidget":
                        self.mainWindow.add_computerVisionWidget()
                        self.mainWindow.computerVisionWidget.parent().setGeometry(qrect)
                    if currentWidget == "manualControlWidget":
                        self.mainWindow.add_manualControlWidget()
                        self.mainWindow.manualControlWidget.parent().setGeometry(qrect)
                    if currentWidget == "missionCommanderWidget":
                        self.mainWindow.add_missionCommanderWidget()
                        self.mainWindow.missionCommanderWidget.parent().setGeometry(qrect)
                    if currentWidget == "dataGraphingWidget":
                        self.mainWindow.add_dataGraphingWidget()
                        self.mainWindow.dataGraphingWidget.parent().setGeometry(qrect)
                    if currentWidget == "controlSystemWidget":
                        self.mainWindow.add_controlSystemWidget()
                        self.mainWindow.controlSystemWidget.parent().setGeometry(qrect)


            self.mainWindow.externalCommClass.previous_state_logging.add("previousWidgetConfig", str(filename))


                #loop through dictionary and use widget values
                #for row in dictionary:


        except:
            print ("file not found or not correct format.")

