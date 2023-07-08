import sys

# Add Movement module
sys.path.insert(0, "MovementModule")
from pydexarm import Dexarm


import time

myarm2 = Dexarm(port="COM6")#Open communication with dexarm
myarm2.go_home()

myarm2.conveyor_belt_backward(5000)
time.sleep(5)
myarm2.conveyor_belt_stop()

