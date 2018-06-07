import sys
import time
from PyQt4 import *
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import QPixmap, QTimer, QColor
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import math
import cv2
import numpy as np


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.position = [0,0,0]
        self.running = True
        self.heading = 0
        
        self.fourcc = cv2.VideoWriter_fourcc(*"H264")
        self.output = cv2.VideoWriter("output.avi", -1, 20, (640,480))
        
        dataFile = open("data.data", "r")
        line = dataFile.readline()
        self.index = 0
        self.data = []
        while line:
            lineData = []
            line = line.split(']')
            line[0] = line[0][1:]
            line[1] = line[1][2:]
            line[2] = line[2][2:]
            
            for i,v in enumerate(line):
                m = v.split(" ")
                for d in m:
                    if d in ["", "\n", " ", " \n"]:
                        continue
                    lineData.append(float(d.replace(",", "")))
            self.data.append(lineData)
            line = dataFile.readline()
        dataFile.close()

        
    def initUI(self):      
        self.setGeometry(300, 300, 640, 480)
        self.show()

    def calculate1(self, xVel, yVel, heading):
        timeVelEstX = 1
        timeVelEstY = 1
        degToRad = 3.1415926535 / 180
        velNcompX = (xVel) * round(math.cos(heading * degToRad))
        velNcompY = (yVel) * -round(math.sin((heading) * degToRad))

        velEcompX = (xVel) * -round(math.sin(heading * degToRad))
        velEcompY = (yVel) * round(math.cos((heading) * degToRad))

        lastDistanceTraveledN = (velNcompX * timeVelEstX*100) + (
                    velNcompY * timeVelEstY*100)# * 1000 / 1.74
        lastDistanceTraveledE = (velEcompX * timeVelEstX*100) + (
                    velEcompY * timeVelEstY*100)# * 1000 / 1.74

        #Add distance traveled to last known position
        #North
        self.position[0] = self.position[0] - lastDistanceTraveledN
        #East
        self.position[1] = self.position[1] + lastDistanceTraveledE



    def calculate2(self, xVel, yVel, heading):
        timeVelEstX = 1
        timeVelEstY = 1
        degToRad = 3.1415926535 / 180
        velNcompX = (xVel) * -round(math.cos(math.radians(heading)))
        velNcompY = (yVel) * round(math.cos(math.radians(heading + 90)))

        velEcompX = (xVel) * -round(math.sin(math.radians(heading)))
        velEcompY = (yVel) * -round(math.sin(math.radians(heading+ 90)))
        print velEcompX, velEcompY

        lastDistanceTraveledN = (velNcompX * timeVelEstX*100) + (
                    velNcompY * timeVelEstY*100)# * 1000 / 1.74
        lastDistanceTraveledE = (velEcompX * timeVelEstX*100) + (
                    velEcompY * timeVelEstY*100)# * 1000 / 1.74

        #Add distance traveled to last known position
        #North
        self.position[0] = self.position[0] - lastDistanceTraveledN
        #East
        self.position[1] = self.position[1] + lastDistanceTraveledE

    def update(self):
        #Read Data
        if self.running == False:
            return
        if self.index >= len(self.data):
            print "Finished"
            self.running = False
            self.finish()
            return
        data = self.data[self.index]
        self.index+=1
        
        xVel = data[0]
        yVel = data[1]
        self.heading = data[3]
        heading = data[3]
        self.calculate2(xVel,yVel,heading)

        #Draw
        self.repaint()
        
        #Take Screenshot
        self.takeScreenshot()

        #Add to video

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QColor(0,0,0))
        qp.drawLine(0, 240, 640, 240)
        qp.drawLine(320, 0, 320, 480)
        
        qp.setBrush(QBrush(QColor(255,0,0), Qt.SolidPattern))
        rad = 20
        scale = .05
        qp.drawEllipse(int(self.position[1] * scale)-(rad/2) + 320, int(self.position[0] * scale)-(rad/2) + 240, rad, rad)
        
        qp.setPen(QColor(0,0,255))
        lineLength = 20
        qp.drawLine(int(self.position[1] * scale)+ 320, int(self.position[0] * scale)+ 240, int(self.position[1] * scale) + 320 + (lineLength * math.sin(math.radians(self.heading))), int(self.position[0] * scale)+ 240 -(lineLength * math.cos(math.radians(self.heading))))
        qp.end()
        
    def takeScreenshot(self):            
        p = QPixmap.grabWindow(self.winId())
        #p.save("Test.jpg", "jpg")
        img = p.toImage().convertToFormat(QtGui.QImage.Format_RGB32)
        height = img.height()
        width = img.width()
        s = img.bits().asstring(img.width() * img.height() * 4)
        newImg = np.fromstring(s, dtype=np.uint8).reshape((height, width, 4)) 
        #newImg = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        cv2.imshow("Test", newImg)
        self.output.write(newImg)
        
    def finish(self):
        self.output.release()
        
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()