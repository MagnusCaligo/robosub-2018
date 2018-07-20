from PyQt4 import QtCore
from PyQt4 import QtGui
from Ui_MissionCommander.ui_missionCommander import Ui_MissionCommander
from Ui_MissionCommander.ui_updateMissionDialog import Ui_Ui_UpdateMissionDialog
import lib.ExternalDevices.Missions as Missions
import json
import os
from pprint import pprint
from lib.Utils.SlideEdit import SlideEdit
from lib.ExternalDevices.movement import MovementController, JoystickMovementController
from lib.ExternalDevices.Mission_Planner_3_Missions.NavigationMission import NavigationMission
from lib.ExternalDevices.Mission_Planner_3_Missions.DiceMission import DiceMission 
from lib.ExternalDevices.Mission_Planner_3_Missions.StartingGateMission import StartingGateMission
from lib.ExternalDevices.Mission_Planner_3_Missions.RouletteMission import RouletteMission
from lib.ExternalDevices.Mission_Planner_3_Missions.TorpedoMission import TorpedoMission


class MissionCommander(QtCore.QObject):
    """
    Class to handle the mission commander widget.
    """
    def __init__(self, externalComm):
        QtCore.QObject.__init__(self)
        self.ui_missionCommander = Ui_MissionCommander()
        self.missionDictionary = {}
        self.stopTime = None
        self.externalComm = externalComm

        if not "missionList" in self.externalComm.guiDataToSend:
            self.externalComm.guiDataToSend["missionList"] = []

        
        self.openFileDialog("./Saved_Missions/missionCommanderPreviousState.txt")

    def connectSignals(self):
	
		
        """
        Connects signals of the missionCommander widget to the
        appropriate slot.
        :return:
        """
#Veronica smells like poo poo 

        self.ui_missionCommander.northTranslation.setMinimum(-500)
        self.ui_missionCommander.northTranslation.setMinimum(-500)
        self.ui_missionCommander.eastTranslation.setMinimum(-500)
        self.ui_missionCommander.eastTranslation.setMaximum(500)
        self.ui_missionCommander.upTranslation.setMinimum(-500)
        self.ui_missionCommander.upTranslation.setMaximum(500)

        self.ui_missionCommander.yawRotation = SlideEdit()
        self.ui_missionCommander.pitchRotation = SlideEdit()
        self.ui_missionCommander.rollRotation = SlideEdit()
		
        self.ui_missionCommander.verticalLayout_5.addWidget(self.ui_missionCommander.yawRotation)
        self.ui_missionCommander.verticalLayout_5.addWidget(self.ui_missionCommander.pitchRotation)
        self.ui_missionCommander.verticalLayout_5.addWidget(self.ui_missionCommander.rollRotation)
		
        self.ui_missionCommander.yawRotation.updateMin(0)
        self.ui_missionCommander.yawRotation.updateMax(360)
        self.ui_missionCommander.yawRotation.setCurrentValue(0)
		
        self.ui_missionCommander.pitchRotation.updateMin(0)
        self.ui_missionCommander.pitchRotation.updateMax(360)
        self.ui_missionCommander.pitchRotation.setCurrentValue(180)
		
        self.ui_missionCommander.rollRotation.updateMin(0)
        self.ui_missionCommander.rollRotation.updateMax(360)
        self.ui_missionCommander.rollRotation.setCurrentValue(180)

        
        #Connects all the buttons and stuff on the Mission Commander Widget
        self.ui_missionCommander.missionTypeCB.currentIndexChanged.connect(self.updateParametersFromCombox)
        self.ui_missionCommander.missionListWidget.currentItemChanged.connect(self.updateSelectedMission)
        self.ui_missionCommander.addMissionButton.clicked.connect(self.createMission)
        self.ui_missionCommander.removeMissionButton.clicked.connect(self.removeMission)
        self.ui_missionCommander.moveUp.clicked.connect(lambda: self.moveMissionPosition(True))
        self.ui_missionCommander.moveDown.clicked.connect(lambda: self.moveMissionPosition(False))
        self.ui_missionCommander.saveMissionList.clicked.connect(lambda: self.saveCurrentState(True))
        self.ui_missionCommander.loadMissionList.clicked.connect(self.openFileDialog)

        self.ui_missionCommander.northTranslation.valueChanged.connect(lambda: self.externalComm.setWaypointX(str(self.ui_missionCommander.missionListWidget.currentItem().text()), float(self.ui_missionCommander.northTranslation.value())) if (self.ui_missionCommander.missionListWidget.currentItem() != None) else None)
        self.ui_missionCommander.eastTranslation.valueChanged.connect(lambda: self.externalComm.setWaypointY(self.ui_missionCommander.missionListWidget.currentItem().text(), self.ui_missionCommander.eastTranslation.value()) if (self.ui_missionCommander.missionListWidget.currentItem() != None) else None)
        self.ui_missionCommander.upTranslation.valueChanged.connect(lambda: self.externalComm.setWaypointZ(self.ui_missionCommander.missionListWidget.currentItem().text(), self.ui_missionCommander.upTranslation.value()) if (self.ui_missionCommander.missionListWidget.currentItem() != None) else None)
        self.ui_missionCommander.yawRotation.valueChanged.connect(lambda: self.externalComm.setWaypointOrientation_Yaw(self.ui_missionCommander.missionListWidget.currentItem().text(), self.ui_missionCommander.yawRotation._currentValue) if (self.ui_missionCommander.missionListWidget.currentItem() != None) else None)
        self.ui_missionCommander.pitchRotation.valueChanged.connect(lambda: self.externalComm.setWaypointOrientation_Pitch(self.ui_missionCommander.missionListWidget.currentItem().text(), self.ui_missionCommander.pitchRotation._currentValue - 180) if (self.ui_missionCommander.missionListWidget.currentItem() != None) else None)
        self.ui_missionCommander.rollRotation.valueChanged.connect(lambda: self.externalComm.setWaypointOrientation_Roll(self.ui_missionCommander.missionListWidget.currentItem().text(), self.ui_missionCommander.rollRotation._currentValue - 180) if (self.ui_missionCommander.missionListWidget.currentItem() != None) else None)

        
        #Connects all the signals with Mission Planner
        self.ui_missionCommander.previousMissionButton.clicked.connect(lambda: self.emit(QtCore.SIGNAL("nextOrPreviousMission(PyQt_PyObject)"), False))
        self.ui_missionCommander.nextMissionButton.clicked.connect(lambda: self.emit(QtCore.SIGNAL("nextOrPreviousMission(PyQt_PyObject)"), True)) 
        
        
        #Resets the mission List and then loads in all the items from the misison list
        self.ui_missionCommander.missionListWidget.clear()
        for i, v in enumerate(self.externalComm.guiDataToSend["missionList"]):
            self.ui_missionCommander.missionListWidget.addItem(QtGui.QListWidgetItem(v.parameters["name"]))
        
    def writeDebugMessage(self, message):
        self.externalComm.mainWindowClass.systemOutput.insertPlainText(str(message) + "\n")
        
    def updateParametersFromCombox(self):
        missionType = str(self.ui_missionCommander.missionTypeCB.currentText())
        

        mission = None
        #Creates the mission by the type
        if missionType == "Navigation v3":
            mission = NavigationMission
        elif missionType == "Dice Mission":
            mission = DiceMission
        elif missionType == "Entry Gate v3":
            mission = StartingGateMission
	elif missionType == "Roulette":
	    mission = RouletteMission
            
        if hasattr(mission, "defaultParameters"):
            self.ui_missionCommander.parameterStringInputs.clear()
            self.ui_missionCommander.parameterStringInputs.setPlainText(mission.defaultParameters)


    def updateSelectedMission(self, missionName):
        '''
        This method is called when an object is clicked on the missionListWidget (The list on the right)
        It will go through and change the rest of the gui to match the parameters of that mission that is selected
        '''
        
        #Make sure that a mission was actually selected
        if missionName == None:
            return
        
        #Finds the misison by its name
        mission = None
        for index, value in enumerate(self.externalComm.guiDataToSend["missionList"]):
            if value.name == missionName.text():
                mission = value
                break
        if mission == None:
            print "Couldn't find mission: " + missionName.text()
            return
        
        
        #Change the combo box to work for the correct mission 
        if isinstance(mission, NavigationMission):
            self.ui_missionCommander.missionTypeCB.setCurrentIndex(1)
        elif isinstance(mission, DiceMission):
            self.ui_missionCommander.missionTypeCB.setCurrentIndex(2)
        elif isinstance(mission, StartingGateMission):
            self.ui_missionCommander.missionTypeCB.setCurrentIndex(3)
        elif isinstance(mission, RouletteMission):
            self.ui_missionCommander.missionTypeCB.setCurrentIndex(4)
	
        
        #Modify the TextLine Edits
        self.ui_missionCommander.missionNameLineEdit.setText(mission.name)
        self.ui_missionCommander.maxTimeLineEdit.setText(str(mission.parameters["maxTime"]))
        self.ui_missionCommander.useGeneralWaypoint.setText("")
        generalWaypoint = mission.parameters['useGeneralWaypoint']
        if generalWaypoint != 0:
            self.ui_missionCommander.useGeneralWaypoint.setText(str(generalWaypoint))

        #Modify the Waypoint
        self.ui_missionCommander.northTranslation.setValue(mission.generalWaypoint[0])
        self.ui_missionCommander.eastTranslation.setValue(mission.generalWaypoint[1])
        self.ui_missionCommander.upTranslation.setValue(mission.generalWaypoint[2])
        self.ui_missionCommander.yawRotation.setCurrentValue(mission.generalWaypoint[3])
        self.ui_missionCommander.pitchRotation.setCurrentValue(mission.generalWaypoint[4]+180)
        self.ui_missionCommander.rollRotation.setCurrentValue(mission.generalWaypoint[5]+180)
        
        #Modify the Checkboxes
        self.ui_missionCommander.useKalmanFilter.setChecked(True)
        if not mission.parameters["useKalmanFilter"] == True:
            self.ui_missionCommander.useKalmanFilter.setChecked(False)
            
        self.ui_missionCommander.useLaser.setChecked(False)
        if mission.parameters["useLaser"] == True:
            self.ui_missionCommander.useLaser.setChecked(True)
            
        #Change the text box to the correct parametersString
        self.ui_missionCommander.parameterStringInputs.clear()
        self.ui_missionCommander.parameterStringInputs.setPlainText(mission.parameters["parametersString"])
        self.saveCurrentState()

        
    def saveCurrentState(self, *filename):
        #Writes the current mission list to a JSON file
        #Defaults to the previousState file
        if len(filename) == 0:
            filename = "./Saved_Missions/missionCommanderPreviousState.txt"
        else:
            fileWidget = QtGui.QWidget()
            fileWidget.resize(320, 240)
            filename = QtGui.QFileDialog.getSaveFileName(fileWidget, 'Save File', '/')
        
        if filename == "":
            return
        if not os.path.isfile(filename):
            return
        
        def jdefault(o):
            _dict = o.__dict__
            if isinstance(o, MovementController) or isinstance(0, JoystickMovementController):
		return None
            return _dict

            return o.__dict__
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(self.externalComm.guiDataToSend["missionList"], default=jdefault))
        
    def moveMissionPosition(self, Up):
        '''
        This will move the misison in the mission list, the 'Up' parameter is whether it needs to be moved up
        or down, True for Up and False for down
        '''
        
        #Finds which mission is selected
        selectedMission = None
        for i in range(self.ui_missionCommander.missionListWidget.count()):
            if self.ui_missionCommander.missionListWidget.item(i).isSelected():
                selectedMission = self.ui_missionCommander.missionListWidget.item(i).text()
        
        #Gets the index in the list of the selected misison 
        index = None
        for i,v in enumerate(self.externalComm.guiDataToSend["missionList"]):
            if v.parameters["name"] == selectedMission:
                index = i
        if index == None:
            return
        
        #removes all the selection, to prevent "updateSelectedMission" from being called
        self.ui_missionCommander.missionListWidget.clearSelection()
        
        if Up:
            if index != 0:
                self.externalComm.guiDataToSend["missionList"].insert(index-1, self.externalComm.guiDataToSend["missionList"].pop(index))
                index -=1
        else:
            if index != len(self.externalComm.guiDataToSend["missionList"])-1:
                self.externalComm.guiDataToSend["missionList"].insert(index+1, self.externalComm.guiDataToSend["missionList"].pop(index))
                index+=1
        
        #Clears the widget and redraws all the missions in the correct order
        self.ui_missionCommander.missionListWidget.clear()
        for i, v in enumerate(self.externalComm.guiDataToSend["missionList"]):
            self.ui_missionCommander.missionListWidget.addItem(QtGui.QListWidgetItem(v.parameters["name"]))
    
        #Selects the mission again in case you want to move more
        self.ui_missionCommander.missionListWidget.item(index).setSelected(True)
        self.saveCurrentState()
        
                

    @QtCore.pyqtSlot()
    def createMission(self):
        """
        Creates the mission and adds it to the missionList. When autonomous mode begins the missionList will
        be sent to mission planner. 
        """
        # Get data from ui elements
        mission = None
        updatingValues = False
        missionType = str(self.ui_missionCommander.missionTypeCB.currentText())
        missionName = str(self.ui_missionCommander.missionNameLineEdit.text())
        
        #If no type is selected, return
        if missionType == "Select a Mission Type":
            return
        
        parameters = {}
        
        #If you are changing the values of a mission, then set the mission to the current misison and
        #set the parameters correctly and set the boolean updatingValues
        for index, value in enumerate(self.externalComm.guiDataToSend["missionList"]):
            if value.name == missionName:
                mission = value
                parameters = value.parameters
                updatingValues = True
                
        
        #Sets all the parameters for the mission based off of the values in the gui
        
        parameters["name"] = missionName
        if self.ui_missionCommander.maxTimeLineEdit.text() == "":
            return
        parameters["maxTime"] = int(self.ui_missionCommander.maxTimeLineEdit.text())
        if self.ui_missionCommander.useGeneralWaypoint.text() == "":
            parameters["useGeneralWaypoint"] = None
        else:
            parameters["useGeneralWaypoint"] = str(self.ui_missionCommander.useGeneralWaypoint.text())
        
        parameters["DirectionToLook"] = True
        if self.ui_missionCommander.lookLeft.isChecked():
            parameters["DirectionToLook"] = False
            
        parameters["useKalmanFilter"] = True
        if not self.ui_missionCommander.useKalmanFilter.isChecked():
            parameters["useKalmanFilter"] = False
        
        parameters["useLaser"] = False
        if self.ui_missionCommander.useLaser.isChecked():
            parameters["useLaser"] = True
            
        parameters["parametersString"] = str(self.ui_missionCommander.parameterStringInputs.toPlainText())
        parameterString = parameters["parametersString"]
        parameterList = parameterString.split("\n")
        for i,v in enumerate(parameterList):
            b = v.split("=")
            if len(b) < 2:
                continue
            b[0] = b[0].replace(" ", "")
            b[1] = b[1].replace(" ", "")
            parameters[b[0]] = b[1]
                
        if updatingValues: 
            mission.parameters = parameters
            self.saveCurrentState()
            return
        
        #Creates the mission by the type
        print "Mission is", missionType 
        if missionType == "Dice Mission":
            mission = DiceMission(parameters)
        elif missionType == "Navigation v3":
            mission = NavigationMission(parameters)
        elif missionType == "Entry Gate v3":
            mission = StartingGateMission(parameters)
        elif missionType == "Roulette":
            mission = RouletteMission(parameters)
            
        mission.parameters["missionType"] = missionType
        mission.name = str(parameters["name"])
        
        

       
        #Adds the misison to the missionListWidget and the missionList and the saves the state of the 
        #misisonList in a JSON file 
        self.ui_missionCommander.missionListWidget.addItem(QtGui.QListWidgetItem(missionName))
        self.externalComm.guiDataToSend["missionList"].append(mission)
        self.saveCurrentState()
        
    def removeMission(self):
        selectedMission = None
        for i in range(self.ui_missionCommander.missionListWidget.count()):
            if self.ui_missionCommander.missionListWidget.item(i).isSelected():
                selectedMission = self.ui_missionCommander.missionListWidget.item(i).text()
        
        #Gets the index in the list of the selected misison 
        index = None
        for i,v in enumerate(self.externalComm.guiDataToSend["missionList"]):
            if v.parameters["name"] == selectedMission:
                index = i
        if index == None:
            return
        
        self.externalComm.guiDataToSend["missionList"].remove(self.externalComm.guiDataToSend["missionList"][index])
        self.ui_missionCommander.missionListWidget.takeItem(index)
        self.saveCurrentState()
        


    @QtCore.pyqtSlot()
    def openFileDialog(self, *filename):
        """
        Opens file search dialog. Used when loading a mission file. Not finished yet.
        :return:
        """
        # Create file widget
        fileWidget = QtGui.QWidget()
        fileWidget.resize(320, 240)
        missionList = []

        # Sets dialog to open at a particular directory
        if len(filename) == 0:
            filenames = QtGui.QFileDialog.getOpenFileNames(fileWidget, 'Open File', '/')
            filename = str(filenames[0])
        else:
            filename = filename[0]
            
        if filename == "":
            return
        
        try:
			with open(filename, "r") as infile:
				missionList = json.load(infile)
        except:
			print "Couldn't Load Mission Commander Previous State"
        
        self.externalComm.guiDataToSend["missionList"] = []
        
        try:
            self.ui_missionCommander.missionListWidget.clear()
        except:
            pass
        
        for i,v in enumerate(missionList):
            missionType = v["parameters"]["missionType"]
            parameters = v["parameters"]
            
            parameterString = parameters["parametersString"]
            parameterList = parameterString.split("\n")
            for n,p in enumerate(parameterList):
                b = p.split("=")
                if len(b) < 2:
                    continue
                b[0] = b[0].replace(" ", "")
                b[1] = b[1].replace(" ", "")
                parameters[b[0]] = b[1]
                
            mission = None
            
            if missionType == "Dice Mission":
                mission = DiceMission(parameters)
            elif missionType == "Navigation v3":
                mission = NavigationMission(parameters)
            elif missionType == "Entry Gate v3":
                mission = StartingGateMission(parameters)
            elif missionType == "Roulette":
                mission = RouletteMission(parameters)
                
            if mission == None:
                print "Didn't load correctly: " + missionType
            
            mission.name = parameters['name']
            mission.generalWaypoint = v["generalWaypoint"]
            self.externalComm.guiDataToSend["missionList"].append(mission)
            try:
                self.ui_missionCommander.missionListWidget.addItem(QtGui.QListWidgetItem(mission.name))
            except:
                pass
        self.saveCurrentState()
        print "Loaded Missions...."
        
