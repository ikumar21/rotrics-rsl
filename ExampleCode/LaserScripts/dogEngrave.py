#Add Laser Module:
import sys
sys.path.insert(0, 'LaserModule')
import laser_module as l_m

#Import Movement Module:
sys.path.insert(0, 'MovementModule')
from pydexarm import Dexarm

import time


def EngraveActualDog(laserRobot):

    #File Name:
    fileLocName = "LaserModule/rotricsGcode/dog.gcode";
    
    #Set laser object center, angle, height/width, laser power:
    dog_laser = l_m.Laser_Object_Properties(fixHeight=True,centerPoint=[0,305],specifiedLength=10,laserPower=125,angle=0)
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,dog_laser)

    #Run the Laser
    l_m.runLaser(laserRobot)



def EngraveLettersDog(laserRobot):
    #Generate G-Code:
    width, height = l_m.gcode_message_creation("DOG",15,False,125,(0,296))
    
    #Run laser:
    l_m.runLaser(laserRobot)
    return width, height;

def EngraveUnderLine(laserRobot, width, height):

    #File Name:
    fileLocName = "LaserModule/rotricsGcode/HorizontalLine.gcode";
    
    #Set laser object center, angle, height/width, laser power:
    line_prop = l_m.Laser_Object_Properties(fixHeight=False,centerPoint=[0,295-height/2],specifiedLength=width,laserPower=125,angle=0)
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,line_prop)

    #Run the Laser
    l_m.runLaser(laserRobot)

if __name__ == "__main__":
    #Establish connection with Laser Arm:  
    laserDexarm = Dexarm(port="COM4");
    #Initialize Arm:
    laserDexarm.go_home();

    #Initialize Arduino:
    l_m.initializeArduino()

    #Close Laser Door:
    l_m.LaserDoorClose()

    #Laser:
    EngraveActualDog(laserDexarm);
    width, height = EngraveLettersDog(laserDexarm)
    EngraveUnderLine(laserDexarm,width,height)


    #Wait for 0.5 sec and Open Laser Door:
    time.sleep(0.5)
    l_m.LaserDoorOpen();





