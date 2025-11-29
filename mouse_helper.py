import pyautogui
import time
import os

print("=====================================================")
print(" 📍 COORDINATE FINDER TOOL")
print("=====================================================")
print("1. Maximize your Careflow/Browser window.")
print("2. Hover your mouse over the name 'Diana Rossi'.")
print("3. Write down the X and Y shown below.")
print("4. Do the same for 'Summary', 'Consultations', etc.")
print("5. Press Ctrl+C to stop.")
print("=====================================================\n")

try:
    while True:
        x, y = pyautogui.position()
        # \r makes it overwrite the same line
        print(f"👉 MOUSE POSITION: x={x}, y={y}      ", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n✅ Done.")