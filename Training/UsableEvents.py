import csv
SCREEN_CAPTURE_BBOX = (0, 0, 2560, 1440)
TIME_BLOCK = .15
RECORDED_KEYS = { 0x01: "LeftDown", 0x02 : "RightDown",
                  0x51: "Q",0x57: "W",0x45: "E",0x52: "R",
                  0x31: "1",0x32: "2",0x33: "3",0x34: "4",0x35: "5",0x36: "6",0x37: "7",
                  0x46: "F", 0x47: "G", 0x11: "ctrl", 0x79: "f10", 0x7A: "f11", 0x41: "A",
                  0x20: "Space"}

START_REC_KEY = 0x79
END_REC_KEY = 0x7A

HOLD_TIME = .50

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
                        cell = int(cell)
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

    return (frameHeader, frameData), (screenPanHeader, screenPanData), (userInputHeader, userInputData)

class Click(object):
    def __init__(self, row = None):
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
        clicks = []
        for press_event, press_x, press_y, press_time, release_event, release_x, release_y, release_time in userInputData[1]:
            row = press_event, press_x, press_y, press_time, release_event, release_x, release_y, release_time
            clicks.append(Click(row))

        i = 0
        frameData = frameData[1]
        while i <= len(frameData)-2:
            frame_time = frameData[i][1]
            next_frame_time = frameData[i+1][1]
            frame_number = frameData[i][0]
            next_frame_Number = frameData[i+1][1]
            for click in clicks:
                if not click.is_held:
                    if click.start_time > frame_time and click.start_time < next_frame_time:
                        click.frames.append(frame_number)
                else:
                    pass
                    #todo if the key is heald
                    # if its heald i need to know the press frame and the release frame. (click.start_time, click.end_time)
            i += 1
        return clicks


if __name__ == "__main__":
    frame, screen, userInput = all_data("c:/Test/00001/frame.csv", "c:/Test/00001/ScreenPan.csv", "c:/Test/00001/input.csv")
    clicks = Click().generate_clicks(userInput,frame)
    for click in clicks:
        print(click.frames)
        print(click.start_time)
