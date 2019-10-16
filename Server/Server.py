import CommonFunctions

serverDomain = "AS-SERVER.DERBY.AC.UK"
clientDomain = ""
dataLast = ""
commandsUnimplemented = {"SOML", "SEND", "SAML", "TURN"}  # Set containing unimplemented commands.
commandsAnytime = {"NOOP", "EXPN", "VRFY", "HELP"}  # Set of commands that can be executed at any time.


def code211(socket):
    data = "General help reply here..."
    CommonFunctions.sendData(data, socket)
    # TODO: 211 used for HELP (no parameters)


def code214(socket):
    data = "Command X info..."
    CommonFunctions.sendData(data, socket)
    # TODO: 214 used for HELP (parameters)


def code220(socket):
    data = "220 " + serverDomain + " Simple Mail Transfer Service Ready"
    CommonFunctions.sendData(data, socket)


def code221(socket):
    data = "221 " + serverDomain + " Service closing transmission channel"
    CommonFunctions.sendData(data, socket)


def code250(socket, message):
    data = "250" + message
    CommonFunctions.sendData(data, socket)


def code251(socket, path):
    # path = <forward-path>
    data = "251 User not local; will forward to " + path
    CommonFunctions.sendData(data, socket)


def code354(socket):
    data = "354 Start mail input; end with <CRLF>.<CRLF>"
    CommonFunctions.sendData(data, socket)


def code421(socket):
    data = "421" + serverDomain + " Service not available, closing transmission channel"
    CommonFunctions.sendData(data, socket)


def code450(socket):
    data = "450 Requested mail action not taken: mailbox unavailable"
    # [E.g., mailbox busy]
    CommonFunctions.sendData(data, socket)


def code451(socket):
    data = "451 Requested action aborted: local error in processing"
    CommonFunctions.sendData(data, socket)


def code452(socket):
    data = "452 Requested action not taken: insufficient system storage"
    CommonFunctions.sendData(data, socket)


def code500(socket):
    data = "500 Syntax error, command unrecognized"
    # [This may include errors such as command line too long]
    CommonFunctions.sendData(data, socket)


def code501(socket):
    data = "501 Syntax error in parameters or arguments"
    CommonFunctions.sendData(data, socket)


def code502(socket):
    data = "502 Command not implemented"
    CommonFunctions.sendData(data, socket)


def code503(socket):
    data = "503 Bad sequence of commands"
    CommonFunctions.sendData(data, socket)


def code504(socket):
    data = "504 Command parameter not implemented"
    CommonFunctions.sendData(data, socket)


def code550(socket):
    data = "550 Requested action not taken: mailbox unavailable"
    # [E.g., mailbox not found, no access]
    CommonFunctions.sendData(data, socket)


def code551(socket, path):
    # path = <forward-path>
    data = "551 User not local; please try " + path
    CommonFunctions.sendData(data, socket)


def code552(socket):
    data = "552 Requested mail action aborted: exceeded storage allocation"
    CommonFunctions.sendData(data, socket)


def code553(socket):
    data = "553 Requested action not taken: mailbox name not allowed"
    # [E.g., mailbox syntax incorrect]
    CommonFunctions.sendData(data, socket)


def code554(socket):
    data = "554 Transaction failed"
    CommonFunctions.sendData(data, socket)


def commandHELO(socket):
    message = " " + serverDomain
    code250(socket, message)


def sequenceMAIL(socket):  # TODO THIS
    code250(socket, " TODO")


def commandRSET(socket):
    code250(socket, " OK")


def commandVRFY(socket):
    code250(socket, " TODO")


def commandEXPN(socket):
    code250(socket, " TODO")


def commandHELP(socket):
    code250(socket, " TODO")


def commandNOOP(socket):
    code250(socket, " TODO")


def commandQUIT(socket):
    code221(socket)


def commandRouter(dataEnc, socket):
    global dataLast
    dataLast = dataEnc.decode()
    command = CommonFunctions.firstWord(dataLast)
    commandW2 = CommonFunctions.secondWord(dataLast)
    if command in commandsUnimplemented:
        code502(socket)
    elif command in commandsAnytime:
        commandsAnytimeRouter(command, socket)
    elif command == "HELO":
        commandHELO(socket)
    elif command == "MAIL" and commandW2 == "FROM:":
        sequenceMAIL(socket)
    elif command == "QUIT":
        commandQUIT(socket)
    else:
        code500(socket)


def commandsAnytimeRouter(command, socket):
    if command == "VRFY":
        commandVRFY(socket)
    elif command == "EXPN":
        commandEXPN(socket)
    elif command == "HELP":
        commandHELP(socket)
    elif command == "NOOP":
        commandNOOP(socket)
    else:
        print("Wrong input")  # This would probably never occur due to the way the function is used.
