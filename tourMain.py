import sys

#Adding Modules to the system path
sys.path.insert(0, 'LaserModule')
sys.path.insert(0, 'MovementModule')
sys.path.insert(0, 'ExampleCode/TourDemo')

#Adding Modules:
from pydexarm import Dexarm
import laser_module as l_m

import constantsTour as c
import time
import keyboard
import threading
import sys
import serial
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

def pickObjectStack(robotFeedrate):
    laserDexarm.move_to(*c.LASER_CLEAR,wait=False)
    pickerDexarm.move_to(*c.PICKER_CLEAR,feedrate=robotFeedrate)
    
    
    blockLocation = c.STACK_PICK_UP; 
    pickerDexarm.move_to(blockLocation[0],blockLocation[1],feedrate=robotFeedrate)
    pickerDexarm.move_to(z=blockLocation[2],feedrate=robotFeedrate)
    pickerDexarm.air_picker_pick()
    pickerDexarm.move_to(z=c.PICKER_CLEAR[2],feedrate=robotFeedrate)



def dropObjectLaser(robotFeedrate):
    pickerDexarm.move_to(0,300,0,feedrate=robotFeedrate)
    pickerDexarm.move_to(*c.LASER_DROP_OFF,feedrate=robotFeedrate)
    pickerDexarm.air_picker_place()
    pickerDexarm.move_to(c.LASER_DROP_OFF[0],c.LASER_DROP_OFF[1],c.LASER_DROP_OFF[2]+30,feedrate=robotFeedrate)
    pickerDexarm.air_picker_stop()
    pickerDexarm.move_to(0,300,0,feedrate=robotFeedrate)
    pickerDexarm.move_to(*c.PICKER_CLEAR,feedrate=robotFeedrate)

def laserObject():
    laserDexarm.go_home()
    #File Name:
    fileLocName = "LaserModule/rotricsGcode/CircleOutline.gcode";
    
    #Set laser object center, angle, height/width, laser power:
    circle_prop = l_m.Laser_Object_Properties(fixHeight=False,centerPoint=[0,310],specifiedLength=10,laserPower=1,angle=0)
    circle_prop.movingFeedrate=10000;
    circle_prop.laseringFeedrate=800;
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,circle_prop)

    #Run the Laser
    l_m.runLaser(laserDexarm)

def pickObjectLaser(robotFeedrate):
    pickerDexarm.move_to(*c.LASER_DROP_OFF,feedrate=robotFeedrate);
    pickerDexarm.move_to(z=c.LASER_DROP_OFF[2]-10,feedrate=robotFeedrate)
    pickerDexarm.air_picker_pick()
    pickerDexarm.move_to(z=c.LASER_DROP_OFF[2]+50,feedrate=robotFeedrate);


def dropObjectConveyor(robotFeedrate):
    pickerDexarm.move_to(0,300,0,feedrate=robotFeedrate)
    pickerDexarm.move_to(*c.PICKER_CLEAR,feedrate=robotFeedrate)
    pickerDexarm.move_to(*c.CONVEYOR_DROP_OFF,feedrate=robotFeedrate)
    pickerDexarm.air_picker_place()
    time.sleep(0.5)
    pickerDexarm.air_picker_stop()
    # pickerDexarm.move_to(*c.PICKER_CLEAR,feedrate=robotFeedrate)

def moveConveyor():
    pickerDexarm.conveyor_belt_move(c.CONVEYOR_DISTANCE,c.CONVEYOR_SPEED)
def pickObjectConveyor(robotFeedrate):
    sliderDexarm.move_to(c.CONVEYOR_PICK_UP[0],c.CONVEYOR_PICK_UP[1],c.CONVEYOR_PICK_UP[2]+50,feedrate=robotFeedrate)
    sliderDexarm.move_to(e=c.CONVEYOR_PICK_UP[3])

    sliderDexarm.move_to(*c.CONVEYOR_PICK_UP)
    sliderDexarm.air_picker_place()
    sliderDexarm.move_to(z=c.CONVEYOR_PICK_UP[2]+20);

def dropObjectStack(robotFeedrate):
    sliderDexarm.move_to(c.STACK_DROP_OFF[0],c.STACK_DROP_OFF[1],c.STACK_DROP_OFF[2]+115,c.STACK_DROP_OFF[3],feedrate=robotFeedrate)
    sliderDexarm.move_to(z=c.STACK_DROP_OFF[2])
    sliderDexarm.air_picker_pick()
    sliderDexarm.move_to(z=c.STACK_DROP_OFF[2]+115)
    sliderDexarm.air_picker_stop()
    sliderDexarm.go_home()

def FirstLoop():
    pickObjectStack(30000);
    dropObjectLaser(30000)
    l_m.LaserDoorClose()
    laserObject()
    laserDexarm.move_to(*c.LASER_CLEAR,feedrate=30000,wait=True)
    time.sleep(1.5)
    l_m.LaserDoorOpen()
    pickObjectLaser(30000)
    dropObjectConveyor(30000)

def SecondLoop():
    moveConveyor();
    pickObjectConveyor(30000)
    dropObjectStack(10000)

if __name__ == "__main__":
    l_m.initializeArduino(False);
    initializeRobotArms()
    startTime = time.monotonic_ns()
    FirstLoop()
    firstLoopTime = (time.monotonic_ns()-startTime)*10**-9

    startTime = time.monotonic_ns()
    SecondLoop()
    secondLoopTime = (time.monotonic_ns()-startTime)*10**-9
    
    print("First Loop:", firstLoopTime)
    print("Second Loop",secondLoopTime)

