#Coaster Line Script

import sys
# adding folder to the system path
sys.path.insert(0, '../../')
import time
from pydexarm import Dexarm
import keyboard
import threading
import sys
import constants as c



def initializeRobotArms():
    global laserDexarm, pickerDexarm, sliderDexarm
    laserDexarm = Dexarm(port="COM4")
    pickerDexarm = Dexarm(port="COM6")
    sliderDexarm = Dexarm(port="COM3")
    laserDexarm.go_home()
    sliderDexarm.go_home()
    pickerDexarm.go_home()


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

def laserDoorOpen():
    pass

def pickerHide(feedrate):
    #Go to location so laser door doesn't hit arm
    pickerDexarm.move_to(*c.PICKER_CLEAR,feedrate=feedrate)

def laserDoorClose():
    pass

def laserHide(feedrate):
    laserDexarm.move_to(*c.LASER_CLEAR,feedrate=feedrate)

def getNewCoaster(feedrate):
    pickUpNewCoaster(feedrate)
    laserDoorOpen()
    laserHide(feedrate)
    dropCoasterLaser(feedrate)
    pickerHide(feedrate)
    laserDoorClose()

def laserCoaster():
    time.sleep(10)
    pass

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


if __name__ == "__main__":
    initializeRobotArms()
    getNewCoaster(16000)
    laserCoaster()
    conveyorDropOff(16000)
    pickerDexarm.conveyor_belt_backward(speed=2000)
    time.sleep(5)
    pickerDexarm.conveyor_belt_stop()