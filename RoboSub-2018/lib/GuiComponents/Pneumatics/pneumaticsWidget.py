from PyQt4 import QtCore, QtGui
from lib.Utils.SlideEdit import SlideEdit
from ui_pneumatics import Ui_Form

class PneumaticsWidget(QtCore.QObject):
    
	def __init__(self, externalComm):
		QtCore.QObject.__init__(self)
		self.ui_Pneumatics = Ui_Form()
		self.externalComm = externalComm
        
        
	def connectSignals(self):
		self.ui_Pneumatics.torpedo1Button.clicked.connect(self.fireTorpedo1)
		self.ui_Pneumatics.torpedo2Button.clicked.connect(self.fireTorpedo2)
		self.ui_Pneumatics.dropper1Button.clicked.connect(self.fireDropper1)
		self.ui_Pneumatics.dropper2Button.clicked.connect(self.fireDropper2)

			
	def fireTorpedo1(self):
		mother = getattr(self.externalComm.externalCommThread, "motherPackets", None)
		if mother != None:
			mother.sendWeapon13Command()
		else:
			print "Motherboard isn't defined yet"
		
	def fireTorpedo2(self):
		mother = getattr(self.externalComm.externalCommThread, "motherPackets", None)
		if mother != None:
			mother.sendWeapon12Command()
		else:
			print "Motherboard isn't defined yet"
		
	def fireDropper1(self):
		mother = getattr(self.externalComm.externalCommThread, "motherPackets", None)
		if mother != None:
			mother.sendWeapon11Command()
		else:
			print "Motherboard isn't defined yet"
		
	def fireDropper2(self):
		mother = getattr(self.externalComm.externalCommThread, "motherPackets", None)
		if mother != None:
			mother.sendWeapon10Command()
		else:
			print "Motherboard isn't defined yet"
