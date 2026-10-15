import pyautogui
import time

time.sleep(3)

pyautogui.typewrite ("Hello, World!", interval=0.1)



#Hotkeys
pyautogui.hotkey('ctrl', 'c')   #CTRL+C
pyautogui.hotkey('ctrl', 'v')   #CTRL+V
pyautogui.hotkey('ctrl', 'a')   #CTRL+A
pyautogui.hotkey('ctrl', 's')   #CTRL+S

#Single pressing special keys
pyautogui.press('enter')    #enter key
pyautogui.press('tab')  #tab key
pyautogui.press('esc')  #esc key
#Holding down keys

pyautogui.keyDown('shift')
pyautogui.typewrite("this is uppercase")
pyautogui.keyUp('shift')

