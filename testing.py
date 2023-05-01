import time

now_ns = time.time_ns() # Time in nanoseconds
start_time = int(now_ns / 1000000)

count = 0;


while(count<100):
    now_ns = time.time_ns() # Time in nanoseconds
    now_ms = int(now_ns / 1000000)
    if(now_ms%100):
        print(now_ms-start_time)

