import time
import sys

def backspace(howMany):
    """
    '\b' moves the cursor one character back.
    ' '  erases the characters
    '\b' then move back again, having a clean slate ahead
    """
    sys.stdout.write('\b'*howMany)
    sys.stdout.write(' ' *howMany)
    sys.stdout.write('\b'*howMany)
    sys.stdout.flush()

def write(str):
    """
    Write out string and then flush it so it will actually be printed.
    After and before a sleep call
    """
    sys.stdout.write(str)
    sys.stdout.flush()

def loading(iterations, loadBarLength, loadChar, wait):
    """
    iterations    - The number of times the full loading bar will display
    loadBarLength - The count of characters that makes up a full loading bar
    loadChar      - The character to use as the loading symbol
    wait          - The amount of time to wait in seconds before printing the next loadChar
    """
    for i in range(iterations):
        for _ in range(loadBarLength):
            write(loadChar)
            time.sleep(wait)
        backspace(loadBarLength)
        time.sleep(wait)
