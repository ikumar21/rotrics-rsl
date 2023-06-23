import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time
import serial
import csv
import random
from itertools import zip_longest

startTime = 0;
firstReading=True

startTimeC=0;
firstReadingC =0;



# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []
ys2 = []


hfig = plt.figure()
hax = hfig.add_subplot(1, 1, 1)
hys = []
hys2 = []

figControl = plt.figure()
axControl =  figControl.add_subplot(1, 1, 1)
xControl =[]
controlForce = []

currentHum1 = 0;
currentHum2 = 0;



var1 = 0;
# Initialize communication with TMP102


# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    global var1;
    # Read temperature (Celsius) from TMP102
    temp_c = round(var1, 2)

    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(temp_c)

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('TMP102 Temperature over Time')
    plt.ylabel('Temperature (deg C)')
    var1+=1;
    if(var1>10):
        var1-=2;

def PlotTemp(i,xs,ys,ys2):
    lowTemp = 78;
    highTemp = 80;

    temp1, temp2 = GetArduinoTemp();
    global firstReading, startTime;
    if(firstReading):
        firstReading=False;
        startTime = time.monotonic();

    nowTime = time.monotonic()


    # Add x and y to lists
    # xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    xs.append(round(nowTime-startTime,1))
    ys.append(temp1)
    ys2.append(temp2)

    # Limit x and y lists to 20 items
    # xs = xs[-20:]
    # ys = ys[-20:]
    # ys2 = ys2[-20:]



    # Draw x and y lists
    ax.clear()
    lowTempThresh = []
    highTempThresh = [];

    for _ in xs: lowTempThresh.append(lowTemp);
    for _ in xs: highTempThresh.append(highTemp);

    ax.plot(xs, ys,xs,ys2,xs,lowTempThresh,xs,highTempThresh);


    # Format plot
    ax.set_title('DHT11 Temperature Data')
    ax.legend(['Sensor 1', 'Sensor 2', 'Low Temp. Threshold', 'High Temp. Threshold'])
    ax.set_xlabel("Time (s)")
    ax.set_ylabel('Temperature (deg F)')




def initializeArduino():
    global arduinoSerial
    arduinoSerial = serial.Serial("/dev/cu.usbmodem14101", 115200, timeout=0.2)
    time.sleep(5);




def GetArduinoTemp():
    message = "$T\n" #Get Temp Data
    arduinoSerial.write((bytes(message, 'utf-8')))

    #Wait until temp data is received:
    while True:
        messageIncoming = arduinoSerial.readline()
        if(len(messageIncoming)>0):
            if(chr(messageIncoming[1])=='T'):
                global currentHum1,currentHum2
                print(messageIncoming)
                t1 = messageIncoming[2:messageIncoming.index(b',')];
                t2 = messageIncoming[messageIncoming.index(b',')+1:messageIncoming.index(b';')];
                currentHum1 = messageIncoming[messageIncoming.index(b';')+1:messageIncoming.index(b'(')];
                currentHum2 = messageIncoming[messageIncoming.index(b'(')+1:messageIncoming.index(b'\r')];
                print("Temp1:",t1)
                print("Temp2:", t2)
                print("Hum:",currentHum1,currentHum2)
                break;
    hys.append(float(currentHum1))
    hys2.append(float(currentHum2))
    while True:
        messageIncoming = arduinoSerial.readline()
        if(len(messageIncoming)>0):
            if(chr(messageIncoming[1])=='C'):
                print(messageIncoming)
                control = messageIncoming[2:messageIncoming.index(b'\r')];
                print("Control Force:",control)
                controlForce.append(int(control));
                break;
    
    return float(t1), float(t2)

# Set up plot to call animate() function periodically

def PlotHum(i,xs,ys,ys2):

    # Add x and y to lists
    # xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    # ys.append(float(currentHum1))
    # ys2.append(float(currentHum2))

    # Limit x and y lists to 20 items
    # xs = xs[-20:]
    # ys = ys[-20:]
    # ys2 = ys2[-20:]

    # Draw x and y lists



    hax.clear()
    hax.plot(xs, ys,xs,ys2)


    # Format plot
    hax.set_title('DHT11 Humidity Data')
    hax.legend(['Sensor 1', 'Sensor 2'])
    hax.set_xlabel("Time (s)")
    hax.set_ylabel('Relative Humidity (%)')
    
    
def GetHeaterControl():
    message = "$C\n" #Get Temp Data
    arduinoSerial.write((bytes(message, 'utf-8')))

    #Wait until temp data is received:
    while True:
        messageIncoming = arduinoSerial.readline()
        if(len(messageIncoming)>0):
            if(chr(messageIncoming[1])=='D'):
                print(messageIncoming)
                control = messageIncoming[2:messageIncoming.index(b',')];

                print("Control:",bool(control))
                return int(control)

def PlotControl(i,xs,ys):

    # Add x and y to lists
    # xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))

    # Limit x and y lists to 20 items
    # xs = xs[-20:]
    # ys = ys[-20:]
    # ys2 = ys2[-20:]

    # Draw x and y lists
    axControl.clear()
    axControl.plot(xs, ys)


    # Format plot
    axControl.set_title('Heater Control Status')
    axControl.set_xlabel("Time (s)")
    axControl.set_ylabel('On/Off')



initializeArduino();
ani = animation.FuncAnimation(fig, PlotTemp, fargs=(xs,ys,ys2), interval=1200)
aniHum = animation.FuncAnimation(hfig, PlotHum, fargs=(xs,hys,hys2), interval=1200)
aniControl = animation.FuncAnimation(figControl, PlotControl, fargs=(xs,controlForce), interval=1200)
plt.show()




d = [xs,ys,ys2,hys,hys2,xControl,controlForce];
fields = ['Time (s)', 'Temp 1 (F)', 'Temp 2 (F)','Humidity 1 (%)','Humidity 2 (%)','Time (s)', 'Control Force']
with open("AllData.csv","w+") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    for values in zip_longest(*d):
        writer.writerow(values)

# # Define the fields that will be used as column headers in the CSV file
# fields = ['Time (s)', 'Temp 1 (F)', 'Temp 2 (F)','Humidity 1 (%)','Humidity 2 (%)','Time (s)', 'Control Force']

# # Create a list of rows, where each row is a list of values that will be written to the CSV file

# rows = [];

# for index in range(len(xControl)):
#     row = [];
#     if(index<len(xs)):
#         row.append()
#     else:
#         row.append('')

# rows = [
#     ['XYZ', '011', '2000'],
#     ['ABC', '012', '8000'],
#     ['PQR', '351', '5000'],
#     ['EFG', '146', '10000']
# ]

# # Open a file called 'EmployeeData.csv' in write mode ('w') and use it as a context manager
# # The 'with' statement ensures that the file is automatically closed when the block of code is finished
# with open('EmployeeData.csv', 'w') as f:
    
#     # Create a CSV writer object that will write to the file 'f'
#     csv_writer = csv.writer(f)
    
#     # Write the field names (column headers) to the first row of the CSV file
#     csv_writer.writerow(fields)
    
#     # Write all of the rows of data to the CSV file
#     csv_writer.writerows(rows)





# #After Clicking Exit: Save Data
# file = open('TempHum.txt','w')
# file.writelines(xs)
# file.close()

# file = open('Temp1.txt','w')
# file.writelines(xs)
# file.close()



# items = ['Mango', 'Orange', 'Apple', 'Lemon']
# file = open('items.txt','w')
# for item in items:
# 	file.write(item+"\n")
# file.close()