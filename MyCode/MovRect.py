import sys

# Add Movement module
sys.path.insert(0, "MovementModule")
from pydexarm import Dexarm

import time

myarm = Dexarm(port="COM6")#Open communication with dexarm

myarm.go_home()

myarm.move_to(x=0,y=350)
myarm.move_to(x=50,y=350)
myarm.move_to(x=50, y=300)
myarm.move_to(x=0,y=300)




