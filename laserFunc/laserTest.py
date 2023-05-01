#Simulate G code: https://nraynaud.github.io/webgcode/
import sys
 
# adding folder to the system path
sys.path.insert(0, '../')
from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
import laserGcode as lgs
import math

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
        self.center = [float(center[0]),float(center[1])];
        self.width = float(recWidth);
        self.height = float(recHeight);
        if stepSize is None:#Default-0.15 mm
            self.stepSize = 0.15;
        else:
            self.stepSize = float(stepSize);


class Triangle:#Equal Sides 
    def __init__(self,center,sideLength,stepSize, angle =None ):
        if angle is None:#Default-no Rotation(0); 0-120 degrees
            self.angle = 0.0;
        else:
             self.angle = float(angle)
        self.center = [float(center[0]),float(center[1])];
        self.length = float(sideLength);
        self.stepSize = float(stepSize);


def rectangleOutlineLaser(cArray, rec: Rectangle):
    #Input center: (x_center,y_center)
    newCoor=[];
    newCoor.append([rec.center[0]-rec.width/2.0,rec.center[1]-rec.height/2.0, True])
    newCoor.append([rec.center[0]-rec.width/2.0,rec.center[1]+rec.height/2.0, True])
    newCoor.append([rec.center[0]+rec.width/2.0,rec.center[1]+rec.height/2.0, True])
    newCoor.append([rec.center[0]+rec.width/2.0,rec.center[1]-rec.height/2.0, True])
    #Make sure to put False for last command to turn off laser:
    newCoor.append([rec.center[0]-rec.width/2.0,rec.center[1]-rec.height/2.0, False])

    rotate_coordinates(newCoor,rec.angle,rec.center)#rotate coordinates to angle
    for elem in newCoor: cArray.append(elem) #Add elements to laser array

def lineLaser(cArray,point1,point2):
    #Input point1: [x_1,y_1]
    #Input point2: [x_2,y_2]
    cArray.append([point1[0],point1[1], True])
    #Make sure to put False for last command to turn off laser/Add new laser commands
    cArray.append([point2[0],point2[1], False])


def rotate_coordinates(coordinates,angle,center):
    cosA = math.cos(math.pi*angle/180.0)*1.0
    sinA = math.sin(math.pi*angle/180.0)*1.0 
    xCenter = center[0]
    yCenter = center[1]

    for coordinate in coordinates:#Necessary to round! otherwise 2.3000e-16 means 2.3 mm
        xOld =  coordinate[0]-xCenter*1.0;
        yOld = coordinate[1]-yCenter*1.0;
        coordinate[0]= round(1.0*xOld*cosA+1.0*yOld*sinA+xCenter,2)
        coordinate[1]= round(1.0*yOld*cosA-1.0*xOld*sinA+yCenter,2)



def rectangleFillLaser(cArray:list,rect: Rectangle):
    #Input center: (x_center,y_center)

    yHeight = rect.center[1]+rect.height/2.0;#Start at top of rectangle
    xStart = rect.center[0]-rect.width/2.0;#Start at left of rectangle
    xStop = rect.center[0]+rect.width/2.0#End at right of rectangle
    
    #Alternate between starting at the left and right of rectangle after each pass, More efficient
    alternateVar = True
    newCoor = [];
    while(yHeight>=rect.center[1]-rect.height/2.0):#Stop at the bottom
        #Go to start of cut, and signal that next movement will be be laser cutting:
        newCoor.append([xStart*alternateVar+xStop*(not alternateVar),yHeight, True])

        #Go to end of cut(laser is on);  Turn off laser
        newCoor.append([xStop*alternateVar+xStart*(not alternateVar),yHeight, False])

        alternateVar=not alternateVar;#laser moved ends, so now start at the new end
        yHeight-=rect.stepSize;#Go down a step level
    
    rotate_coordinates(newCoor,rect.angle,rect.center)#rotate coordinates to angle
    for elem in newCoor: cArray.append(elem) #Add elements to laser array

    rectangleOutlineLaser(cArray,rect)#Outline to give sharp edges/corners

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

def triangleOutlineLaser(cArray, tri: Triangle):
    #Input center: (x_center,y_center)
    newCoor = [];
    
    #Start at right bottom
    xTri = tri.center[0]+tri.length/2;#Leftmost point of triangle
    yTri = tri.center[1]-tri.length/2.0/math.sqrt(3);#Bottom of triangle
    newCoor.append([xTri,yTri, True])
    
    #Go to Top Middle
    xTri-=tri.length/2
    yTri += tri.length*math.sqrt(3)/2;
    newCoor.append([xTri,yTri, True])

    #Go to bottom Left
    xTri-=tri.length/2
    yTri -= tri.length*math.sqrt(3)/2;
    newCoor.append([xTri,yTri, True])
    
    #Go to bottom Right
    xTri+=tri.length
    #Make sure to put False for last command to turn off laser:
    newCoor.append([xTri,yTri, False])

    rotate_coordinates(newCoor,tri.angle,tri.center)
    for elem in newCoor: cArray.append(elem)


def triangleFillLaser(cArray,tri: Triangle):
    #Input center: (x_center,y_center)

    xLocation = tri.center[0]-tri.length/2.0+tri.stepSize #Start at leftmost point of triangle
   
    yStart = tri.center[1]-tri.length/2.0/math.sqrt(3.0)

    
    #Alternate between starting at the top and bottom of triangle after each pass, More efficient
    alter = True
    newCoor = [];
    while(xLocation<=tri.center[0]+tri.length/2.0):#Stop at the bottom
        xRelative = xLocation-tri.center[0]+tri.length/2; 

        yStop = yStart + min(xRelative,tri.length-xRelative)*math.sqrt(3)
        #Go to start of cut, and signal that next movement will be be laser cutting:
        newCoor.append([xLocation,yStart*alter+yStop*(not alter), True])

        #(Laser is on) Go to end of cut; Then turn off laser
        newCoor.append([xLocation,yStop*alter+yStart*(not alter), False])

        alter=not alter;#laser moved ends, so now start at the new end
        xLocation+=tri.stepSize;#Go right a step level
    
    rotate_coordinates(newCoor,tri.angle,tri.center)
    for elem in newCoor: cArray.append(elem)
    triangleOutlineLaser(cArray, tri)#Outline triangle for sharp edges

    #Make sure to put False for last command to turn off laser:
    cArray[-1][2]=False

def arrangement1(coorArray,waferBoard:Wafer_Board):

    #Create board:
    createSquareWaferBoard(coorArray, waferBoard);

    #Get all centers of each square in board:
    squareCenters = centerSquares(waferBoard);#
    
    #Entries in Wafer

    rectangleFillLaser(coorArray,Rectangle(squareCenters[0][0],10,10,0.4,45))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[0][2],10,10,0.3,30))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[1][1],7,10,0.3))
    rectangleOutlineLaser(coorArray,Rectangle(squareCenters[1][3],5,10,None))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[2][0],5,10,0.25,15))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[2][2],5,5,0.25))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][0],10,5,0.25))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][1],10,3,0.25))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][2],6,3,0.1))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][3],2,5,0.15))




def arrangement2(coorArray,waferBoard:Wafer_Board):

    #Create board:
    createSquareWaferBoard(coorArray, waferBoard);

    #Get all centers of each square in board:
    squareCenters = centerSquares(waferBoard);#
    
    #Entries in Wafer


    triangleFillLaser(coorArray,Triangle(squareCenters[0][0],10,0.2,30))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[0][2],8,8,0.2,45))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[0][4],8,5,0.2,30))

    triangleFillLaser(coorArray,Triangle(squareCenters[1][1],8,0.2,0))
    triangleFillLaser(coorArray,Triangle(squareCenters[1][3],7,0.2,0))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[1][5],5,5,0.2,30))
    
    triangleFillLaser(coorArray,Triangle(squareCenters[2][0],10,0.2,30))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[2][2],8,8,0.2,10))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[2][4],6,6,0.2,60))
    
    rectangleFillLaser(coorArray,Rectangle(squareCenters[3][0],9,7,0.25))

    rectangleFillLaser(coorArray,Rectangle(squareCenters[4][1],10,3,0.2))
    rectangleFillLaser(coorArray,Rectangle(squareCenters[4][2],6,3,0.2))
    
    rectangleFillLaser(coorArray,Rectangle(squareCenters[5][3],2,5,0.2))
    triangleFillLaser(coorArray,Triangle(squareCenters[5][0],5,0.2,0))




if __name__ == "__main__":
    coordinateArray = []
    waferBoard1 = Wafer_Board((0,300),80,4)
    waferBoard2 = Wafer_Board((0,300),75,6)


    #arrangement1(coordinateArray, waferBoard1);
    arrangement2(coordinateArray, waferBoard2);


    
    lgs.gcode_point_creation(coordinateArray,200)#Create gcode with power level 200;
    runLaser();


