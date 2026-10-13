#import pyautogui
#pyautogui.FAILSAFE = True
#pyautogui.PAUSE = 5.0


import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1.0

print("Screen size:", pyautogui.size())
print("Mouse position:", pyautogui.position())

pyautogui.moveTo(500, 500, duration=1)   # move mouse to (500, 500) over 1 second
pyautogui.click()                        # click there
pyautogui.write("Hello from PyAutoGUI!", interval=0.1)  # type text