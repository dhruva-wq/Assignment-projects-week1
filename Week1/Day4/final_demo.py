import pyautogui
import time
from datetime import datetime

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

print("Open the chrome browser...")
time.sleep(2)

pyautogui.hotkey('win', 'r')
time.sleep(1)
pyautogui.write('chrome')
time.sleep(1)
pyautogui.press('enter')
time.sleep(3)
pyautogui.write('weather today')
time.sleep(1)
pyautogui.press('enter')
time.sleep(5)
pyautogui.hotkey('ctrl','a')
time.sleep(1)
pyautogui.hotkey('ctrl','c')
time.sleep(1)
pyautogui.hotkey('win','r')
time.sleep(1)
pyautogui.write('notepad')
time.sleep(1)
pyautogui.press('enter')
time.sleep(3)
pyautogui.hotkey('ctrl','v')
time.sleep(2)