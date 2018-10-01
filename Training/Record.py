from PIL import ImageGrab
import os
import threading
import time
import csv
import pyautogui
import win32api
import copy

SCREEN_CAPTURE_BBOX = (0, 0, 2560, 1440)
TIME_BLOCK = .15
RECORDED_KEYS = { 0x01: "LeftDown", 0x02 : "RightDown",
                  0x51: "Q",0x57: "W",0x45: "E",0x52: "R",
                  0x31: "1",0x32: "2",0x33: "3",0x34: "4",0x35: "5",0x36: "6",0x37: "7",
                  0x46: "F", 0x47: "G", 0x11: "ctrl", 0x79: "f10", 0x7A: "f11", 0x41: "A",
                  0x20: "Space"}

START_REC_KEY = 0x79
END_REC_KEY = 0x7A

# todo add ability top pan the screen


class PressReleaseListener(threading.Thread):
    def __init__(self, event, mouse_position, press_time):
        threading.Thread.__init__(self)
        self.event = event
        self.press = (self.event, mouse_position, press_time)
        self.release = ()
        self.lock = threading.Lock()

    def run(self):
        while True:
            if not win32api.GetAsyncKeyState(self.event):
                self.lock.acquire()
                self.release = (self.event, pyautogui.position(), time.time())
                self.lock.release()
                break
            time.sleep(.01)


class ScreenPanListener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = "ScreenPan"
        self.leftPan = []
        self.rightPan = []
        self.upPan = []
        self.downPan = []
        self.kill = False
        self.allPans = []

    def run(self):
        while not self.kill:
            mouse_position = pyautogui.position()
            if mouse_position[0] <= SCREEN_CAPTURE_BBOX[0]+1:
                self.leftPan.append(("LeftPan", mouse_position, time.time()))
            if mouse_position[0] >= SCREEN_CAPTURE_BBOX[2]-1:
                self.rightPan.append(("RightPan", mouse_position, time.time()))
            if mouse_position[1] <= SCREEN_CAPTURE_BBOX[1]+1:
                self.upPan.append(("UpPan", mouse_position, time.time()))
            if mouse_position[1] >= SCREEN_CAPTURE_BBOX[3]-1:
                self.downPan.append(("DownPan", mouse_position, time.time()))
            time.sleep(.1)

    def is_empty(self):
        if self.leftPan:
            return False
        elif self.rightPan:
            return False
        elif self.upPan:
            return False
        elif self.downPan:
            return False
        else:
            return True


class EventListener(threading.Thread):
    def __init__(self, recorded_keys):
        threading.Thread.__init__(self)
        self.press_release_events = []
        self.screen_pan_events = []
        self.lock = threading.Lock()
        self.keyIndexes = list(recorded_keys.keys())
        self.kill = False

    def run(self):
        while not self.kill:
            screenPan = ScreenPanListener()
            screenPan.start()
            for i in self.keyIndexes:
                if win32api.GetAsyncKeyState(i):
                    event = PressReleaseListener(i, pyautogui.position(), time.time())
                    self.press_release_events.append(event)
                    self.press_release_events[-1].start()
                    self.keyIndexes.remove(i)
            time.sleep(.1)
            screenPan.kill = True
            if not screenPan.is_empty():
                self.screen_pan_events.append(screenPan)


    def getEvents(self):
        events = []
        for event in self.press_release_events:
            if event.release:
                events.append(event)
                self.press_release_events.remove(event)
                self.keyIndexes.append(event.event)
        for pan_event in self.screen_pan_events:
            if not pan_event.is_empty():
                events.append(pan_event)
                self.screen_pan_events.remove(pan_event)

        return events


class UserInput(threading.Thread):
    def __init__(self):
        """
        :param screen_bbox: screen capture bbox example (0, 0, 2560, 1440)
        """
        threading.Thread.__init__(self)
        self.inputKeys = copy.copy(RECORDED_KEYS)
        self.start_recording = False
        self.kill = False

        self.inputData = []

    def run(self):
        eventListener = EventListener(self.inputKeys)
        eventListener.start()
        while not self.kill:
            events = eventListener.getEvents()
            if not self.start_recording:
                for event in events:
                    if event.event == START_REC_KEY:
                        self.start_recording = True
            else:
                for event in events:
                    if event.event == END_REC_KEY:
                        self.kill = True
                        eventListener.kill = True
                self.inputData.append(events)
            time.sleep(.01)

    def getInput(self):
        theInput = self.inputData
        self.inputData = []
        return theInput


class SaveData(object):
    def __init__(self, champion, directory="Defualt"):
        self.folder_integerCount = 5  # the number format will look like this Lucian00001 for the folder
        self.file_integerCount = 10
        self.file_number = 0
        self.captured_events = []
        self.frame_index_time = []
        self.ss_data = []

        self.champion = champion
        if directory == "Defualt":
            directory = "./Data/" + self.champion + "/"
        self.directory = directory
        self.directory = self.newFolder()
        self.inputFile = self.directory+"input.csv"
        self.frameFile = self.directory+"frame.csv"
        self.screenPanFile = self.directory+"screenPan.csv"
        open(self.inputFile, "wb") # creates the input folder

    def getFolderInteger(self):
        largest = 0
        for i in os.listdir(self.directory):
            if os.path.isdir(self.directory+i):

                number = int(i)
                if number > largest:
                    largest = number
        return largest

    def newFolder(self):
        folderInt = self.getFolderInteger() + 1
        print(folderInt)
        name = "0" * (self.folder_integerCount - len(str(folderInt)))
        name += str(folderInt)
        path = self.directory+name+"/"
        os.mkdir(path)
        return path

    def save(self, userInput, resize=False):
        newFileName = "0"*(self.file_integerCount-len(str(self.file_number)))
        newFileName += str(self.file_number)
        newFileName += ".jpg"
        self.captured_events.append(userInput)
        self.frame_index_time.append((newFileName[0:-4], time.time()))
        self.file_number += 1

        img = ImageGrab.grab(SCREEN_CAPTURE_BBOX)
        if resize:
            img = img.resize((800, 450))
        img = img.convert(mode="L")

        img.save(self.directory+newFileName, "JPEG")

    def quit(self):
        """
        must be called before the program exits to save all the input
        :return: nothing!
        """
        inputFile = open(self.inputFile, "w")
        frameFile = open(self.frameFile, "w")
        screenPanFile = open(self.screenPanFile, "w")
        csv_writer_input = csv.writer(inputFile, delimiter=",")
        csv_writer_frame = csv.writer(frameFile, delimiter=",")
        csv_writer_screenPan = csv.writer(screenPanFile, delimiter=",")
        csv_writer_input.writerow(("event", "mouse_x", "mouse_y", "time",
                                   "event", "mouse_x", "mouse_y", "time"))
        csv_writer_frame.writerow(("FrameID", "Time"))
        csv_writer_screenPan.writerow(("event", "mouse_x", "mouse_y", "time"))
        for events in self.captured_events:

            for event in events:
                if event:
                    for e in event:
                        if e.event == "ScreenPan":
                            thePans = [e.leftPan, e.rightPan, e.upPan, e.downPan]
                            for pan in thePans:
                                if pan:
                                    for pan_event in pan:
                                        sp_event = pan_event[0]
                                        sp_mouse_x = pan_event[1][0]
                                        sp_mouse_y = pan_event[1][1]
                                        sp_time = pan_event[2]
                                        csv_writer_screenPan.writerow([sp_event, sp_mouse_x, sp_mouse_y, sp_time])
                        else:
                            press = e.press
                            p_event = press[0]
                            p_mouse_x = press[1][0]
                            p_mouse_y = press[1][1]
                            p_time = press[2]

                            release = e.release
                            r_event = release[0]
                            r_mouse_x = release[1][0]
                            r_mouse_y = release[1][1]
                            r_time = release[2]

                            csv_writer_input.writerow([p_event, p_mouse_x, p_mouse_y, p_time,
                                                       r_event, r_mouse_x, r_mouse_y, r_time])
        for frame, the_time in self.frame_index_time:
            csv_writer_frame.writerow((frame, the_time))

        inputFile.close()


def run():
    userInput = UserInput()
    userInput.start()
    data = SaveData("Lucian", directory="c:/Test/")
    while userInput.isAlive():
        if userInput.start_recording:
            startingTime = time.time()
            data.save(userInput.getInput())
            endingTime = time.time()
            totalTime = endingTime-startingTime
            #print(totalTime)
            if TIME_BLOCK - totalTime > 0:
                time.sleep(TIME_BLOCK - totalTime)

    data.quit()


if __name__ == "__main__":
    run()
