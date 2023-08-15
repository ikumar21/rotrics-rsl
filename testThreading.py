import sys
import time

#Adding Modules to the system path
sys.path.insert(0, 'LaserModule')
sys.path.insert(0, 'MovementModule')
sys.path.insert(0, 'ExampleCode/TourDemo')

#Adding Modules:
from pydexarm import Dexarm
import laser_module as l_m

l_m.initializeArduino()
time.sleep(2)
l_m.LaserDoorOpen()

# import threading
# import time

# CollisionLock = threading.Lock()
# BlockAvailable =threading.Lock()

# def FirstLoop():
#     BlockAvailable.acquire()
#     time.sleep(0.3)
#     for i in range(5):
#         time.sleep(0.3)
#         if i == 2:
#             CollisionLock.release()
#         print("Loop 1: ", i)


# def SecondLoop():
#     CollisionLock.acquire()
#     for i in range(5):
#         time.sleep(0.05)
#         print("Loop 2: ", i)
#     BlockAvailable.release()


# def ThreadLoop1():
#     count=0;
#     while True:
#         count+=1;
#         FirstLoop()
#         if count==3:
#             break;
# def ThreadLoop2():
#     count=0;
#     while True:
#         count+=1;
#         SecondLoop()
#         if count==3:
#             break;


# thread1 = threading.Thread(target=ThreadLoop1)
# thread2  = threading.Thread(target=ThreadLoop2)

# thread1.start()
# CollisionLock.acquire()
# thread2.start()
