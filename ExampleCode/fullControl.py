"""
Script to move the robot arm freely and/or the sliding rail/conveyor belt
Purpose: See the Robot position in certain locations

Commands:
r->Print robot location
m-> Change movement increment
v-> Change Robot Speed 
b-> Change belt speed

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
# adding folder to the system path
sys.path.insert(0, '../')
import time
from pydexarm import Dexarm
import keyboard
import threading
import sys
#Open communication with dexarm
#Windows: 
#dexarm1 = Dexarm(port="COM6")


#Change depending on what arm is connected to
robotConnectedConveyor = False;
robotConnectedRail = False;


stepIncrement= 20#mm


#First Initialize Dexarm:
#Factory Settings: Home -> (0,300,0)
#dexarm1.go_home()#Goes to robot home position

def robotLeft():
    global stepIncrement
    while True:
        keyboard.wait("a")
        print("\n\nLeft"+str(stepIncrement)+"\n\n")

def robotRight():
    global stepIncrement
    while True:
        keyboard.wait("d")
        print("\n\nRight"+str(stepIncrement)+"\n\n")

def robotAway():
    global stepIncrement
    while True:
        keyboard.wait("s")
        print("\n\nAway"+str(stepIncrement)+"\n\n")

def robotTowards():
    global stepIncrement
    while True:
        keyboard.wait("w")
        print("\n\nTowards"+str(stepIncrement)+"\n\n")

def robotUp():
    global stepIncrement
    while True:
        keyboard.wait("up arrow")
        print("\n\nUp"+str(stepIncrement)+"\n\n")

def robotDown():
    global stepIncrement
    while True:
        keyboard.wait("down arrow")
        print("\n\nDown"+str(stepIncrement)+"\n\n")

def quitProg():
    keyboard.wait("esc")
    print("Exiting Program")
    sys.exit(0)


if __name__ =="__main__":
	# creating thread
    functionsMovement = [robotLeft, robotRight,robotAway,robotTowards,robotUp,robotDown];
    threadsMov = [threading.Thread(target=func, args=()) for func in functionsMovement]
    threadQuit = threading.Thread(target=quitProg, args=());
    # threadLeftMov = threading.Thread(target=robotLeft, args=())
    # threadRightMov = threading.Thread(target=robotRight, args=())
    # threadAwayMov = threading.Thread(target=robotAway, args=())
    # threadTowardsMov = threading.Thread(target=robotTowards, args=())   
    # threadUpMov = threading.Thread(target=robotUp, args=())
    # threadDownMov = threading.Thread(target=robotDown, args=())
    

	# starting all threads
    for thread in threadsMov: thread.setDaemon(True)
    for thread in threadsMov: thread.start()
    threadQuit.start()

    # for thread in threadsMov:
    #     thread.join()
	# both threads completely executed
    print("DONE")
