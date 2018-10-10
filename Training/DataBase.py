import sqlite3 as sql
from UsableEvents import default_convert, all_data, Click, Frame, ScreenPan

def create_table_click(c):
    c.execute("""CREATE TABLE IF NOT EXISTS click(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            event INTEGER,
            start_time INTEGER,
            mouse_position_press_x INTEGER,
            mouse_position_press_y INTEGER,
            mouse_position_release_x INTEGER,
            mouse_position_release_y INTEGER,
            total_time REAL,
            frame INTEGER
            )"""
              )

def create_table_screenPan(c):
    c.execute("""CREATE TABLE IF NOT EXISTS screenPan(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                start_time REAL,
                mouse_position_x INTEGER,
                mouse_position_y INTEGER,
                frame INTEGER)
                """
              )

def create_table_frame(c):
    c.execute("""CREATE TABLE IF NOT EXISTS frame(
                    id INTEGER PRIMARY KEY,
                    start_time REAL)
                   """
              )

class DataBase(object):
    def __init__(self, dbname):
        """

        :param clicks: list() (Click,...)
        :param pans: list() (Pans,...)
        :param frames: list() (list(),...)
        """
        conn = sql.connect(dbname+".db")
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        self.c = c
        self.conn = conn
    def new(self, clicks, pans, frames):
        create_table_screenPan(self.c)
        create_table_frame(self.c)
        create_table_click(self.c)
        self.clicks = clicks[1]
        self.clicks_columns = clicks[0]
        self.pans = pans[1]
        self.pans_columns = pans[0]
        self.frames = frames[1]
        self.frames_columns = frames[0]
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
            self.c.execute("INSERT INTO click (event, start_time, mouse_position_press_x,"
                           "mouse_position_press_y, mouse_position_release_x, mouse_position_release_y,"
                           "total_time,frame) VALUES (?,?,?,?,?,?,?,?)",
                           (event, start_time, mouse_position_press[0], mouse_position_press[1],
                            mouse_position_release[0], mouse_position_release[1], total_time, frame))
            self.conn.commit()

        for pan in self.pans:
            event = pan[0]
            mouse_x = pan[1]
            mouse_y = pan[2]
            time = pan[3]
            i = 0
            while self.frames[i][1] < time:
                i += 1
            frame = self.frames[i][0]
            self.c.execute(
                "INSERT INTO screenPan ( event, mouse_position_x, mouse_position_y, start_time, frame) VALUES (?,?,?,?,?)",
                (event, mouse_x, mouse_y, time, frame))
            self.conn.commit()

        for frame in self.frames:
            id = frame[0]
            start_time = frame[1]
            self.c.execute("INSERT INTO frame (id, start_time) VALUES (?, ?)", (id, start_time))
            self.conn.commit()

    def insert_into(self, table_name, data):
        pass

    def remove_from(self, table, conditions):
        """

        :param table: string()
        :param conditions: dict()
        :return:
        """
        self.c.execute("DELETE FROM {} WHERE ") #todo Finish this

    def select_from(self, table_name, columns="*"):
        return self.c.execute("SELECT {} FROM {}".format(columns, table_name)).fetchall()# not a great way of doing it

frame_path, screen_path, userInput_path = "c:/Test/00002/frame.csv", "c:/Test/00002/ScreenPan.csv", "c:/Test/00002/input.csv"
frames, pans, clicks = all_data(frame_path, screen_path, userInput_path)
dataBase = DataBase("Lucian00002")
for row in dataBase.select_from("click"):
    print(row)
