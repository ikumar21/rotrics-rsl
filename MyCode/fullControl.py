"""
Script to move the robot arm freely and/or the sliding rail/conveyor belt
Purpose: See the Robot position in certain locations

Commands:
r->Print robot location
m-> Change movement increment
f-> Change Robot Feedrate (mm/min) 
b-> Change belt speed (mm/min)
v->Change rail step size

a->Move Left by __ mm
d->Move Right by __ mm
s->Move Towards base (- y-axis) by __ mm
w->Move away from base (+ y-axis) by __ mm
Up Arrow key-> Move Up (Away from Table) by __ mm
Down Arrow key-> Move Down (Into Table) by __ mm

If Conveyor:
Left Key-> Move to left with speed __ mm/min
Right Key-> Move to right with speed __ mm/min
Space key-> Stop Conveyor

If Sliding Rail:
Left Key->Move Left by __ mm
Right Key->Move Right by __ mm


"""


import sys
# Add Movement module
sys.path.insert(0, "MovementModule")
from pydexarm import Dexarm

import time
import keyboard
import threading
import sys

#Open communication with dexarm
#Windows: 
dexarm1 = Dexarm(port="COM6")

#First Initialize Dexarm:
#Factory Settings: Home -> (0,300,0)
dexarm1.go_home()#Goes to robot home position


robotConnectedConveyor = False;
robotConnectedRail = False;

def robotPrintLocation():
    dexarm1._send_cmd("G92.1\r");#Resets
    x,y,z,e,_,_,_ =dexarm1.get_current_position()
    print(x,y,z,e, "mm")

def robotLeft(stepIncrement, feedrate):
    dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
    dexarm1.move_to(x=-stepIncrement,feedrate=feedrate)
    dexarm1._send_cmd("G92.1\r");#Resets to home

def robotRight(stepIncrement, feedrate):
    dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
    dexarm1.move_to(x=stepIncrement,feedrate=feedrate)
    dexarm1._send_cmd("G92.1\r");#Resets to home

def robotAway(stepIncrement, feedrate):
    dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
    dexarm1.move_to(y=stepIncrement,feedrate=feedrate)
    dexarm1._send_cmd("G92.1\r");#Resets to home

def robotTowards(stepIncrement, feedrate):
    dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
    dexarm1.move_to(y=-stepIncrement,feedrate=feedrate)
    dexarm1._send_cmd("G92.1\r");#Resets to home

def robotUp(stepIncrement, feedrate):
    dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
    dexarm1.move_to(z=stepIncrement,feedrate=feedrate)
    dexarm1._send_cmd("G92.1\r");#Resets to home

def robotDown(stepIncrement, feedrate):
    dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
    dexarm1.move_to(z=-stepIncrement,feedrate=feedrate)
    dexarm1._send_cmd("G92.1\r");#Resets to home



def getIntInput(strInput):
    input_a = "Filler"
    while(type(input_a)!=int):
        input_a = input(strInput)
        try:
            input_a =int(input_a)
        except:
            print("Error enter integer.")
    return input_a


def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def conveyorMov(speed, runBackwards):
    dexarm1.conveyor_belt_stop()
    if(runBackwards==1):
        dexarm1.conveyor_belt_backward(speed)
    elif(runBackwards==0):
        dexarm1.conveyor_belt_forward(speed)

stepMovSize = 1
speedRobot = 8000;
beltSpeed = 2000;
railStep = 20

if(robotConnectedRail):
    dexarm1.sliding_rail_init()

while True:
    keyboard.read_key()
    #Move Robot arm:
    if keyboard.is_pressed('a'):
        robotLeft(stepMovSize,speedRobot)
    if keyboard.is_pressed('d'):
        robotRight(stepMovSize,speedRobot)
    if keyboard.is_pressed('w'):
        robotAway(stepMovSize,speedRobot)
    if keyboard.is_pressed('s'):
        robotTowards(stepMovSize,speedRobot)
    if keyboard.is_pressed('up arrow'):
        robotUp(stepMovSize,speedRobot)
    if keyboard.is_pressed('down arrow'):
        robotDown(stepMovSize,speedRobot)

    #End Effector Control:
    if keyboard.is_pressed('p'):
        dexarm1.air_picker_pick()
    if keyboard.is_pressed('o'):
        dexarm1.air_picker_stop()
    # if keyboard.is_pressed('down arrow'):
    #     robotDown(stepMovSize,speedRobot)

    #Move accessory:
    if keyboard.is_pressed('left arrow'):
        if(robotConnectedConveyor):
            conveyorMov(beltSpeed, 0)
        elif(robotConnectedRail):
            dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
            dexarm1.move_to(e=-railStep,feedrate=speedRobot)
            dexarm1._send_cmd("G92.1\r");#Resets to home
    if keyboard.is_pressed('right arrow'):
        if(robotConnectedConveyor):
            conveyorMov(beltSpeed, 1)
        elif(robotConnectedRail):
            dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Zeros position
            dexarm1.move_to(e=railStep,feedrate=speedRobot)
            dexarm1._send_cmd("G92.1\r");#Resets to home
    if keyboard.is_pressed('space'): 
        if(robotConnectedConveyor):
            conveyorMov(beltSpeed, -1)

    #Report robot position:
    if keyboard.is_pressed('r'):
        robotPrintLocation()

    #Set speed, movement sizes:
    if keyboard.is_pressed('m'):
        flush_input()
        stepMovSize = getIntInput("\nEnter robot movement step size(mm):\n")
        print("Movement Step Size is now "+str(stepMovSize)+"mm")
    if keyboard.is_pressed('f'):
        flush_input()
        speedRobot = getIntInput("\nEnter robot feedrate(mm/min):\n")
        print("Robot Feedrate is now "+str(speedRobot)+"mm/min")
    if keyboard.is_pressed('b'):
        flush_input()
        beltSpeed = getIntInput("\nEnter belt speed(mm/min):\n")
        print("Belt speed is now "+str(beltSpeed)+"mm/min")
    if keyboard.is_pressed('v'):
        flush_input()
        railStep = getIntInput("\nEnter Sliding Rail Step Size(mm):\n")
        print("Sliding Rail Step Size is now "+str(railStep)+"mm")
    
    #Exit Program:
    if keyboard.is_pressed('ESC'):
        sys.exit()

"""
Timing Function:
count =0;
        now_ns = time.time_ns() # Time in nanoseconds
        start_time = int(now_ns / 1000000) #Time in Milliseconds
        while True:
            keyboard.read_key()
            if keyboard.is_pressed('f'):
                count+=1
                if count ==100:
                    break;
        now_ns = time.time_ns() # Time in nanoseconds
        stopTime = int(now_ns / 1000000) #Time in Milliseconds
        print(stopTime-start_time)
"""