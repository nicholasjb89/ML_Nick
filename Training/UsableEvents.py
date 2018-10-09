import csv

HOLD_TIME = .15
RECORDED_KEYS = { 0x01: "LeftDown", 0x02 : "RightDown",
                  0x51: "Q",0x57: "W",0x45: "E",0x52: "R",
                  0x31: "1",0x32: "2",0x33: "3",0x34: "4",0x35: "5",0x36: "6",0x37: "7",
                  0x46: "F", 0x47: "G", 0x11: "ctrl", 0x79: "f10", 0x7A: "f11", 0x41: "A",
                  0x20: "Space"}


def all_data(frame_path, screenPan_path, userInput_path):
    # frame
    frameData = []
    with open(frame_path, newline="\n") as frameFile:
        data = csv.reader(frameFile, delimiter=",")
        f_first_run = False
        for row in data:
            if not f_first_run:
                frameHeader = row
                f_first_run = True
            else:
                formatedRow = []
                for cell in row:
                    if cell.isdigit():
                        cell = int(cell)
                    else:
                        cell = float(cell)
                    formatedRow.append(cell)
                frameData.append(formatedRow)
        frameData = sorted(frameData, key=lambda x: x[1])

    # screenPan
    screenPanData = []
    with open(screenPan_path, newline='\n') as screenFile:
        data = csv.reader(screenFile, delimiter=",")
        f_first_run = False
        for row in data:
            if not f_first_run:
                screenPanHeader = row
                f_first_run = True
            else:
                formatedRow = []
                for cell in row:
                    if "." in cell:
                        cell = float(cell)
                    formatedRow.append(cell)
                screenPanData.append(formatedRow)
        screenPanData = sorted(screenPanData, key=lambda x: x[3])

    # userInput
    userInputData = []
    with open(userInput_path, newline="\n") as userInputFile:
        data = csv.reader(userInputFile, delimiter=",")
        f_first_run = True
        for row in data:
            if f_first_run:
                f_first_run = False
                userInputHeader = row
            else:
                formatedRow = []
                for cell in row:
                    if cell.isdigit():
                        cell = int(cell)
                    else:
                        cell = float(cell)
                    formatedRow.append(cell)
                userInputData.append(formatedRow)
        userInputData = sorted(userInputData, key=lambda x: x[3])

    return [[frameHeader, frameData], [screenPanHeader, screenPanData], [userInputHeader, userInputData]]

def default_convert(frame_path, screen_path, userInput_path):
    frame, screen, userInput = all_data(frame_path, screen_path, userInput_path)
    clicks = Click().generate_clicks(userInput, frame)
    print("Click Lenght: ", len(clicks))
    pans = ScreenPan().generate_pans(screen, frame)

    # A Click
    i = 0
    clickA = 0
    aClick = 0
    not_good_click = []
    while i < len(clicks)-1:
        click = clicks[i]
        next_click = clicks[i+1]
        if RECORDED_KEYS[click.event] == "A":
            if RECORDED_KEYS[next_click.event] != "LeftDown":
                not_good_click.append(click)
                clickA += 1
            else:
                aClick += 1
        i += 1
    for click in not_good_click:
        clicks.remove(click)
    print("Click A:", clickA, ", A Click:", aClick)
    print("New Click Length: ", len(clicks))


class Frame(object):
    @staticmethod
    def getFrame(click_time, frameData):
        i = 0
        frameData = frameData[1]
        while i <= len(frameData) - 2:
            frame_time = frameData[i][1]
            next_frame_time = frameData[i + 1][1]
            frame_number = frameData[i][0]
            if click_time > frame_time and click_time < next_frame_time:
                return frame_number
            i += 1

    @staticmethod
    def getFramesBetweenTwo(start, end, frameData):
        frameData = frameData[1]
        frames = []
        for frameIndex, frameTime in frameData:
            if frameTime > start and frameTime < end:
                frames.append(frameIndex)
        return frames


class Click(object):
    def __init__(self, row=None):
        self.raw_data = row
        if self.raw_data is not None:
            self.event = row[0]
            self.start_time = row[3]
            self.end_time = row[7]
            self.mouse_position_press = row[1], row[2]
            self.mouse_position_release = row[5], row[6]
            self.total_time = abs(self.start_time - self.end_time)
            if self.total_time >= HOLD_TIME:
                self.is_held = True
            else:
                self.is_held = False

            self.frames = []
    def generate_clicks(self, userInputData, frameData):
        """
        will generate clicks()
        :return: list() (Click, Click,...)
        """

        def setFrames(events, frameData):
            for event in events:
                event.frames.append(Frame.getFrame(event.start_time, frameData))


        clicks = []
        for press_event, press_x, press_y, press_time, release_event, release_x, release_y, release_time in userInputData[1]:
            row = press_event, press_x, press_y, press_time, release_event, release_x, release_y, release_time
            clicks.append(Click(row))

        setFrames(clicks, frameData)
        return clicks


class ScreenPan(object):
    def __init__(self, row=None):
        if row is not None:
            self.raw_data = row
            self.event = row[0]
            self.start_time = row[3]
            self.mouse_position = row[1], row[2]

            self.frames = []
            self.end_time = None
    def generate_pans(self,panData, frameData):

        def setFrames(events, frameData):
            formatedEvents = []
            i = 0
            while i < len(events):
                event = events[i]
                event.frames.append(Frame.getFrame(event.start_time, frameData))
                i += 1

        pans = []
        for event, mouse_x, mouse_y, panTime in panData[1]:
            row = event, mouse_x, mouse_y, panTime
            pans.append(ScreenPan(row))
        setFrames(pans, frameData)

        formated_pans = []

        i = 0
        saved_pan = pans[0]
        while i < len(pans)-1:
            current_pan = pans[i]
            next_pan = pans[i+1]
            if next_pan.event == next_pan.event:
                if next_pan.frames[0] != current_pan.frames[0]:
                    saved_pan.end_time = current_pan.start_time
                    formated_pans.append(saved_pan)
                    saved_pan = next_pan
            else:
                saved_pan.end_time = current_pan.start_time
                formated_pans.append(saved_pan)
                saved_pan = next_pan

            i += 1
        return formated_pans

if __name__ == "__main__":
    default_convert("c:/Test/00002/frame.csv", "c:/Test/00002/ScreenPan.csv", "c:/Test/00002/input.csv")