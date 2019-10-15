import CommonFunctions

serverDomain = "AS-SERVER.DERBY.AC.UK"


def code211(socket):
    data = "General help reply here..."
    sendData(data, socket)
    # TODO: 211 used for HELP (no parameters)


def code214(socket):
    data = "Command X info..."
    sendData(data, socket)
    # TODO: 214 used for HELP (parameters)


def code220(socket):
    data = "220 " + serverDomain + " Simple Mail Transfer Service Ready"
    sendData(data, socket)


def code221(socket):
    data = "221 " + serverDomain + " Service closing transmission channel"
    sendData(data, socket)


def code250(socket, message):
    data = "250" + message
    sendData(data, socket)


def code251(socket, path):
    # path = <forward-path>
    data = "251 User not local; will forward to " + path
    sendData(data, socket)


def code354(socket):
    data = "354 Start mail input; end with <CRLF>.<CRLF>"
    sendData(data, socket)


def code421(socket):
    data = "421" + serverDomain + " Service not available, closing transmission channel"
    sendData(data, socket)


def code450(socket):
    data = "450 Requested mail action not taken: mailbox unavailable"
    # [E.g., mailbox busy]
    sendData(data, socket)


def code451(socket):
    data = "451 Requested action aborted: local error in processing"
    sendData(data, socket)


def code452(socket):
    data = "452 Requested action not taken: insufficient system storage"
    sendData(data, socket)


def code500(socket):
    data = "500 Syntax error, command unrecognized"
    # [This may include errors such as command line too long]
    sendData(data, socket)


def code501(socket):
    data = "501 Syntax error in parameters or arguments"
    sendData(data, socket)


def code502(socket):
    data = "502 Command not implemented"
    sendData(data, socket)


def code503(socket):
    data = "503 Bad sequence of commands"
    sendData(data, socket)


def code504(socket):
    data = "504 Command parameter not implemented"
    sendData(data, socket)


def code550(socket):
    data = "550 Requested action not taken: mailbox unavailable"
    # [E.g., mailbox not found, no access]
    sendData(data, socket)


def code551(socket, path):
    # path = <forward-path>
    data = "551 User not local; please try " + path
    sendData(data, socket)


def code552(socket):
    data = "552 Requested mail action aborted: exceeded storage allocation"
    sendData(data, socket)


def code553(socket):
    data = "553 Requested action not taken: mailbox name not allowed"
    # [E.g., mailbox syntax incorrect]
    sendData(data, socket)


def code554(socket):
    data = "554 Transaction failed"
    sendData(data, socket)


def sendData(data, socket):
    data = data.encode()
    socket.send(data)


def commandRouter(data, socket):
    data = data.decode()
    command = CommonFunctions.firstWord(data)
    commandW2 = CommonFunctions.secondWord(data)
    cniSet={"SOML","SEND","SAML","TURN"}  # Set containing unimplemented commands.
    if command in cniSet:
        code502(socket)
    elif command == "HELO":
        commandHELO(socket)
    elif command == "MAIL" and commandW2 == "TO":
        sequenceMAIL(socket)
    elif command == "VRFY":
        commandVRFY(socket)
    elif command == "EXPN":
        commandEXPN(socket)
    elif command == "HELP":
        commandHELP(socket)
    elif command == "NOOP":
        commandNOOP(socket)
    elif command == "QUIT":
        commandQUIT(socket)
    else:
        code500(socket)


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
