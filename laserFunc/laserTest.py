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

#Before calling any laser functions, make sure the laser is off already

class Wafer_Board:
    def __init__(self,center,waferSideLength,numberColumnsRows):
        self.numberColumnsRows=numberColumnsRows;
        self.individualSquareLength=1.0*waferSideLength/numberColumnsRows;
        self.center=center;
        self.waferSideLength=waferSideLength;

class Rectangle:
    def __init__(self,center,recWidth,recHeight,stepSize, angle =None ):
        if angle is None:#Default-no Rotation(0); 0-180 degrees
            self.angle = 0;
        else:
             self.angle = angle
        self.center = center;
        self.width = recWidth;
        self.height = recHeight;
        self.stepSize = stepSize;





def rectangleOutlineLaser(cArray, rec: Rectangle):
    #Input center: (x_center,y_center)
    
    cArray.append([rec.center[0]-rec.width/2.0,rec.center[1]-rec.height/2.0, True])
    cArray.append([rec.center[0]-rec.width/2.0,rec.center[1]+rec.height/2.0, True])
    cArray.append([rec.center[0]+rec.width/2.0,rec.center[1]+rec.height/2.0, True])
    cArray.append([rec.center[0]+rec.width/2.0,rec.center[1]-rec.height/2.0, True])
    #Make sure to put False for last command to turn off laser:
    cArray.append([rec.center[0]-rec.width/2.0,rec.center[1]-rec.height/2.0, False])

def lineLaser(cArray,point1,point2):
    #Input point1: [x_1,y_1]
    #Input point2: [x_2,y_2]
    cArray.append([point1[0],point1[1], True])
    #Make sure to put False for last command to turn off laser/Add new laser commands
    cArray.append([point2[0],point2[1], False])


def rectangleFillLaser(cArray,rect: Rectangle):
    #Input center: (x_center,y_center)

    yHeight = rect.center[1]+rect.height/2.0;#Start at top of rectangle
    xStart = rect.center[0]-rect.width/2.0;#Start at left of rectangle
    xStop = rect.center[0]+rect.width/2.0#End at right of rectangle
    
    #Alternate between starting at the left and right of rectangle after each pass, More efficient
    alternateVar = True

    while(yHeight>=rect.center[1]-rect.height/2.0):#Stop at the bottom
        #Go to start of cut, and signal that next movement will be be laser cutting:
        cArray.append([xStart*alternateVar+xStop*(not alternateVar),yHeight, True])

        #Go to end of cut(laser is on);  Turn off laser
        cArray.append([xStop*alternateVar+xStart*(not alternateVar),yHeight, False])

        alternateVar=not alternateVar;#laser moved ends, so now start at the new end
        yHeight-=rect.stepSize;#Go down a step level 
    
    #Make sure to put False for last command to turn off laser:
    cArray[-1][2]=False


#gcode_message_creation("A1",specifiedLength=30,fixHeight=True,power=34,messageCenter=center)


def runLaser():
    laserDexarm = Dexarm(port="COM4")#Open communication with dexarm
    laserDexarm.go_home()#Initializes Robot

    laserDexarm._send_cmd("G92.1\r\n")#Resets coordinate to dexarm factory setting, home is (0,300)

    with open("outputGcode.txt") as f:
        lines = f.readlines()
    for x in lines:#Send gcode of the letters:
        a = x+"\r\n"
        laserDexarm._send_cmd(a);


def centerSquares(waferBoard: Wafer_Board):
    #Inputs: Center of Board [x,y]; length of one box; number of boxes per row;
    #Output: array of arrays of centers of each box; 
    # -> squareCenter[0][3] = Center of box in 1st row and 4th column 
    squareCenters =[];
    numColumns = waferBoard.numberColumnsRows;
    individualSquareLength = waferBoard.individualSquareLength;

    yCenter = waferBoard.center[1]+(numColumns-1)*individualSquareLength/2#Highest row: Y position 

    for row in range(numColumns):#Go through each row
        rowCenters =[];
        
        #Leftmost Column: x position
        xCenter = waferBoard.center[0]-(numColumns-1)*individualSquareLength/2

        for column in range(numColumns):#Go through each column
            rowCenters.append([xCenter,yCenter]);
            
            #Go to the next box on the right
            xCenter+= individualSquareLength;
        
        squareCenters.append(rowCenters);
        
        #Go Down a row
        yCenter-=individualSquareLength;
    return squareCenters;


def createSquareWaferBoard(coorArray,wafB: Wafer_Board):
    #Create square box
    outerBox = Rectangle(wafB.center,wafB.waferSideLength,wafB.waferSideLength,None)
    rectangleOutlineLaser(coorArray,outerBox)
    for i in range(1,wafB.numberColumnsRows):
        #Line 1 Vertical
        x1 = wafB.individualSquareLength*i-wafB.waferSideLength/2;#Constant x
        yStart1 = wafB.center[1]+wafB.waferSideLength/2#Start at Top
        yStop1 = wafB.center[1]-wafB.waferSideLength/2#End at Bottom
        
        #Line 2 Horizontal
        y2 = wafB.individualSquareLength*i+wafB.center[1]-wafB.waferSideLength/2;#Constant y
        xStart2 = wafB.center[0]-wafB.waferSideLength/2
        xStop2 = wafB.center[0]+wafB.waferSideLength/2
        
        lineLaser(coorArray, [x1,yStart1],[x1,yStop1])
        lineLaser(coorArray, [xStart2,y2],[xStop2,y2])
    #End of Wafer Board





def arrangement1(coorArray,waferBoard:Wafer_Board):

    #Create board:
    createSquareWaferBoard(coorArray, waferBoard);

    #Get all centers of each square in board:
    squareCenters = centerSquares(waferBoard,);#
    
    #Entries in Wafer

    rectangleFillLaser(coorArray,Rectangle(squareCenters[0][0],10,10,0.4))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[0][2],10,10,0.3))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[1][1],7,10,0.3))
    rectangleOutlineLaser(coorArray,Rectangle(squareCenters[1][3],5,10,None))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[2][0],5,10,0.25))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[2][2],5,5,0.25))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][0],10,5,0.25))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][1],10,3,0.25))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][2],6,3,0.1))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][3],2,5,0.15))




if __name__ == "__main__":
    coordinateArray = []
    waferBoard1 = Wafer_Board((0,300),80,4)


    arrangement1(coordinateArray, waferBoard1);

    lgs.gcode_point_creation(coordinateArray,200)#Create gcode with power level 200;
    #runLaser();


