from DataBase import DataBase, RECORDED_KEYS
from PIL import ImageGrab, Image, ImageFile

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
            clicks = dataBase.select_from("click", conditions={"frame": id})
            new_img = Image.new("L", img.size)
            new_img.paste(img)
            for click in clicks:
                event = RECORDED_KEYS[click[1]]
                for event_image in event_images:
                    if event_image[1] == event:
                        event_path = event_image[2] + "/" +  event_image[1] + ".jpg"
                        with Image.open(event_path) as event_img:
                            new_img.paste(event_img,(click[3], click[4]))
            new_img.save(savepath + id + ".jpg")


if __name__ == "__main__":
    dbName = "Lucian00010Lost"
    path = "C:/Test/Lucian00010Lost/"
    generate_event_images(path, "C:/Users/rambo/Desktop/test/", dbName)
