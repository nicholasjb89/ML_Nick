from DataBase import DataBase, RECORDED_KEYS
from PIL import ImageGrab, Image, ImageFile

import os
def generate_event_images(path,savepath, dbName):
    """

    :param path: str() that all the data is in
    :param savepath: the new path for the images
    :return:
    """
    frame_path, screen_path, userInput_path = path+"frame.csv", path+"ScreenPan.csv", path+"input.csv"
    dataBase = DataBase(dbName)
    event_images = dataBase.select_from("humaninterface")
    for id, start_time in dataBase.select_from("frame"):
        print(id)
        with Image.open(path+str(id)+".jpg", "r") as img:
            new_img = Image.new("L", img.size)
            new_img.paste(img)
            clicks = dataBase.select_from("click", conditions={"frame": id})
            for click in clicks:
                event = RECORDED_KEYS[click[1]]
                for event_image in event_images:
                    if event_image[1] == event:
                        event_path = event_image[2] + "/" +  event_image[1] + ".jpg"
                        with Image.open(event_path) as event_img:
                            new_img.paste(event_img, (click[3], click[4]))
            pans = dataBase.select_from("screenPan", conditions={"frame": id})
            for pan in pans:
                for event_image in event_images:
                    if event_image[1].lower() == pan[1].lower():
                        event_path = event_image[2] + "/" + event_image[1] + ".jpg"
                        with Image.open(event_path) as event_img:
                            if pan[1].lower() == "rightpan":
                                if pan[4] + event_img.size[1] > new_img.size[1]:
                                    y = new_img.size[1] - event_img.size[1]
                                else:
                                    y = pan[4]
                                new_img.paste(event_img, (pan[3]-event_img.size[0], y))

                            elif pan[1].lower() == "downpan":
                                if pan[3] + event_img.size[0] > new_img.size[0]:
                                    x = new_img.size[0] - event_img.size[0]
                                else:
                                    x = pan[3]
                                new_img.paste(event_img, (x, pan[4] - event_img.size[1]))

                            else:
                                new_img.paste(event_img, (pan[3], pan[4]))
            new_img.save(savepath + id + ".jpg")


# def watch(path):
#     """
#     this will show the images in the path specified, It can only use .jpg files
#     :param path: string() the path to the folder with images in it
#     :return: None
#     """
#
#     for file_path in os.listdir(path):
#         img = Image.open(path+"/"+file_path)

if __name__ == "__main__":
    dbName = "Lucian00010Lost"
    path = "C:/Test/Lucian00010Lost/"
    generate_event_images(path, "C:/Users/rambo/Desktop/test/", dbName)

    # watch("C:/Users/rambo/Desktop/test")
