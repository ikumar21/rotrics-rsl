import sys
# adding folder to the system path
sys.path.insert(0, '../')
import time
from pydexarm import Dexarm




#Go to Rotrics Studio and check port name of dexarm
#Windows: 
dexarm1 = Dexarm(port="COM6")#Open communication with dexarm
#Macbook/Linux: dexarm = Dexarm(port="/dev/tty.usbmodem2069397847531")

#First Initialize Dexarm:
#Factory Settings: Home -> (0,300,0)
dexarm1.go_home()#Goes to robot home position


robotConnectedConveyor = True;
robotConnectedRail = False;

#Command to move dexarm (mm): x = 50; y = 250; z = 10; 
#Feedrate is speed of robot movement(mm/min): Maximum is 30,000 mm/min
#Default is 2000 mm/min if no value
#Default of wait is True -> code will busy wait or "stop" until robot finishes movement
dexarm1.move_to(50,250,10,feedrate=4000,wait=True)


#To Move Relatively:

#Current Robot Position is now (0,0,0,0):
dexarm1._send_cmd("G92 X0 Y0 Z0 E0\r"); #Resets position

#Now you can move relatively: (Moves 50 mm to the postive x and down 10 mm)
dexarm1.move_to(50,None,-10,feedrate=4000,wait=True)

dexarm1._send_cmd("G92.1\r");#Resets back to factory coordinate system: home is (0,300,0)




if(robotConnectedConveyor):
    #Move conveyor forward at speed of 1000 mm/min: Max speed is 7200 mm/min-> 600 mm/sec
    dexarm1.conveyor_belt_forward(1000)
    time.sleep(5)#Move for at least one second

    #Stop Conveyor
    dexarm1.conveyor_belt_stop()

    #Move conveyor backwards at speed of 2000 mm/min
    dexarm1.conveyor_belt_backward(2000)
    time.sleep(2)#Move for at least 500 milliseconds

    #Stop Conveyor
    dexarm1.conveyor_belt_stop()
    time.sleep(5)

    #Move Conveyor Belt Certain Position (Busy Wait):
    #Positive position-> moves forward, negative-> moves to the backwards
    #Inputs: position(mm), speed (mm/min)

    dexarm1.conveyor_belt_move(position=400,speed=2000)


if(robotConnectedRail):
    #Need to initilize first:
    #Make sure it starts in the middle, then it will go to one end of the rail
    dexarm1.sliding_rail_init()

    #Moves to position 300 mm at a speed of 4000 mm/min;
    #Movement Range :0-1000 mm; max speed -> 15,000 mm/min 
    dexarm1.move_to(None,None,None,300,feedrate=4000,wait=True)

    #To Move Relatively for Rail:

    #Current Robot Position is now (~,~,~,0):
    dexarm1._send_cmd("G92 E0\r"); #Resets position

    #Now you can move relatively: (Moves 50 mm to the postive x)
    dexarm1.move_to(None,None,None,50,feedrate=4000,wait=True)
    dexarm1._send_cmd("G92.1\r");#Resets back to factory coordinate system


    




