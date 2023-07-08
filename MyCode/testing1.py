import sys


# Add Movement module
sys.path.insert(0, "MovementModule")
from pydexarm import Dexarm

#Add Laser Module:
sys.path.insert(0, 'LaserModule')
import laser_module as l_m

import time

from pydexarm import Dexarm

# myarm = Dexarm(port="COM6")#Open communication with dexarm


# myarm.go_home()#Goes to robot home position


# myarm.move_to(x=200,z=50,y=200,feedrate=30000)

# myarm.air_picker_pick();

# time.sleep(3)

# myarm.move_to(x=-200,y=300, z=50)

# myarm.move_to(z=-10)
# myarm.air_picker_place()
# time.sleep(0.5)
# myarm.air_picker_stop()
# l_m.initializeArduino();
# time.sleep(3);
# l_m.LaserDoorClose()

laserarm = Dexarm(port="COM4")#Open communication with Dexarm

l_m.initializeArduino()

time.sleep(3)

l_m.LaserDoorClose()

l_m.gcode_message_creation("DOG",20,False,255,(0,300))
l_m.runLaser(laserarm)
l_m.LaserDoorOpen()



