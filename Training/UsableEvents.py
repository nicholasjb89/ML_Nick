import csv


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
                    elif cell.isdigit():
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
                userInputHeader = row
                f_first_run = False
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

    return (frameHeader,frameData), (userInputHeader, userInputData), (screenPanHeader, screenPanData)


print(all_data("c:/Test/00001/frame.csv", "c:/Test/00001/ScreenPan.csv", "c:/Test/00001/input.csv"))