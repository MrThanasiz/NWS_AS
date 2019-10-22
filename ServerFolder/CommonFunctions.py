import SecurityServer

def numberOfWords(string):
    stringSplit = string.split(" ")
    return len(stringSplit)

def firstWord(string):
    stringSplit = string.split(" ")
    return stringSplit[0]


def secondWord(string):
    stringSplit = string.split(" ")
    if len(stringSplit) >= 2:
        return stringSplit[1]
    else:
        return "-"

def commandOnly(string):
    word1 = firstWord(string)
    word2 = secondWord(string)
    if word1 == "MAIL" and word2 == "FROM:":
        commandOnly = "MAIL FROM:"
    elif word1 == "RCPT" and word == "TO:":
        commandOnly = "RCPT TO:"
    else:
        commandOnly = word1
    return commandOnly


def arguementOnly(string):
    word1 = firstWord(string)
    word2 = secondWord(string)
    if (word1 == "MAIL" and word2 == "FROM:") or (word1 == "RCPT" and word == "TO:"):
        stringSplit = string.split(" ", 2)
        if len(stringSplit) == 3:
            return stringSplit[2]
        else:
            return "-"
    elif word2 == "-":
        return "-"
    else:
        stringSplit = string.split(" ", 1)
        return stringSplit[1]


def withoutTwoFirstWords(string):
    stringSplit = string.split(" ", 2)
    if len(stringSplit) >= 3:
        return stringSplit[2]
    else:
        return "too few args"


def sendDataKeyExchange(data, socket):
    data = data.encode()
    socket.send(data)


def sendData(data, socket, SecrServer):
    data = data.encode()
    data = SecrServer.encryptData(data)
    socket.send(data)


def decryptData(data, SecServ):
    return SecServ.decryptData(data)
