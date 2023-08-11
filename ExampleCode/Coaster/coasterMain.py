#Coaster Line Script
import sys

#Adding Modules to the system path
sys.path.insert(0, 'ImageModule')
sys.path.insert(0, 'LaserModule')
sys.path.insert(0, 'MovementModule')


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
    sliderDexarm = Dexarm(port="COM19")
    laserDexarm.go_home()
    sliderDexarm.go_home()
    pickerDexarm.go_home()
    sliderDexarm.sliding_rail_init();
def initializeCamera():
    global camera0
    camera0 = i_m.Camera_Object(cameraNum=0,cameraType=i_m.BIG_CAMERA)


def laserCoaster():
    l_m.gcode_message_creation("CAR",50,False,200,(0,300))
    l_m.runLaser(laserDexarm)
    pass

def pickerHide(feedrate):
    #Go to location so laser door doesn't hit arm
    pickerDexarm.move_to(*c.PICKER_CLEAR,feedrate=feedrate,wait=True)

def laserHide(feedrate):
    laserDexarm.move_to(*c.LASER_CLEAR,feedrate=feedrate)

def pickUpNewCoaster(feedrate):
    #Go to new coaster location:
    cLoc = c.COASTER_PICKUP
    pickerDexarm.move_to(cLoc[0],cLoc[1],cLoc[2]+8, feedrate=feedrate)
    pickerDexarm.move_to(*c.COASTER_PICKUP, feedrate=feedrate)
    
    #Pick up coaster
    pickerDexarm.air_picker_pick()
    time.sleep(0.5)
    
    #Move up 25 mm in z:
    pickerDexarm._send_cmd("G92 X0 Y0 Z0\r"); #Zeros position
    pickerDexarm.move_to(z=25,feedrate=feedrate)
    pickerDexarm._send_cmd("G92.1\r");#Resets to home

def dropCoasterLaser(feedrate):
    pickerDexarm.move_to(*c.LASER_DROP_OFF,feedrate=feedrate)
    pickerDexarm.air_picker_stop()

def getNewCoaster(feedrate):
    pickUpNewCoaster(feedrate)
    l_m.LaserDoorOpen()
    laserHide(feedrate)
    dropCoasterLaser(feedrate)

    pickerDexarm.go_home()
    pickerHide(feedrate)
    
    print(pickerDexarm.get_current_position())
    l_m.LaserDoorClose()

def CoasterLaser2Conveyor(feedrate):
    #Pick up Coaster
    pickerDexarm.go_home()
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
    l_m.LaserDoorOpen()
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
    
def getCoasterDetail(feedrate):
    pickerDexarm.move_to(*c.IMAGE_READ,feedrate= feedrate)
    return getWordNow(camera=camera0)





def coasterContainer(word,feedrate,conveyorSpeed):
    #Move picker robot out of the way
    pickerHide(feedrate);
    
    if word== "DOG":
        pickerDexarm.conveyor_belt_move(-650,conveyorSpeed)
    elif word =="CAR":
        containerCoaster(feedrate)



def containerCoaster(feedrate):

    cLoc = c.COASTER_CONVEYOR

    #Move sliding Robot to coaster:
    sliderDexarm.move_to(e=600,feedrate=2000);
    sliderDexarm.move_to(cLoc[0],cLoc[1],cLoc[2]+10, feedrate=feedrate)
    sliderDexarm.move_to(cLoc[0],cLoc[1],cLoc[2], feedrate=feedrate)

    #Pick Up coaster:
    sliderDexarm._send_cmd("M1000\r")
    sliderDexarm.move_to(cLoc[0],cLoc[1],cLoc[2]+20, feedrate=feedrate)

    #Drop off Coaster:
    sliderDexarm.move_to(e=300,feedrate=2000);
    sliderDexarm.move_to(*c.CONVEYOR_CONTAINER)
    sliderDexarm._send_cmd("M1001\r")
    sliderDexarm.air_picker_stop()

if __name__ == "__main__":


    #Initialize:
    initializeRobotArms()
    l_m.initializeArduino()
    initializeCamera()

    #Pick up new Coaster, open laser door, drop off coaster to laser, Close Laser door
    getNewCoaster(16000)

    # time.sleep(5)
    laserCoaster()

    #Open Laser door, pick up coaster, drop off coaster at Conveyor
    conveyorDropOff(16000)

    # #Analyze Coaster for words
    word=getCoasterDetail(16000)
    print(word)

    #Put Coaster in right Container
    coasterContainer(word,16000,4000)     
