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
    width, height = l_m.gcode_message_creation("CAT",15,False,255,(0,300))
    l_m.runLaser(laserRobot)
    return width;



if __name__ == "__main__":
    #Initialize Laser Arm:
    laserDexarm = Dexarm(port="COM4");

    #Laser:
    # EngraveActualDog(laserDexarm);
    for _ in range(20):
        EngraveLettersDog(laserDexarm)




