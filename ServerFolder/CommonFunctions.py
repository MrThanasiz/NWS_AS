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
    word1 = firstWord(string).upper()
    word2 = secondWord(string).upper()
    if word1 == "MAIL" and word2 == "FROM:":
        commandOnly = "MAIL FROM:"
    elif word1 == "RCPT" and word2 == "TO:":
        commandOnly = "RCPT TO:"
    else:
        commandOnly = word1
    return commandOnly


def arguementOnly(string):
    word1 = firstWord(string)
    word2 = secondWord(string)
    if (word1.upper() == "MAIL" and word2.upper() == "FROM:") or (word1.upper() == "RCPT" and word2.upper() == "TO:"):
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

def mailValidation(arguement):
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.@"

    if arguement[0] == "<" and arguement[-1] == ">":
        arguement = arguement[1:-1]
        arguement = arguement.split("@")
        if len(arguement) == 2:
            if all(char in charset for char in arguement[0]):
                if len(arguement[1].split(".")) >1:
                    return "OK"
                else:
                    return "Domain name must include atleast 1 period (.)"
            else:
                return "Sorry, only letters (a-Z), numbers (0-9), and periods (.) are allowed."
        else:
            return "There must be exactly 1 at symbol (@) in the address"
    else:
        return "Sender address must be enclosed in \"< >\" "


def userpassValidate(arguement):
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()[]{}-=_+,./<>?|"
    if all(char in charset for char in arguement[0]):
        return True
    else:
        return False

def sendDataKeyExchange(data, socket):
    data = data.encode()
    socket.send(data)


def sendData(data, socket, SecrServer):
    data = data.encode()
    data = SecrServer.encryptData(data)
    socket.send(data)


def decryptData(data, SecServ):
    return SecServ.decryptData(data)
