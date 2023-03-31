from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
'''windows'''
#laserDexarm = Dexarm(port="COM4")

def getXY(stringXY,xArray,yArray):
    startIndexX = stringXY.index('X')+1;
    stopIndexX = stringXY.index(' ', 3)
    startIndexY = stringXY.index('Y')+1;
    xArray.append(float(stringXY[startIndexX:stopIndexX]))
    yArray.append(float(stringXY[startIndexY:]))
    return float(stringXY[startIndexX:stopIndexX]),float(stringXY[startIndexY:]);


def editHeaderAddNewLines(lines):
    #Adds in new lines
    for linePos in range(len(lines)):
        lines[linePos] = lines[linePos]+'\n'
    #Changes Gcode Header to work for the dexarm
    lines[0]="G0 Z0\n"
    lines[1]="M2000\n"
    lines[2]="M888 P1\nM888 P14 \nM5\n"
    lines[3]="G0 F400\nG1 F400 \nG0 X0 Y0\n"

def gcode_creation(message,specifiedLength,fixHeight,power):
    #First argument - Message to Write
    #Second Argument - length desired (mm) 
    #Third argument - True - height should be set to the length, False- width should be set
    #4th Argument - power desired (0-255), default = 100 
    power = int(power) if (int(power) <256 and int(power)>0) else 100
    lines = ttg(message,2,0,"Return",400).toGcode("M3 S"+str(power),"M5","G1","G1")#Generate Laser Gcode
    editHeaderAddNewLines(lines)
    xPos, yPos = [],[]
    for line in lines:#Inserts all x/y position into arrays
        if(line[0]=='G' and (line[1]=='1' or line[1]=='0') and line[3]=='X'):
            getXY(line,xPos,yPos)

    if(fixHeight==True):#Scales according to height or width
        scalar = float(specifiedLength)/(max(yPos)-min(yPos))
    else:
        scalar=float(specifiedLength)/(max(xPos)-min(xPos))
    for linePos in range(len(lines)):
        line = lines[linePos]
        if(line[0]=='G' and (line[1]=='1' or line[1]=='0') and line[3]=='X'):
            x, y = getXY(line,xPos,yPos)
            lines[linePos] = line[0:4] + str(round(scalar*x,2))+" Y"+str(round(scalar*y,2))+'\n'     

    with open("outputGcode.txt", "w") as f:#Write to file
        f.writelines(lines)
    f.close()

if __name__ == "__main__":
    gcode_creation("ABC",10.2,True,-32)
    # laserDexarm.go_home()
    # laserDexarm._send_cmd("G92.1\r\n")
    # laserDexarm.set_workorigin()
    # time.sleep(3)
    # with open("outputGcode.txt") as f:#Send gcode of the letters:
    #     lines = f.readlines()
    # for x in lines:
    #     a = x+"\r\n"
    #     laserDexarm._send_cmd(a);
