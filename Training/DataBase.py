import sqlite3 as sql
import csv
import os
import numpy as np
from PIL import Image

COLUMNS = {"click": ("id", "event", "start_time", "mouse_position_press_x", "mouse_position_press_y",
                     "mouse_position_release_x", "mouse_position_release_y", "total_time", "frame"),
           "screenPan": ("id", "event", "start_time", "mouse_position_x", "mouse_position_y", "frame"),
           "frame": ("id", "start_time", "path"),
           "click_archive": ("id", "event", "start_time", "mouse_position_press_x", "mouse_position_press_y",
                     "mouse_position_release_x", "mouse_position_release_y", "total_time", "frame"),
           "screenPan_archive": ("id", "event", "start_time", "mouse_position_x", "mouse_position_y", "frame"),
           "frame_archive": ("id", "start_time", "path"),
           "humaninterface": ("id", "string", "path"),
           "usedAbilityIcon": ("id", "string", "path")
           }

RECORDED_KEYS = { 0x01: "leftclick", 0x02 : "rightclick",
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
                    if not cell.isdigit():
                        cell = float(cell)
                    else:
                        cell = str(cell)
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


def create_table_click(c):
    c.execute("""CREATE TABLE IF NOT EXISTS click(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            event INTEGER,
            start_time REAL,
            mouse_position_press_x INTEGER,
            mouse_position_press_y INTEGER,
            mouse_position_release_x INTEGER,
            mouse_position_release_y INTEGER,
            total_time REAL,
            frame TEXT
            )"""
              )


def create_table_screenPan(c):
    c.execute("""CREATE TABLE IF NOT EXISTS screenPan(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                start_time REAL,
                mouse_position_x INTEGER,
                mouse_position_y INTEGER,
                frame TEXT)
                """
              )


def create_table_frame(c):
    c.execute("""CREATE TABLE IF NOT EXISTS frame(
                    id TEXT PRIMARY KEY,
                    start_time REAL,
                    path TEXT)
                   """
              )


def create_table_click_archive(c):
    c.execute("""CREATE TABLE IF NOT EXISTS click_archive(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            event INTEGER,
            start_time REAL,
            mouse_position_press_x INTEGER,
            mouse_position_press_y INTEGER,
            mouse_position_release_x INTEGER,
            mouse_position_release_y INTEGER,
            total_time REAL,
            frame TEXT
            )"""
              )


def create_table_screePan_archive(c):
    c.execute("""CREATE TABLE IF NOT EXISTS screenPan_archive(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                start_time REAL,
                mouse_position_x INTEGER,
                mouse_position_y INTEGER,
                frame TEXT)
                """
              )


def create_table_frame_archive(c):
    c.execute("""CREATE TABLE IF NOT EXISTS frame_archive(
                    id TEXT PRIMARY KEY,
                    start_time REAL,
                    path TEXT)
                   """
              )


def create_table_human_interface(c):
    c.execute("""CREATE TABLE IF NOT EXISTS humaninterface(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                string TEXT,
                path TEXT)
    """)


def create_table_used_ability_icon(c):
    c.execute("""CREATE TABLE IF NOT EXISTS usedAbilityIcon(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                string TEXT,
                path TEXT)
    """)


class DataBase(object):
    def __init__(self, path, name):
        """

        :param clicks: list() (Click,...)
        :param pans: list() (Pans,...)
        :param frames: list() (list(),...)
        """
        conn = sql.connect(path + ".db")
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        self.c = c
        self.conn = conn
        self.path = path

    def _insert_into(self, table_name, values, batch=False):
        """
        This only works for click like tables! (click and click_archive)
        :param table_name: string() name of the table that will be inserted into
        :param values: list() all the values that will be added in
        :param batch: Bool() if im doing a lot of inserts setting  batch to True will not commit after each insert you
        must use conn.commit() after inserting though
        :return:
        """
        execution_text = """INSERT INTO {}{} VALUES{}

        """
        if len(values) == len(COLUMNS[table_name]) - 1:
            execution_text = execution_text.format(table_name, COLUMNS[table_name][1:], values)
        else:
            execution_text = execution_text.format(table_name, COLUMNS[table_name], values)
        self.c.execute(execution_text)
        if not batch:  # if im only doing a couple just commit after each insert
            self.conn.commit()

    def new(self, clicks, pans, frames, inputImagesPath, usedAbilitiesPath):
        create_table_screenPan(self.c)
        create_table_frame(self.c)
        create_table_click(self.c)
        create_table_click_archive(self.c)
        create_table_screePan_archive(self.c)
        create_table_frame_archive(self.c)
        create_table_human_interface(self.c)
        create_table_used_ability_icon(self.c)
        self.clicks = clicks[1]
        self.pans = pans[1]
        self.frames = frames[1]
        for click in self.clicks:
            event = click[0]
            start_time = click[3]
            mouse_position_press = click[1], click[2]
            mouse_position_release = click[5], click[6]
            total_time = click[7] - start_time
            i = 0
            while self.frames[i][1] < start_time:
                i += 1
            frame = self.frames[i][0]
            self._insert_into("click", (event, start_time, mouse_position_press[0], mouse_position_press[1],
                                      mouse_position_release[0], mouse_position_release[1], total_time, frame), batch=True)

        for pan in self.pans:
            event = pan[0]
            mouse_x = pan[1]
            mouse_y = pan[2]
            time = pan[3]
            i = 0
            while self.frames[i][1] < time:
                i += 1
            frame = self.frames[i][0]
            self._insert_into("screenPan", (event, time, mouse_x, mouse_y, frame), batch=True)

        for frame in self.frames:
            id = frame[0]
            start_time = frame[1]
            self._insert_into("frame", (id, start_time, self.path), batch=True)
        #humanInterface
        for path in os.listdir(inputImagesPath):
            value = os.path.basename(path)[0:-4]
            self._insert_into("humaninterface", (value, inputImagesPath))
        #usedAbility
        for path in os.listdir(usedAbilitiesPath):
            value = os.path.basename(path)[0:-4]
            self._insert_into("usedAbilityIcon", (value, usedAbilitiesPath))
        self.conn.commit()

    def remove_from(self, table, conditions):
        """

        :param table: string()
        :param conditions: dict()
        :return:
        """
        conditionsText = "DELETE  FROM {} WHERE "
        values = self.select_from(table, conditions=conditions)[0]
        self._insert_into(table+"_archive", values)
        for condition in conditions.keys():
            conditionsText += str(condition) + "=" + str(conditions[condition])
            if len(conditions.keys()) > 1:
                conditionsText += "AND"
        if "AND" in conditionsText:
            conditionsText = conditionsText[0:len(conditionsText)-5]
        conditionsText = conditionsText.format(table)
        self.c.execute(conditionsText)
        self.conn.commit()

    def select_from(self, table_name, columns="*", conditions=None):
        """

        :param table_name: String()
        :param columns:
        :param conditions: dict()
        :return:
        """

        if conditions is not None:
            conditionsText = "SELECT {} FROM {} WHERE "
            for condition in conditions.keys():
                if type(conditions[condition] == type(str())):
                    conditionsText += str(condition) + "=" + "\"" + conditions[condition]+ "\""
                else:
                    conditionsText += str(condition) + "=" + str(conditions[condition])
                if len(conditions.keys()) > 1:
                    conditionsText += " AND "
            if "AND" in conditionsText:
                conditionsText = conditionsText[0:len(conditionsText)-5]
            conditionsText = conditionsText.format(columns, table_name)
            return self.c.execute(conditionsText).fetchall()
        else:
            data = self.c.execute("SELECT {} FROM {}".format(columns, table_name)).fetchall()
            return data

    def remove_multi_a(self):
        clicks = self.select_from("click")
        i = 0
        while i < len(clicks)-1:
            click = clicks[i]
            next_click = clicks[i+1]
            if click[1] == 0x41 and next_click[1] == 0x41:

                self.remove_from("click", {"id": click[0]})
            i += 1

    def remove_click_a(self): # todo do a better job this can get rid of clicks that i want to keep
        clicks = self.select_from("click")
        i = 1
        while i < len(clicks)-1:
            previouse_click = clicks[i-1]
            click = clicks[i]
            next_click = clicks[i+1]
            if click[1] == 0x01 and next_click[1] == 0x41:
                # remove A
                self.remove_from("click", {"id": next_click[0]})
            i += 1

    def remove_double_leftClick(self):
        # todo this will remove a lot of useful data like shop items
        double_leftClick = self.find_double_clicks(1, value=1)
        for double in double_leftClick:
            self.remove_from("click", {"id": double[0][0]})

    def remove_on_cd(self):
        def img1_in_img2(img1, img2):
            """

            :param img1: Image()
            :param img2: Image()
            :return: Bool()
            """
            img1_list = list(img1.getdata())
            img2_list = list(img2.getdata())
            print(len(img1_list))
            return False
            # todo Finish this.
            # get a list for img1 and img2
            # then search the 2nd list for any occurrence of the first list

        icons = self.select_from("usedAbilityIcon")
        icon_dict = {}
        for icon in icons:
            img = Image.open(icon[2] + "/" + icon[1] + ".jpg")
            icon_dict[icon[1]] = img
        q_list = self.select_from("click", conditions={"event": "81"}) #finds all Q's
        for q in q_list:
            frame = self.select_from("frame", conditions={"id": str(q[8])})[0]
            img = Image.open(frame[2]+"/"+frame[0]+".jpg")
            icon_img = icon_dict["Q"]
            if img1_in_img2(icon_img,img):
                print("yes")

    def find_double_clicks(self, column, value="all"):
        clicks = self.select_from("click")
        double_clicks = []
        i = 0
        while i < len(clicks) - 1:
            click = clicks[i]
            next_click = clicks[i + 1]
            if value == "all":
                if click[column] == next_click[column]:
                    double_clicks.append((click, next_click))
                i += 1
            else:
                if click[column] == value:
                    if click[column] == next_click[column]:
                        double_clicks.append((click, next_click))
                i += 1
        return double_clicks


if __name__ == "__main__":
    path = "C:/Users/rambo/Desktop/SavedGames/Lucian00001Lost/"
    frame_path, screen_path, userInput_path = path + "frame.csv", path + "ScreenPan.csv", path + "input.csv"
    frames, pans, clicks = all_data(frame_path, screen_path, userInput_path)
    dataBase = DataBase(path, "Lucian00001Lost")
    humanInterfacePath = "C:/Users/rambo/OneDrive/Documents/Programming/Python/PycharmProjects/ML_Nick/Training/images/Human Interface"
    usedAbilitiesPath = "C:/Users/rambo/OneDrive/Documents/Programming/Python/PycharmProjects/ML_Nick/Training/images/icons"
    # dataBase.new(clicks, pans, frames, humanInterfacePath, usedAbilitiesPath)

    num_clicks = dataBase.select_from("click")
    # dataBase.remove_multi_a()
    # dataBase.remove_click_a()
    # dataBase.remove_double_leftClick()
    for frame, start_time, path in dataBase.select_from("frame"):
        print(frame, start_time, path)
    for key in RECORDED_KEYS.keys():
        print(key, RECORDED_KEYS[key])

    print(dataBase.remove_on_cd())

"""
    Trying to add new Table?
        create the table function
            def create_new_table_tableName(c)
        add it to the COLUMNS dictionary
        add it to DataBase.new()
        runDataBase.new(with the new table data)
        
    Trying to modify and existing Table?
        modify def create_table_tableName
        modify COLUMNS to match the new data
        run DataBase.new()
        
"""

