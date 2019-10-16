def firstWord(string):
    stringSplit = string.split(" ")
    return stringSplit[0]


def secondWord(string):
    stringSplit = string.split(" ")
    if len(stringSplit) >= 2:
        return stringSplit[1]
    else:
        return "-"


def withoutFirstWord(string):
    stringSplit = string.split(" ", 1)
    if len(stringSplit) >= 2:
        return stringSplit[1]
    else:
        return "too few args"


def withoutTwoFirstWords(string):
    stringSplit = string.split(" ", 2)
    if len(stringSplit) >= 3:
        return stringSplit[2]
    else:
        return "too few args"


def recvData(socket):
    return socket.recv(8192).decode()


def sendData(data, socket):
    data = data.encode()
    socket.send(data)
