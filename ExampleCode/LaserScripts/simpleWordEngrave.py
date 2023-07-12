#Add Laser Module:
import sys
sys.path.insert(0, 'LaserModule')
import laser_module as l_m

#Import Movement Module:
sys.path.insert(0, 'MovementModule')
from pydexarm import Dexarm



#Code:

#Word to Laser:
word="FIRE"

#Establish connection with Laser Arm:  
laserDexarm = Dexarm(port="COM4");

#Initialize Arm:
laserDexarm.go_home();

#Generate G-Code; Get final width and height of lasered Word:
width, height = l_m.gcode_message_creation(word,20,False,125,(0,300))

#Run laser:
l_m.runLaser(laserDexarm)
