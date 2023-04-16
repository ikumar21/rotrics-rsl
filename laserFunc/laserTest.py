# from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
import laserGcode as lgs
'''windows'''
#laserDexarm = Dexarm(port="COM4")
#Simulate G code: https://nraynaud.github.io/webgcode/

def rectangleLaser(cArray,recWidth,recHeight, center):
    #Input center: (x_center,y_center)
    cArray.append([center[0]-recWidth/2.0,center[1]-recHeight/2.0, True])
    cArray.append([center[0]-recWidth/2.0,center[1]+recHeight/2.0, True])
    cArray.append([center[0]+recWidth/2.0,center[1]+recHeight/2.0, True])
    cArray.append([center[0]+recWidth/2.0,center[1]-recHeight/2.0, True])
    #Make sure to put False for last command to turn off laser:
    cArray.append([center[0]-recWidth/2.0,center[1]-recHeight/2.0, False])

def lineLaser(cArray,point1,point2):
    #Input point1: [x_1,y_1]
    #Input point2: [x_2,y_2]
    cArray.append([point1[0],point1[1], True])
    #Make sure to put False for last command to turn off laser/Add new laser commands
    cArray.append([point2[0],point2[1], False])


def rectangeFillLaser(cArray,recWidth,recHeight, center, stepY):
    #Input center: (x_center,y_center)
    yHeight = center[1]+recHeight/2.0;
    xStart = center[0]-recWidth/2.0;
    xStop = center[0]+recWidth/2.0
    startFirst = True

    while(yHeight>=center[1]-recHeight/2.0):
        cArray.append([xStart*startFirst+xStop*(not startFirst),yHeight, True])
        cArray.append([xStop*startFirst+xStart*(not startFirst),yHeight, False])
        startFirst=not startFirst;
        yHeight-=stepY;
    
    #Make sure to put False for last command to turn off laser:
    cArray[-1][2]=False

#gcode_message_creation("A1",specifiedLength=30,fixHeight=True,power=34,messageCenter=center)

if __name__ == "__main__":
    coorArray = []

    center = (10,10);
    rectangeFillLaser(coorArray,10,10,center,0.25)
    center = (0,20);
    #rectangeFillLaser(coorArray,10,10,center,0.5)
    

    # #Start of Wafer Board
    # center = (0,300);
    # rectangleLaser(coorArray,200,200,center)
    # for i in [1,2,3,4]:
    #     lineLaser(coorArray, [40*i-100,400],[40*i-100,200])
    #     lineLaser(coorArray, [-100,40*i+200],[100,40*i+200])
    # #End of Wafer Board

    lgs.gcode_point_creation(coorArray,255)