import sys
# adding folder to the system path
sys.path.insert(0, '../../')
import time
from pydexarm import Dexarm
import keyboard
import threading
import sys
import constants as c




pickerDexarm = Dexarm(port="COM6")
pickerDexarm.go_home()

pickerDexarm.conveyor_belt_move(-280,4000)
