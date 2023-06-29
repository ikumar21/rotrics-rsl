# from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
import serial

'''windows'''
#laserDexarm = Dexarm(port="COM4")
#Simulate G code: https://nraynaud.github.io/webgcode/
#Create SVg from image: https://picsvg.com


class Laser_Object_Properties():
    def __init__(self, fixHeight:bool = True,centerPoint = [0,300], specifiedLength = 50,laserPower:int =175, angle=0):
        #If true, laser object's height will be equal to specified length
        #Otherwise, laser object's width will be equal to specified length
        self.fixHeight = fixHeight 
        self.centerPoint = centerPoint #x,y position of center of object
        self.specifiedLength = specifiedLength;
        self.laserPower = laserPower;
        self.angle = angle;
        self.laseringFeedrate = 800;
        self.movingFeedrate = 800;

def editHeaderAddNewLines(lines):
    #Adds in new lines
    for linePos in range(len(lines)):
        lines[linePos] = lines[linePos]+'\n'
    #Changes Gcode Header to work for the dexarm
    lines[0]="G0 Z0\n"
    lines[1]="M2000\n"
    lines[2]="M888 P1\nM888 P14 \nM5\n"#M5 turns off Laser
    lines[3]="G0 F800\nG1 F800 \n"


def GcodeObjectCreation(fileName,objectProperties: Laser_Object_Properties):
    #First argument - File of G-Code 
    #Second Argument - Desired properties of Object 
    #Output: G-Code in outputGcode.txt and returns tuple -> width, height
    
    #Get lines from G-code:
    with open(fileName, "r") as f: objectLines = f.readlines()
    
    #Set laser object center, angle, height/width, laser power:
    # dog_laser = Laser_Object_Properties(fixHeight=True,centerPoint=[0,340-25],specifiedLength=50,laserPower=125,angle=0)
    
    #Get the modifed G-code with right properties
    laserLines,width, height = ModifyGcode(objectLines, objectProperties);

    #Write to file
    with open("outputGcode.txt", "w") as f:
        f.writelines(laserLines)
    f.close()
    
    return width, height

def gcode_message_creation(message,specifiedLength,fixHeight,power, messageCenter):
    #First argument - Message to Write - String
    #Second Argument - length desired (mm) 
    #Third argument - True - height should be set to the specified length, False- width should be set
    #4th Argument - power desired (0-255), default = 100 
    #5th Argument - center of object to be written (x,y)

    #Output: Gcode of lasering message in file called outputGcode.txt


    # M5 turns off laser, M3 S100 turns on laser with power lvl 100/255
    lines = ttg(message,2,0,"Return",400).toGcode("M3 S"+str(power),"M5","G1","G0")
    editHeaderAddNewLines(lines)#Fix up Header and add "\n"

    #Get all movement x, y positions:
    xPos = [float(line[4:line.index(' ', 3)]) for line in lines if line[0]=='G' and line[3]=='X']
    yPos = [float(line[line.index('Y')+1:]) for line in lines if line[0]=='G' and line[3]=='X']

    #Scales according to height or width
    if(fixHeight==True):
        scalar = float(specifiedLength)/(max(yPos)-min(yPos))
    else:
        scalar=float(specifiedLength)/(max(xPos)-min(xPos))
    
    xPos = [elem*scalar for elem in xPos]
    yPos = [elem*scalar for elem in yPos];

    #Shift message to desired centerpoint
    xShift = messageCenter[0]-(max(xPos)+min(xPos))/2.0
    yShift = messageCenter[1]-(max(yPos)+min(yPos))/2.0
    xPos = [elem+xShift for elem in xPos];
    yPos = [elem+yShift for elem in yPos];

    #Start at right place
    lines[3]+="G0 X"+str(round(xPos[0],2))+" Y"+str(round(yPos[0],2))+"\n"

    #Changes the Gcode x,y to scale/move, round to 2 decimal points (mm)
    lineIndex =0;

    for linePos in range(len(lines)):
        line = lines[linePos]
        if(line[0:2] == "M5"):#Laser should turn off:
            laserCommand = False
        elif(line[0:2]=="M3"):#Laser should be on
            laserCommand = True
        if(line[0]=='G' and (line[1]=='1' or line[1]=='0') and line[3]=='X'):
            xPosString = str(round(xPos[lineIndex],2))
            yPosString = str(round(yPos[lineIndex],2))
            lines[linePos] = "G"+str(int(laserCommand))+" X" + xPosString+" Y"+yPosString+'\n'     
            lineIndex+=1

    #Write to file
    with open("outputGcode.txt", "w") as f:
        f.writelines(lines)
    f.close()

    #Return width, height:
    return round(max(xPos)-min(xPos),2), round(max(yPos)-min(yPos),2)


def gcode_point_creation(coorArray,power):
    #Ouput: gcode of lasering lines between points-> outputGcode.txt

    #Input coorArray: array of arrays [x,y, LaserOn]
    #LaserOn - should laser be on when going to next point

    #Ex: [[0,0,True],[0,20,False], [10,20,True], [10,0,False/True]]
    #Will create two vertical lines at x = 0 and 10 with height of 20.

    power = int(power) if (int(power) <256 and int(power)>0) else 100
    laserOnCommand = "M3 S"+str(power)+"\n"

    coorArray[-1][2]=False;#Turn off Laser at last coordinate

    lines = [" "," "," "," "]
    editHeaderAddNewLines(lines)#Add header 
    
    
    prevLaserCommand = False;#Start with laser off
    for coordinate in coorArray:
        posCommand = "G"+str(int(prevLaserCommand))+ " X"+str(coordinate[0])+ " Y"+str(coordinate[1])+"\n"
        lines.append(posCommand)#Go To coordinate
        if(coordinate[2]!= prevLaserCommand):#Turn on/off laser if it isn't already
            laserCommand = laserOnCommand if coordinate[2] else "M5\n"
            lines.append(laserCommand)
            prevLaserCommand=coordinate[2]; 
    #for lines 
    with open("outputGcode.txt", "w") as f:
        f.writelines(lines)
    f.close()



def ModifyGcode(lines, obj_prop:Laser_Object_Properties):
    #Returns lines, width, and height
    
    #Get all movement x, y positions:
    xPos = [float(line[4:line.index(' ', 3)]) for line in lines if line[0]=='G' and line[3]=='X']
    yPos = [float(line[line.index('Y')+1:]) for line in lines if line[0]=='G' and line[3]=='X']

    #Scales according to height or width
    if(obj_prop.fixHeight==True):
        scalar = float(obj_prop.specifiedLength)/(max(yPos)-min(yPos))
    else:
        scalar=float(obj_prop.specifiedLength)/(max(xPos)-min(xPos))
    
    xPos = [elem*scalar for elem in xPos]
    yPos = [elem*scalar for elem in yPos]

    #Shift Object to desired centerpoint
    xShift = obj_prop.centerPoint[0]-(max(xPos)+min(xPos))/2.0
    yShift = obj_prop.centerPoint[1]-(max(yPos)+min(yPos))/2.0
    xPos = [elem+xShift for elem in xPos];
    yPos = [elem+yShift for elem in yPos];

    #Rotates Object
    cosA = math.cos(math.pi*obj_prop.angle/180.0)*1.0
    sinA = math.sin(math.pi*obj_prop.angle/180.0)*1.0 
    xCenter = obj_prop.centerPoint[0]
    yCenter = obj_prop.centerPoint[1]
    for index in range(len(xPos)):
        xOld = xPos[index]-xCenter*1.0;
        yOld = yPos[index]-yCenter*1.0;
        xPos[index]= 1.0*xOld*cosA+1.0*yOld*sinA+xCenter
        yPos[index]= 1.0*yOld*cosA-1.0*xOld*sinA+yCenter

    #Changes the Gcode x,y to scale/move, round to 2 decimal points (mm)
    lineIndex =0;
    laserCommand = False;#Start with laser on
    for linePos in range(len(lines)):
        line = lines[linePos]
        if(line[0:2] == "M5"):#Laser should turn off:
            laserCommand = False
        elif(line[0:2]=="M3"):#Laser should be on
            laserCommand = True
        if(line[0]=='G' and (line[1]=='1' or line[1]=='0') and line[3]=='X'):
            xPosString = str(round(xPos[lineIndex],2))
            yPosString = str(round(yPos[lineIndex],2))
            lines[linePos] = "G"+str(int(laserCommand))+" X" + xPosString+" Y"+yPosString+'\n'     
            lineIndex+=1

    
    return lines, round(max(xPos)-min(xPos),2), round(max(yPos)-min(yPos),2);


def runLaser(lasDexarm):
    
    #Initializes Robot
    lasDexarm.go_home()
    
    #Resets coordinate to dexarm factory setting, home is (0,300)
    lasDexarm._send_cmd("G92.1\r\n")

    #Read the gcode:
    with open("outputGcode.txt") as f:
        lines = f.readlines()

    #Send Laser gcode:
    for x in lines:
        #Don't send if it's a comment
        if(x[0]!=";"):
            a = x+"\r\n"
            lasDexarm._send_cmd(a);

def initializeArduino():
    global laserArduinoSerial
    laserArduinoSerial = serial.Serial("COM7", 115200, timeout=0.2)
def LaserDoorClose():
    message = "$C\n"
    laserArduinoSerial.write((bytes(message, 'utf-8')))

    #Wait until door is opened:
    while True:
        messageIncoming = laserArduinoSerial.readline()
        if(len(messageIncoming)>0):
            if(chr(messageIncoming[1])=='D'):
                break;
def LaserDoorOpen():
    message = "$O\n"
    laserArduinoSerial.write((bytes(message, 'utf-8')))
    #Wait until door is opened:
    while True:
        messageIncoming = laserArduinoSerial.readline()
        if(len(messageIncoming)>0):
            print(messageIncoming)
            if(chr(messageIncoming[1])=='D'):
                break;







