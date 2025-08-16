import os
import time
import sys

os.system('clear')

RED = "\033[31m"
GREEN = "\033[32m"
WHITE = "\033[37m"
RESET = "\033[0m"

message = f"{RED}Tools {GREEN}is {WHITE}updating, please wait"
print(message, end="", flush=True)

for i in range(10):
    dot_color = [RED, GREEN, WHITE][i % 3]
    print(dot_color + ".", end="", flush=True)
    time.sleep(0.5)

print("\n" + GREEN + "Update completed successfully!" + RESET)
