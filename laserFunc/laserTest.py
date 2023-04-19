#Simulate G code: https://nraynaud.github.io/webgcode/
import sys
 
# adding Folder_2 to the system path
sys.path.insert(0, '../')
from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
import laserGcode as lgs



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
    print(yHeight)
    startFirst = True

    while(yHeight>=center[1]-recHeight/2.0):
        cArray.append([xStart*startFirst+xStop*(not startFirst),yHeight, True])
        cArray.append([xStop*startFirst+xStart*(not startFirst),yHeight, False])
        startFirst=not startFirst;
        yHeight-=stepY;
    
    #Make sure to put False for last command to turn off laser:
    cArray[-1][2]=False
    print(xStop-xStart,yHeight)

#gcode_message_creation("A1",specifiedLength=30,fixHeight=True,power=34,messageCenter=center)


def runLaser():
    laserDexarm = Dexarm(port="COM4")
    laserDexarm.go_home()
    laserDexarm._send_cmd("G92.1\r\n")
    with open("outputGcode.txt") as f:#Send gcode of the letters:
        lines = f.readlines()
    for x in lines:
        a = x+"\r\n"
        laserDexarm._send_cmd(a);


def centerSquares(center,individualSquareLength,numColumns):
    squareCenters =[];
    yCenter = center[1]+(numColumns-1)*individualSquareLength/2

    
    for row in range(numColumns):
        rowCenters =[];
        xCenter = center[0]-(numColumns-1)*individualSquareLength/2
        for column in range(numColumns):
            rowCenters.append([xCenter,yCenter]);
            xCenter+= individualSquareLength;
        squareCenters.append(rowCenters);
        yCenter-=individualSquareLength;
    return squareCenters;



if __name__ == "__main__":
    coorArray = []
    # center = (10,10);
    # rectangeFillLaser(coorArray,10,10,center,0.25)
    # center = (0,20);
    # #rectangeFillLaser(coorArray,10,10,center,0.5)
    

    #Start of Wafer Board
    center = (0,300);
    squareLength = 80;
    numColumnsRows = 4;
    rectangleLaser(coorArray,squareLength,squareLength,center)
    individualSquareLength = squareLength/numColumnsRows;
    for i in range(1,numColumnsRows):
        lineLaser(coorArray, [individualSquareLength*i-squareLength/2,center[1]+squareLength/2],[individualSquareLength*i-squareLength/2,300-squareLength/2])
        lineLaser(coorArray, [-squareLength/2,individualSquareLength*i+center[1]-squareLength/2],[squareLength/2,individualSquareLength*i+center[1]-squareLength/2])
    #End of Wafer Board

    

    #Random Square Fill:
    squareCenters = centerSquares(center,individualSquareLength,numColumnsRows);

    rectangeFillLaser(coorArray,10,10,squareCenters[0][0],0.5)
    rectangeFillLaser(coorArray,10,10,squareCenters[0][2],0.25)
    rectangeFillLaser(coorArray,15,15,squareCenters[1][1],1)
    rectangeFillLaser(coorArray,10,10,squareCenters[1][3],0.1)
    rectangeFillLaser(coorArray,5,5,squareCenters[3][0],0.05)
    rectangeFillLaser(coorArray,10,10,squareCenters[3][1],0.2)


    lgs.gcode_point_creation(coorArray,200)
    runLaser();


