import sys

def delete_last_lines(n=1):
    for _ in range(n):
        sys.stdout.write("\033[F") #back to previous line
        sys.stdout.write("\033[K") #clear line
        sys.stdout.flush()

