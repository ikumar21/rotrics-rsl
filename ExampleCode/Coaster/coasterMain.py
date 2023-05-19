#Coaster Line Script

import sys
# adding folder to the system path
sys.path.insert(0, '../../')
sys.path.insert(0, '../../imageFunc')
sys.path.insert(0, '../../laserFunc')
import time
from pydexarm import Dexarm
import keyboard
import threading
import sys
import constants as c
import serial
import image_module as i_m
import laser_module as l_m
import cv2



def initializeRobotArms():
    global laserDexarm, pickerDexarm, sliderDexarm
    laserDexarm = Dexarm(port="COM4")
    pickerDexarm = Dexarm(port="COM6")
    sliderDexarm = Dexarm(port="COM3")
    laserDexarm.go_home()
    sliderDexarm.go_home()
    pickerDexarm.go_home()

def initializeCamera():
    global camera0
    camera0 = i_m.Camera_Object(cameraNum=0,cameraType=i_m.BIG_CAMERA)

def initializeArduino():
    global laserArduinoSerial
    laserArduinoSerial = serial.Serial("COM5", 115200, timeout=0.1)
def laserDoorClose():
    message = "$C\r\n"
    laserArduinoSerial.write((bytes(message, 'utf-8')))
    time.sleep(10)
    pass
def laserDoorOpen():
    message = "$O\r\n"
    laserArduinoSerial.write((bytes(message, 'utf-8')))
    time.sleep(10)
    pass

def laserCoaster():
    #dogProp = l_m.Laser_Object_Properties(False,[0,300],60,125,0)
    l_m.gcode_message_creation("CAR",50,False,200,(0,300))
    l_m.runLaser(laserDexarm)
    pass

def pickerHide(feedrate):
    #Go to location so laser door doesn't hit arm
    pickerDexarm.move_to(*c.PICKER_CLEAR,feedrate=feedrate)

def laserHide(feedrate):
    laserDexarm.move_to(*c.LASER_CLEAR,feedrate=feedrate)

def pickUpNewCoaster(feedrate):
    #Go to new coaster location:
    cLoc = c.COASTER_PICKUP
    pickerDexarm.move_to(cLoc[0],cLoc[1],cLoc[2]+8, feedrate=feedrate)
    pickerDexarm.move_to(*c.COASTER_PICKUP, feedrate=feedrate)
    
    #Pick up coaster
    pickerDexarm.air_picker_pick()
    
    #Move up 25 mm in z:
    pickerDexarm._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
    pickerDexarm.move_to(z=25,feedrate=feedrate)
    pickerDexarm._send_cmd("G92.1\r");#Resets to home

def dropCoasterLaser(feedrate):
    pickerDexarm.move_to(*c.LASER_DROP_OFF,feedrate=feedrate)
    pickerDexarm.air_picker_stop()

def getNewCoaster(feedrate):
    pickUpNewCoaster(feedrate)
    laserDoorOpen()
    laserHide(feedrate)
    dropCoasterLaser(feedrate)
    pickerHide(feedrate)
    laserDoorClose()

def CoasterLaser2Conveyor(feedrate):
    #Pick up Coaster
    pickerDexarm.move_to(*c.LASER_DROP_OFF,feedrate=feedrate)
    pickerDexarm.move_to(*c.LASER_PICK_UP,feedrate=feedrate)
    pickerDexarm.air_picker_pick()
    
    #Clear Laser Frame:
    pickerDexarm.move_to(z=0,feedrate=feedrate)
    
    #Go To Conveyor
    pickerDexarm.go_home()
    pickerDexarm.move_to(*c.CONVEYOR_DROP_OFF,feedrate=feedrate)
    pickerDexarm.air_picker_stop()
    
    #Clear Conveyor
    cLoc = c.CONVEYOR_DROP_OFF
    pickerDexarm.move_to(z=cLoc[2]+20,feedrate=feedrate)
    pickerHide(feedrate)

def conveyorDropOff(feedrate):
    laserDoorOpen()
    laserHide(feedrate)
    CoasterLaser2Conveyor(feedrate)

def getWordNow(camera:i_m.Camera_Object):
    imgWord = camera.GetImageBGR()
    cv2.imwrite("imageWord.png",imgWord)
    imgAnalysis = i_m.Google_Analysis("imageWord.png",analyzeText=True,analyzeObjects=False)
    if(len(imgAnalysis.words)==1):
        return imgAnalysis.words[0].wordText
    else:
        return None
    
def getCoasterDetail(conveyorSpeed,robotFeedrate):
    #Get Coaster to right frame
    pickerDexarm.conveyor_belt_move(-200,conveyorSpeed)
    sliderDexarm.move_to(*c.IMAGE_READ,feedrate= robotFeedrate)
    return getWordNow(camera=camera0)





def coasterContainer(word,feedrate):
    if word== "CAR":
        topContainerCoaster(feedrate)
    elif word =="DOG":
        bottomContainerCoaster(feedrate)

def topContainerCoaster(feedrate):
    cLoc = c.CONVEYOR_TOP_CONTAINER
    sliderDexarm.move_to(cLoc[0],cLoc[1],cLoc[2]+40, feedrate=feedrate)
    sliderDexarm.move_to(cLoc[0],cLoc[1],cLoc[2], feedrate=feedrate)
    sliderDexarm.move_to(cLoc[0],cLoc[1]+5,cLoc[2], feedrate=feedrate)
    sliderDexarm.move_to(cLoc[0],cLoc[1]+150,cLoc[2]-3, feedrate=feedrate)

def bottomContainerCoaster(feedrate):
    pass



if __name__ == "__main__":

    #Initialize:
    initializeRobotArms()
    initializeArduino()
    initializeCamera()

    
    #Pick up new Coaster, open laser door, drop off coaster to laser, Close Laser door
    getNewCoaster(16000)

    laserCoaster()

    #Open Laser door, pick up coaster, drop off coaster at Conveyor
    conveyorDropOff(16000)

    # #Analyze Coaster for words
    word=getCoasterDetail(4000,2000)
    print(word)
    #Put Coaster in right Container
    coasterContainer(word,16000)     
