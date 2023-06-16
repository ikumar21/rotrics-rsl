import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time
import serial

startTime = 0;
firstReading=True

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []
ys2 = []



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
    ax.plot(xs, ys,xs,ys2)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('DHT11 Temperature Data')
    plt.ylabel('Temperature (deg F)')




def initializeArduino():
    global arduinoSerial
    arduinoSerial = serial.Serial("COM5", 115200, timeout=0.2)
    time.sleep(5);




def GetArduinoTemp():
    message = "$T\n" #Get Temp Data
    arduinoSerial.write((bytes(message, 'utf-8')))

    #Wait until temp data is received:
    while True:
        messageIncoming = arduinoSerial.readline()
        if(len(messageIncoming)>0):
            if(chr(messageIncoming[1])=='T'):
                print(messageIncoming)
                t1 = messageIncoming[2:messageIncoming.index(b',')];
                t2 = messageIncoming[messageIncoming.index(b',')+1:];
                print("Temp1:",t1)
                print("Temp2:", t2)
                return float(t1), float(t2)


# Set up plot to call animate() function periodically

initializeArduino();
ani = animation.FuncAnimation(fig, PlotTemp, fargs=(xs,ys,ys2), interval=1000)
plt.show()


#After Clicking Exit: Save Data

print("Hi")