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

# The 2 following functions are used to separate the command from the argument.


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


def argumentOnly(string):
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


def mailValidationSMTP(argument):
    if argument[0] == "<" and argument[-1] == ">":
        argument = argument[1:-1]
        return mailValidation(argument)
    else:
        return "Mail address must be enclosed in \"< >\" "


def mailValidation(argument):
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.@"
    argument = argument.split("@")
    if len(argument) == 2:
        if all(char in charset for char in argument[0]):
            if len(argument[1].split(".")) >1:
                return "OK"
            else:
                return "Domain name must include atleast 1 period (.)"
        else:
            return "Sorry, only letters (a-Z), numbers (0-9), and periods (.) are allowed."
    else:
        return "There must be exactly 1 at symbol (@) in the address"


def userpassValidate(argument):
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-=_+,.?"
    if all(char in charset for char in argument) and len(argument) >=6:
        return True
    else:
        return False


def sendDataKeyExchange(data, module):
    data = data.encode()
    module._send_data(data)


def sendData(data, module, SecurityServer):  # This command is used to send data while not in the KeyExchange state.
    data = data.encode()
    data = SecurityServer.encryptData(data)
    module._send_data(data)


def decryptData(data, SecurityServer):
    return SecurityServer.decryptData(data)
