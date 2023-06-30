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
    dog_laser = l_m.Laser_Object_Properties(fixHeight=True,centerPoint=[0,305],specifiedLength=20,laserPower=125,angle=0)
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,dog_laser)

    #Run the Laser
    l_m.runLaser(laserRobot)



def EngraveLettersDog(laserRobot):
    width, height = l_m.gcode_message_creation("DOG",20,False,125,(0,290))
    l_m.runLaser(laserRobot)
    return width;

def EngraveUnderline(laserRobot, width):

    #File Name:
    fileLocName = "LaserModule/rotricsGcode/HorizontalLine.gcode";
    
    #Set laser object center, angle, height/width, laser power:
    line_properties = l_m.Laser_Object_Properties(fixHeight=False,centerPoint=[0,285],specifiedLength=20,laserPower=200,angle=0)
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,line_properties)

    print("WIDTH", width, height)
    #Run the Laser
    l_m.runLaser(laserRobot)


if __name__ == "__main__":
    #Initialize Laser Arm:
    laserDexarm = Dexarm(port="COM4");

    #Laser:
    EngraveActualDog(laserDexarm);
    letterWidth = EngraveLettersDog(laserDexarm)
    letterWidth=6;
    EngraveUnderline(laserDexarm,letterWidth);


