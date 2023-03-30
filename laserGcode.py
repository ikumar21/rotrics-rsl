from pydexarm import Dexarm
import time
import math 
from ttgLib.TextToGcode import ttg
import threading
'''windows'''
laserDexarm = Dexarm(port="COM4")


def gcode_creation():
    ttg("1234",2,0,"File",400).toGcode("M3 S255","M5","G1","G1")
    #Changes Gcode to work for the dexarm
    with open("output.gcode") as f:
        lines = f.readlines()
    f.close()
    lines[0]="G0 Z0\n"
    lines[1]="M2000\n"
    lines[2]="M888 P1\nM888 P14 \nM5\n"
    lines[3]="G0 F400\nG1 F400 \n"
    a = "G0"
    a+=lines[4];
    lines[4]=a
    with open("outputGcode.txt", "w") as f:
        f.writelines(lines)
    f.close()

if __name__ == "__main__":
    gcode_creation()
    laserDexarm.go_home()
    laserDexarm._send_cmd("G92.1\r\n")
    laserDexarm.set_workorigin()
    time.sleep(3)
    with open("outputGcode.txt") as f:#Send gcode of the letters:
        lines = f.readlines()
    for x in lines:
        a = x+"\r\n"
        laserDexarm._send_cmd(a);


