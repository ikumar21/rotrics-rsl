from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
'''windows'''
#laserDexarm = Dexarm(port="COM4")


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
    #Get all movement x, y positions:
    xPos = [float(line[4:line.index(' ', 3)]) for line in lines if line[0]=='G' and line[3]=='X']
    yPos = [float(line[line.index('Y')+1:]) for line in lines if line[0]=='G' and line[3]=='X']
    if(fixHeight==True):#Scales according to height or width
        scalar = float(specifiedLength)/(max(yPos)-min(yPos))
    else:
        scalar=float(specifiedLength)/(max(xPos)-min(xPos))
    lineIndex =0;
    for linePos in range(len(lines)):#changes Gcode to scale size
        line = lines[linePos]
        if(line[0]=='G' and (line[1]=='1' or line[1]=='0') and line[3]=='X'):
            lines[linePos] = line[0:4] + str(round(scalar*xPos[lineIndex],2))+" Y"+str(round(scalar*yPos[lineIndex],2))+'\n'     
            lineIndex+=1
    with open("outputGcode.txt", "w") as f:#Write to file
        f.writelines(lines)
    f.close()

if __name__ == "__main__":
    gcode_creation("BCA",115,True,34)
    # laserDexarm.go_home()
    # laserDexarm._send_cmd("G92.1\r\n")
    # laserDexarm.set_workorigin()
    # time.sleep(3)
    # with open("outputGcode.txt") as f:#Send gcode of the letters:
    #     lines = f.readlines()
    # for x in lines:
    #     a = x+"\r\n"
    #     laserDexarm._send_cmd(a);
