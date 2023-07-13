#Add Laser Module:
import sys
sys.path.insert(0, 'LaserModule')
import laser_module as l_m

#Import Movement Module:
sys.path.insert(0, 'MovementModule')
from pydexarm import Dexarm



def CutShapes(laserDexarm):
    fileLocName = "LaserModule/rotricsGcode/CircleOutline.gcode";
    
    #Set laser object center, angle, height/width, laser power:
    shapes_prop = l_m.Laser_Object_Properties(fixHeight=False,centerPoint=[60,350],specifiedLength=35,laserPower=50,angle=0)

    #Change Speed:
    shapes_prop.movingFeedrate=800;
    shapes_prop.laseringFeedrate=400;
    
    #Generate G-Code:
    width, height = l_m.GcodeObjectCreation(fileLocName,shapes_prop)



if __name__ == "__main__":
    #Establish connection with Laser Arm:  
    laserDexarm = Dexarm(port="COM4");

    #Initialize Arm:
    laserDexarm.go_home();

    #Generate G-code:
    CutShapes(laserDexarm);
    
    #Run Laser
    l_m.runLaser(laserDexarm)