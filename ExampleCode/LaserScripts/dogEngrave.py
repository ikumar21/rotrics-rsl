#Add Laser Module:
import sys
sys.path.insert(0, 'LaserModule')
import laser_module as l_m

#Import Movement Module:
sys.path.insert(0, 'MovementModule')
from pydexarm import Dexarm



def EngraveActualDog(laserRobot):

    #File Name:
    fileLocName = "LaserModule/rotricsGcode/dog.gcode";
    
    #Set laser object center, angle, height/width, laser power:
    dog_laser = l_m.Laser_Object_Properties(fixHeight=True,centerPoint=[0,340-25],specifiedLength=50,laserPower=125,angle=0)
    
    #Generate G-Code:
    l_m.GcodeObjectCreation(fileLocName,dog_laser)

    #Run the Laser
    l_m.runLaser(laserRobot)


def EngraveLettersDog(laserRobot):
    width, height = l_m.gcode_message_creation("DOG",20,True,125,(0,273))
    l_m.runLaser(laserRobot)
    return width;

def EngraveUnderline(laserRobot, width):
    #Get lines from G-code:
    with open("LaserModule/rotricsGcode/HorizontalLine.gcode", "r") as f: lineLines = f.readlines()
    
    #Set laser object center, angle, height/width, laser power:
    line_properties = l_m.Laser_Object_Properties(fixHeight=False,centerPoint=[0,80],specifiedLength=width,laserPower=125,angle=0)
    
    #Get the modifed G-code with right properties
    laserLines = l_m.ModifyGcode(lineLines, line_properties)

    #Write to file
    with open("outputGcode.txt", "w") as f:
        f.writelines(laserLines)
    f.close()

    #Run the Laser
    l_m.runLaser(laserRobot)



if __name__ == "__main__":
    #Initialize Laser Arm:
    laserDexarm = Dexarm(port="COM4");

    #Laser:
    EngraveActualDog(laserDexarm);
    letterWidth = EngraveLettersDog(laserDexarm)
    EngraveUnderline(laserDexarm,letterWidth);



