# from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
'''windows'''
#laserDexarm = Dexarm(port="COM4")
#Simulate G code: https://nraynaud.github.io/webgcode/
class LaserCutterPrp:
    a = 0;


def editHeaderAddNewLines(lines):
    #Adds in new lines
    for linePos in range(len(lines)):
        lines[linePos] = lines[linePos]+'\n'
    #Changes Gcode Header to work for the dexarm
    lines[0]="G0 Z0\n"
    lines[1]="M2000\n"
    lines[2]="M888 P1\nM888 P14 \nM5\n"#M5 turns off Laser
    lines[3]="G0 F800\nG1 F800 \n"


def gcode_message_creation(message,specifiedLength,fixHeight,power, messageCenter):
    #First argument - Message to Write
    #Second Argument - length desired (mm) 
    #Third argument - True - height should be set to the specified length, False- width should be set
    #4th Argument - power desired (0-255), default = 100 
    #5th Argument - center of object to be written (x,y)

    #Find power of laser cutter
    power = int(power) if (int(power) <256 and int(power)>0) else 100

    #Generate Laser Gcode using library
    # M5 turns off laser, M3 S100 turns on laser with power lvl 100/255
    lines = ttg(message,2,0,"Return",400).toGcode("M3 S"+str(power),"M5","G1","G1")
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
    lines[3]+="G1 X"+str(round(xPos[0],2))+" Y"+str(round(yPos[0],2))+"\n"

    #Changes the Gcode x,y to scale/move, round to 2 decimal points (mm)
    lineIndex =0;
    for linePos in range(len(lines)):
        line = lines[linePos]
        if(line[0]=='G' and (line[1]=='1' or line[1]=='0') and line[3]=='X'):
            xPosString = str(round(xPos[lineIndex],2))
            yPosString = str(round(yPos[lineIndex],2))
            lines[linePos] = line[0:4] + xPosString+" Y"+yPosString+'\n'     
            lineIndex+=1

    #Write to file
    with open("outputGcode.txt", "w") as f:
        f.writelines(lines)
    f.close()


def gcode_point_creation(coorArray,power):
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

if __name__ == "__main__":
    center = (20,30);
    #gcode_message_creation("A1",specifiedLength=30,fixHeight=True,power=34,messageCenter=center)
    cArray = [[0,0,True],[20,20,True], [40,0,True], [0,0,False/True]]
    gcode_point_creation(cArray,255)
    # laserDexarm.go_home()
    # laserDexarm._send_cmd("G92.1\r\n")
    # #laserDexarm.set_workorigin() 
    # time.sleep(3)
    # with open("outputGcode.txt") as f:#Send gcode of the letters:
    #     lines = f.readlines()
    # for x in lines:
    #     a = x+"\r\n"
    #     laserDexarm._send_cmd(a);

"""
G0 X-11.50 Y-11.50
M3 S127
G1 X11.50 Y-11.50
M5
"""
