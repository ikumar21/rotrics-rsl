import threading
import time

def a():
    for i in range(10): 
        time.sleep(0.05)
        print(i);


def b():
    for x in range(5):
        time.sleep(0.01)
        print("HI")

def doThreadActions():
    thread1 = threading.Thread(target=a)
    thread2  = threading.Thread(target=b)

    thread1.start()
    thread2.start()

    thread2.join()
    thread1.join()

doThreadActions()

doThreadActions()
doThreadActions()