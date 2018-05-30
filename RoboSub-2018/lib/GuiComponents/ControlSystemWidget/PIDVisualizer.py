'''
Copyright 2018, Mechatronics, All rights reserved.  
:Author: David Pierce Walker-Howell
:Date: Created on Mar 27, 2018
:Description: Contains a pyqtgraphing widget to be inserted into a PyQt4 GUI for real-time PID error visualization.
'''
import pyqtgraph as pg
import numpy as np
from PyQt4 import QtGui, QtCore
import sys
import random
import time
import math

class PIDVisualizer(QtGui.QWidget):
	def __init__(self, targetValue=0, currentValue=0, timeWindow=10, sampleTimeInterval=.01):
		'''
		Initialization of PIDVisualization parameters for the real-time dynamic PID Plotting widget.

		Parameters
			-targetValue: The set desired position(for sensor data) the PID controller is attempting to converge on
			-currentValue:	The current position of sensor data the PID controller is operation on.
			-timeWindow: 	The time span the graph shows in seconds. By default this is 10 seconds.
			-sampleTimeInterval:	The graph update rate in seconds. By default this is 0.01 seconds 
		Returns
			-N/A
		'''
		QtGui.QWidget.__init__(self)

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
		'''
		Initialize the specification for the real-time graph. NOTE: To actually add the graph widget to a GUI,
		add classInstance.plt as the widget.

		Parameters:
			N/A
		Returns:
			N/A
		'''
		#Initialize the PlotWidget(the widget to be added into the Qt Gui)
		self.plt = pg.PlotWidget(title="PID Visualizer")
		self.plt.resize(600, 250)	#size: 600x250
		self.plt.showGrid(x=True, y=True)
		self.plt.setLabel('left', 'Sensor Data(error)')
		self.plt.setLabel('bottom', 'Time')

		#Set the colors of each curve: Red for target, green for current values
		self.curve1Color = pg.mkPen(color=(0, 255, 0))
		self.curve2Color = pg.mkPen(color=(255, 0, 0))

		#Add a Legend for the data
		self.plt.addLegend()

		#Plot the current value and target value of sensor data
		self.curve1 = self.plt.plot(self.xAxisTimeFrame, self.yAxisCurrentValue, pen=self.curve1Color, name="Current Value")
		self.curve2 = self.plt.plot(self.xAxisTimeFrame, self.yAxisTargetValue, pen=self.curve2Color, name="Target Value")
		
		#Initialize a timer signal to signal the graph to update every sampleTimeInterval seconds
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.__updateGraph__)	#call the updateGraph slot to update graph
		self.timer.start(self.sampleTimeInterval)

	def setTargetValue(self, targetValue, currentValue):
		'''
		Setter function to set the targetValue and currentvalue each when updating the graph.
		Calculate the residual error from the targetValue and currentValue. Lastly the function
		updates the targetValues numpy array to be plotted.

		Parameters:
			-targetValue: The set desired position(for sensor data) the PID controller is attempting to converge on
			-currentValue:	The current position of sensor data the PID controller is operation on.
		Returns:
			N/A	
		'''
		self.targetValue = targetValue
		self.currentValue = currentValue
		self.error = self.targetValue - self.currentValue
		#update graph to show line at new target value
		self.yAxisTargetValue = targetValue * np.ones(int(self.bufferSize), dtype=np.float)

	def updateValues(self, targetValue, currentValue):
		'''
		Update the targetValue and currentValue from the PID controller. This should be called constantly by the PID
		controller each time the targetValue or currentValue changes.

		Parameters:
			-targetValue: The set desired position(for sensor data) the PID controller is attempting to converge on
			-currentValue:	The current position of sensor data the PID controller is operation on.
		Returns:
			N/A	
		'''
		self.setTargetValue(targetValue, currentValue)

		#running buffer where new data is inserted at the end and old data is truncated
		self.yAxisCurrentValue = (np.append(self.yAxisCurrentValue, currentValue))[1:]

		#Plot the current value and target value of sensor data
		self.curve1.setData(self.xAxisTimeFrame, self.yAxisCurrentValue)
		self.curve2.setData(self.xAxisTimeFrame, self.yAxisTargetValue)
	
	def clearYAxisData(self, targetValue=0, currentValue=0):
		'''
		Clear/Reset the data plot buffers. This is typically called when switching between different PID controller
		graphs.

		Parameters:
			-targetValue: The set desired position(for sensor data) the PID controller is attempting to converge on.
						  By default this is 0 when clearing the data buffers.
			-currentValue:	The current position of sensor data the PID controller is operation on.
							By default this is 0 when clearing the data buffers.
		Returns:
			N/A	
		'''
		self.setTargetValue(targetValue, currentValue)
		self.yAxisCurrentValue = self.yAxisCurrentValue * self.currentValue
		self.yAxisTargetValue = self.yAxisTargetValue * self.targetValue

	def __updateGraph__(self):
		'''
		The callback/slot called by the Qtcore Timer to update the real-time graph.

		Parameters
			N/A
		Returns
			N/A
		'''
		#Plot the current value and target value of sensor data
		self.curve1.setData(self.xAxisTimeFrame, self.yAxisCurrentValue)
		self.curve2.setData(self.xAxisTimeFrame, self.yAxisTargetValue)

if __name__ == "__main__": 
	#The PID Visualizer widget should exist within a Qt gui
	app = QtGui.QApplication(sys.argv)
	w = QtGui.QWidget()
	PIDPlotter = PIDVisualizer()
	layout = QtGui.QGridLayout()

	#To add the PID Plot widget, add PIDVisualizer.plt into the addWidget.
	layout.addWidget(PIDPlotter.plt, 0, 1, 3, 1)
	w.setLayout(layout)
	w.show()

	sys.exit(app.exec_())
