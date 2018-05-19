from Ui_DataGraphing.ui_dataGraphing import Ui_DataGraphing
from Ui_DataGraphing.ui_updateGraphs import Ui_Dialog
from pyqtgraph.Qt import QtCore, QtGui
from lib.ExternalDevices.external_communication import ExternalComm
from PyQt4.QtGui import QFileDialog

import csv
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

import time


class Graph:
    def __init__(self):
        self.graphName = None
        self.xAxisData = None
        self.yAxisData = None

class DataGraphing(QtCore.QObject):
    """
    Creates the data graphing widget.  The user is able to define
    what data they want to the X or Y axis to show. The user can
    create up to five graphs at a time and can select graphs in
    the settings tab to edit or remove graphs.
    """
    def __init__(self, externalCommClass):
        QtCore.QObject.__init__(self)

        # Ui class
        self.ui_dataGraphing = Ui_DataGraphing()
        self.ui_updateGraph = Ui_Dialog()
        
        # Class instances
        self.chunkSize = None
        self.maxChunks = None
        self.startTime = None
        self.graphWin = None

        # Signal origins (classes a signal may come from)
        self.externalComm = externalCommClass
        self.xData = []
        self.xText, self.yText = None, None
        self.yData = []

        self.graphsDict = {}
        self.pltList = []
        self.curvesList = []
        self.dataList = []
        self.ptrList = []

        self.columnsCount = 2

        self.count = 0
        # Testing
        self.plt = None
        self.graph = None
        self.timer = QtCore.QTimer()


    def connectSignals(self):
        """
        Connect signals.

        ExternalDataReady()  ----> emitted from ExternalComm when data is ready.
        timeout()            ----> emitted when timer times out.

        :return:
        """
        #self.ui_dataGraphing.createGraphButton.clicked.connect(self.addGraph)

        #self.timer.start(100)
        #Set up the Load From File button to open the file explorer.
        self.ui_dataGraphing.loadFileButton.clicked.connect(self.loadFromFile)
        self.ui_dataGraphing.loadFileButton.clicked.connect(self.selectFile)
        self.ui_dataGraphing.xAxisCB.currentIndexChanged.connect(lambda index: self.xChange(index))
        self.ui_dataGraphing.yAxisCB.currentIndexChanged.connect(lambda index: self.yChange(index))


        self.addGraph()

    @QtCore.pyqtSlot()
    def xChange(self, index):
        self.xText = self.ui_dataGraphing.xAxisCB.itemText(index)
        self.graph.xAxisData = self.xText
        self.graph.yAxisData = self.yText
        self.graph.graphName = self.graph.xAxisData + " vs. " + self.graph.yAxisData
        self.plt.setLabel('left', self.graph.yAxisData, 'm')
        self.plt.setLabel('bottom', self.graph.xAxisData, 's')
        self.plt.setLabel('top', self.graph.graphName, None)

    @QtCore.pyqtSlot()
    def yChange(self, index):
        self.yText = self.ui_dataGraphing.yAxisCB.itemText(index)
        self.graph.xAxisData = self.xText
        self.graph.yAxisData = self.yText
        self.graph.graphName = self.graph.xAxisData + " vs. " + self.graph.yAxisData
        self.plt.setLabel('left', self.graph.yAxisData, 'm')
        self.plt.setLabel('bottom', self.graph.xAxisData, 's')
        self.plt.setLabel('top', self.graph.graphName, None)

    @QtCore.pyqtSlot()
    def addGraph(self):
        self.graph = Graph()

        self.graph.xAxisData = self.ui_dataGraphing.xAxisCB.currentText()
        self.xText = self.graph.xAxisData

        self.graph.yAxisData = self.ui_dataGraphing.yAxisCB.currentText()
        self.yText = self.graph.yAxisData

        self.graph.graphName = self.graph.xAxisData + " vs. " + self.graph.yAxisData

        self.setupGraph(self.graph)
        self.connect(self.externalComm, QtCore.SIGNAL("ExternalDataReady()"), self.updateGraph)

    def setupGraph(self, graph):
        """
        Set all the variables for the graph window and the plot itself.
        :return:
        """
        self.graphWin = pg.GraphicsWindow()
        self.graphWin.setWindowTitle(self.graph.graphName)
        self.ui_dataGraphing.graphLayout.addWidget(self.graphWin)
        self.chunkSize = 300
        self.maxChunks = 10
        self.startTime = pg.ptime.time()
        self.graphWin.nextRow()
        self.plt = self.graphWin.addPlot(colspan=self.columnsCount)
        self.plt.setLabel('left', self.graph.yAxisData, 'm')
        self.plt.setLabel('bottom', self.graph.xAxisData, 's')
        self.plt.setLabel('top', self.graph.graphName, None)
        self.plt.setXRange(-10, 0)
        curves = []
        data = np.empty((self.chunkSize + 1, 2))
        ptr = 0
        self.columnsCount += 1

        self.ptrList.append(ptr)
        self.pltList.append(self.plt)
        self.curvesList.append(curves)
        self.dataList.append(data)

    def updateGraph(self, yList):
        """
        Updates the graph in chunks, adding one new plot curve for
        every 100 samples.
        :return:
        """
        # Loop through all the curves setting the X location
        # according to how much time has passed
        self.count += 1
        if self.count == 10:

            self.ahrsData = self.externalComm.ahrsData
            self.dvlData = self.externalComm.dvlData
            self.count = 0

            for plot, curves, data, ptr in zip(self.pltList, self.curvesList, self.dataList, self.ptrList):
                # Loop through all the graphs and update each one
                #for graphs in self.graphsList:
                now = pg.ptime.time()
                for c in curves:
                    c.setPos(-(now - self.startTime), 0)

                # If the plot curve has hit a certain number of samples
                # then make a new plot for the next number of samples
                # and remove the old curve
                i = ptr % self.chunkSize
                if i == 0:
                    curve = plot.plot(pen=(0,255,0))
                    curves.append(curve)
                    last = data[-1]
                    data = np.empty((self.chunkSize + 1, 2))
                    data[0] = last
                    while len(curves) > self.maxChunks:
                        c = curves.pop(0)
                        plot.removeItem(c)
                else:
                    curve = self.curves[-1]

                # Test data
                data[i + 1, 0] = abs(now - self.startTime)
                data[i + 1, 1] = self.yList[1]
                curve.setData(x=data[:i + 2, 0], y=data[:i + 2, 1])
                ptr += 1

    def selectFile(self):
        """
        Opens a file to choose which data to plot. Must be a csv file.
        :return:
        """
        file = QtGui.QFileDialog.getOpenFileName()
        loadFromFile(file)

    def loadFromFile(self, file):
        """
        Load plotting points from a file.
        :return:
        """
        yList = None

        # Open the file they want to read.
        with open(file, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)

            index = 0
            for row[''] in reader:
                yList[index]
                index += 1