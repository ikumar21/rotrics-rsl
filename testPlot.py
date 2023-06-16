import time


startTime = time.monotonic()

time.sleep(3)

stopTime = time.monotonic()

print(startTime,stopTime, stopTime-startTime)