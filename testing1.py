import serial
import time

arduino = serial.Serial(port='COM7', baudrate=9600, timeout=.1)


def write_read(x):
    arduino.flushOutput()
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data


while True:
    num = input("Enter a number: ")
    print(type(num))
    value = write_read(num)
    print(value)