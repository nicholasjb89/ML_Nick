import pickle


def trainableData(rawInputData):
    """
    :param rawInputData: dict() the pickled data
    :return: list() ("w",position),("r",position),...)
    """
    usable_data = []
    skipped_first = False
    for k in rawInputData.keys():
        if not skipped_first:
            skipped_first = True
        else:
            data = rawInputData[k]
            #all the input data for x seconds seconds of gameplay
            keyboard = data[0]
            mouseclick = data[1][0]
            mousemove = data[1][1]
            for key in keyboard:
                button = key[0]
                the_time = key[1]
                mouse_position = mousePosAtKBrelease(key[1], mousemove, mouseclick)[0]

                picture_index = k
                usable_data.append([button, mouse_position, the_time, picture_index])
            for click in mouseclick:
                button = str(click[0])
                mouse_position = click[1]
                the_time = click[2]
                picture_index = k

                usable_data.append([button, mouse_position, the_time, picture_index])
    return usable_data


def mousePosAtKBrelease(time, mousemove, mouseclick):
    closets_position = None
    for event in mousemove:
        if closets_position is None:
            closets_position = event
        else:
            if abs(time - event[1]) < abs(time - closets_position[1]):
                closets_position = event

    for event in mouseclick:
        if abs(time - event[2]) < abs(time - closets_position[1]):
            closets_position = (event[1], event[2])

    return closets_position


if __name__ == "__main__":
    theFile = open("c:/Test/00003/input.txt", "br")
    inputData = pickle.load(theFile)
    theFile.close()

    user_input = trainableData(inputData)
    total_input = len(user_input)
    total_time = abs(user_input[0][2]-user_input[total_input-1][2])
    starting_time = user_input[0][2]
    avg_input_per_second = total_input/total_time

    fastest_input = None
    last_input = None
    for the_input in user_input:
        button = the_input[0]
        mouse_position = the_input[1]
        the_time = the_input[2]
        picture_index = the_input[3]
        #checks to see how fast 2 inputs came in (burst input)
        if last_input is None:
            last_input = the_input
            fastest_input = (user_input[0], 10000000)
        else:
            last_time = last_input[2]
            fastest_time_between_input = fastest_input[1]
            current_time_between_input = abs(last_time-the_time)
            if current_time_between_input == 0.0:
                print(last_input)
                print(the_input)
                print("-------------------") #toDo request human help when this happens for best results
            if current_time_between_input < fastest_time_between_input and current_time_between_input != 0.0:
                fastest_input = (the_input, current_time_between_input, last_input)
            last_input = the_input
    print("avg input per second:", avg_input_per_second)
    print("total:", total_input)
    print("total time:", total_time)
    print("fastest input:", fastest_input)
