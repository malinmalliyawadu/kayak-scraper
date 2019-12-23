import time
import sys
from loading import write, backspace

def countdown(start, wait):
    for i in range(start, 0, -1):
        write(str(i))
        time.sleep(wait)
        backspace(len(str(i)))
