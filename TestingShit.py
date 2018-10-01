import cProfile, pstats, io, sys, time, os, copy
import numpy as np
import cv2
import pyautogui
from PIL import Image, ImageGrab, ImageFile
import mss
from win32api import GetKeyState
import win32api
import threading
import csv


def profile(fnc):
    """
    A decorator that uses cProfile to profile a function
    :param fnc:
    :return:
    """
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "tottime"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        i = 0
        line = ""
        for char in s.getvalue():
            if char == "\n":
                print(line)
                line = ""
                i += 1
            else:
                line += char
                if i == 10:
                    break


        return retval
    return inner

@profile
def run():
    startTime = time.time()
    # monitor = {'top': 0, 'left': 0, 'width': 2560, 'height': 1440}
    # SS_array = np.array(mss.mss().grab(monitor))
    # img = Image.fromarray(SS_array)
    #temp = io.BytesIO()
    img = ImageGrab.grab((0, 0, 2560, 1440))
    #img = img.resize((800, 450))
    img = img.convert(mode="L")
    img.save("c:/Test/newTest01.jpg", "JPEG")


@profile
def run2():
    image = pyautogui.screenshot(region=(0, 0, 800, 450))
    #image.resize((600, 450))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

@profile
def run3():
    monitor = {'top': 0, 'left': 0, 'width': 2560, 'height': 1440}
    SS_array = np.array(mss.mss().grab(monitor))
    img = Image.fromarray(SS_array)
    temp = io.BytesIO()
    img = img.resize((800, 450))
    img = img.convert(mode="L")
    img.save(temp, "JPEG")
    temp.name = "c:/Test01/test.jpg"
    print(sys.getsizeof(temp))

def mouse_listener():
    mouse = {0x01: 'leftClick',
             0x02: 'rightClick'}
    while True:
        for i in range(1, 256):
            if win32api.GetAsyncKeyState(i):
                if i in mouse:
                    print(mouse[i])
                    print(time.time())
                    print(pyautogui.position())
                else:
                    print(chr(i))
        time.sleep(.01)

def csvTest():
    def writer():
        theFile = open("eggs.csv", "w", newline="\n")
        theWriter = csv.writer(theFile, delimiter=",")
        theWriter.writerow(["ButtonLeft", (57, 589), time.time()])
        theFile.close()

    def reader():
        theFile = open("eggs.csv", "r", newline="\n")
        theReader = csv.reader(theFile, delimiter=",")

        for row in theReader:
            print(row)
        theFile.close()
    writer()
    reader()

class KeyListener(threading.Thread):
    def __init__(self, key, press_time, mouse_position):
        threading.Thread.__init__(self)
        self.key = key
        self.press = (self.key, press_time, mouse_position)
        self.release = []
        self.lock = threading.Lock()

    def run(self):
        while True:
            if not win32api.GetAsyncKeyState(self.key):
                self.lock.acquire()
                self.release.append([self.key, time.time(), pyautogui.position()])
                self.lock.release()
                break
            time.sleep(.01)


class EventListener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.events = []
        self.lock = threading.Lock()
        self.keyIndexes = list(range(1, 256))

    def run(self):
        while self.isAlive:
            for i in self.keyIndexes:
                if win32api.GetAsyncKeyState(i):
                    event = KeyListener(i, time.time(), pyautogui.position())
                    self.events.append(event)
                    self.events[-1].start()
                    self.keyIndexes.remove(i)
            time.sleep(.01)

    def getEvents(self):
        events = []
        for event in self.events:
            if event.release:
                events.append(event)
                self.events.remove(event)
                self.keyIndexes.append(event.key)

        return events


if __name__ == "__main__":
    csvTest()