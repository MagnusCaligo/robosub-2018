import pyqtgraph as pg
import numpy as np
from PyQt4 import QtGui, QtCore
import sys
import random
import time
import math

class PIDVisualizer(QtGui.QWidget):
	def __init__(self, targetValue=0, currentValue=0, timeWindow=10, sampleTimeInterval=.01):
		
		QtGui.QWidget.__init__(self)

		'''
		Sensor Data Values:
		-Target Value is the sensor value the PID controller is trying to converge on.
		-Current Values is the current value of the sensor
		'''
		self.targetValue = targetValue
		self.currentValue = targetValue

		#The x-axis time frame to show data(if timeWindow = 10, then you will see 10 seconds of data plots)
		self.timeWindow = timeWindow
		self.sampleTimeInterval = sampleTimeInterval 	#Update rate of graph
		self.bufferSize = timeWindow/sampleTimeInterval	#Size of sensor data array that will be updated and plotted at each time sample
		self.error = targetValue-currentValue 			
		self.xAxisTimeFrame = np.linspace(0, 10, self.bufferSize)	#Evenly scaled matrix to plot sensor data against
		self.yAxisCurrentValue = currentValue * np.ones(int(self.bufferSize), dtype=np.float) #current value of the data stored in a list of size buffersize
		self.yAxisTargetValue = targetValue * np.ones(int(self.bufferSize), dtype=np.float) #Target value which will be plot as a horizontal line on the graph

		#initialize the graph 
		self.init_graph()

	def init_graph(self):
		self.plt = pg.PlotWidget(title="PID Visualizer")
		self.plt.resize(600, 250)
		self.plt.showGrid(x=True, y=True)
		self.plt.setLabel('left', 'Sensor Data')
		self.plt.setLabel('bottom', 'Time')

		#Set the colors of each curve: Red for target, green for current values
		self.curve1Color = pg.mkPen(color=(0, 255, 0))
		self.curve2Color = pg.mkPen(color=(255, 0, 0))

		#Add a Legend for the data
		self.plt.addLegend()

		#Plot the current value and target value of sensor data
		self.curve1 = self.plt.plot(self.xAxisTimeFrame, self.yAxisCurrentValue, pen=self.curve1Color, name="Current Value")
		self.curve2 = self.plt.plot(self.xAxisTimeFrame, self.yAxisTargetValue, pen=self.curve2Color, name="Target Value")
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.__updateGraph__)
		self.timer.start(self.sampleTimeInterval)

	def setTargetValue(self, targetValue, currentValue):
		self.targetValue = targetValue
		self.currentValue = currentValue
		self.error = self.targetValue - self.currentValue
		#update graph to show line at new target value

	def updateValues(self, targetValue, currentValue):
		self.setTargetValue(targetValue, currentValue)

		#running buffer where new data is inserted at the end and old data is truncated
		self.yAxisCurrentValue = (np.append(self.yAxisCurrentValue, currentValue))[1:]

		#Plot the current value and target value of sensor data
		self.curve1.setData(self.xAxisTimeFrame, self.yAxisCurrentValue)
		self.curve2.setData(self.xAxisTimeFrame, self.yAxisTargetValue)
	
	def clearYAxisData(self, targetValue=0, currentValue=0):
		self.setTargetValue(targetValue, currentValue)
		self.yAxisCurrentValue = self.yAxisCurrentValue * self.currentValue
		self.yAxisTargetValue = self.yAxisTargetValue * self.targetValue

	def dummyTestData(self):
		frequency = 0.5
		noise = random.normalvariate(0., 1.)
		currentValue = 10.*math.sin(time.time()*frequency*2*math.pi) + noise
		return currentValue

	def __updateGraph__(self):
		#Plot the current value and target value of sensor data
		#self.updateValues(10, 10, 10, 0, self.dummyTestData())
		self.curve1.setData(self.xAxisTimeFrame, self.yAxisCurrentValue)
		self.curve2.setData(self.xAxisTimeFrame, self.yAxisTargetValue)


app = QtGui.QApplication(sys.argv)
w = QtGui.QWidget()
PIDPlotter = PIDVisualizer()
layout = QtGui.QGridLayout()
layout.addWidget(PIDPlotter.plt, 0, 1, 3, 1)
w.setLayout(layout)
w.show()

sys.exit(app.exec_())
