import sys
# adding folder to the system path
sys.path.insert(0, '../../')
import time
#from pydexarm import Dexarm
import keyboard
import threading
import sys
import constants as c
import serial

#cd Desktop/rotrics-rsl/ExampleCode/Coaster

ArduinoSerial = serial.Serial("COM5", 115200, timeout=0.1)

mess = "$C\r\n"
ArduinoSerial.write((bytes(mess, 'utf-8')))
time.sleep(1)
ArduinoSerial.write((bytes(mess, 'utf-8')))
time.sleep(1)

print("o")

while True:
    messageIncoming = ArduinoSerial.readline()
    if(len(messageIncoming)>0):
        print(messageIncoming)
        if(chr(messageIncoming[1])=='A'):
            ArduinoSerial.write((bytes(mess, 'utf-8')))