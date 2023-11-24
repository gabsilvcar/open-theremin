from synth import Synth
import pyautogui
import time
import threading

performanceDuration = 10 # em segundos

width, heidth = pyautogui.size()

synth = Synth()

def findMouseLoop():
    for i in range(performanceDuration * 100):
        x, y = pyautogui.position()
        actual_x = x / width
        actual_y = 1 - (y / heidth)
        synth.setFrequency(actual_y)
        synth.setFilter(actual_x)
        time.sleep(0.01)

mouseThread = threading.Thread(target=findMouseLoop)

synth.startPerformance(performanceDuration)

mouseThread.start()

mouseThread.join()

synth.stopPerformance()
