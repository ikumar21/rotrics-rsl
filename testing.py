import serial
import time
def initializeArduino():
    global laserArduinoSerial
    laserArduinoSerial = serial.Serial("COM7", 115200,  timeout=1)
def LaserDoorClose():
    message = "$C\r\n"
    laserArduinoSerial.write(bytes(message,'utf-8'))

    #Wait until door is opened:
    while True:
        messageIncoming = laserArduinoSerial.readline()
        if(len(messageIncoming)>0):
            if(chr(messageIncoming[1])=='D'):
                break;
def LaserDoorOpen():
    message = "$O\n"
    laserArduinoSerial.write(message.encode())
    print("send")
    laserArduinoSerial.write((bytes(message, 'utf-8')))
    #Wait until door is opened:
    while True:
        messageIncoming = laserArduinoSerial.readline()
        if(len(messageIncoming)>0):
            print(messageIncoming)
            if(chr(messageIncoming[1])=='D'):
                break;


initializeArduino();
time.sleep(5)
LaserDoorOpen();
