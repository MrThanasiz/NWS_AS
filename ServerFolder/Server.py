import CommonFunctions
import SecurityServer
import Storage

serverDomain = "AS-SERVER.DERBY.AC.UK"
accountEmailRegistry = Storage.accountsLoad("Email")
accountUserRegistry = Storage.accountsLoad("User")
print("FILES LOADED")
commandsUnimplemented = {"SOML", "SEND", "SAML", "TURN"}  # Set containing unimplemented commands.
commandsAnytime = {"NOOP", "EXPN", "VRFY", "HELP", "QUIT"}  # Set of commands that can be executed at any time.
commandsImplemented = {"HELO","QUIT","MAIL FROM:","RCPT TO:","DATA","RSET","NOOP", "EXPN", "VRFY", "HELP","EHLO"}


class serverInstance:
    def __init__(self):
        self.state = "keyExchange"
        self.transferKey = 0
        self.secrServer = SecurityServer.securityServer()
        self.subStateMail = "init"
        self.mailFromBuffer = ""
        self.rcptBuffer = []
        self.dataBuffer = ""

    def commandRouter(self, dataEnc, socket):

        if self.state == "keyExchange":
            dataDec = dataEnc.decode()
            self.stateKeyExchange(dataDec, socket)

        elif self.state == "login":
            dataDec = self.secrServer.decryptData(dataEnc).decode()
            self.stateLogin(dataDec, socket)

        elif self.state == "default":
            dataDec = self.secrServer.decryptData(dataEnc).decode()
            self.stateDefault(dataDec, socket)

        elif self.state == "mail":
            dataDec = self.secrServer.decryptData(dataEnc).decode()
            self.stateMAIL(dataDec, socket)
        else:
            print("Command couldn't be routed")
            self.code421(socket)

    def stateKeyExchange(self, dataDec, socket):
        self.transferKey, completed = (self.secrServer.initiateKeyExchangeServer(dataDec, socket))
        if completed:
            self.state = "login"
            print(str(self.transferKey))

    def stateLogin(self, dataDec, socket):
        command = CommonFunctions.commandOnly(dataDec).upper()
        arguement = CommonFunctions.arguementOnly(dataDec)
        if (command == "REGISTER" or command == "LOGIN") and CommonFunctions.numberOfWords(arguement) == 2:
            userName = CommonFunctions.firstWord(arguement)
            userPass = CommonFunctions.secondWord(arguement)
            if len(userName) >= 6 and len(userPass) >= 6:
                if command == "REGISTER":
                    print("register") # TODO
                else:
                    print("login") # TODO
            else:
                self.code501(" Username and Password must be atleast 6 characters long")
        else:
            self.code501(" Available commands: \n"
                         "login <username> <password> \n"
                         "register <username> <password>", socket)

    def stateDefault(self, dataDec, socket):

        command = CommonFunctions.commandOnly(dataDec)
        arguement = CommonFunctions.arguementOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " Arguement:" + arguement)

        if command in commandsUnimplemented:
            self.code502(socket)
        elif command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, socket)
        elif command == "LOGOUT":
            self.state = "login"
        elif command == "HELO":
            self.commandHELO(socket)
        elif command == "MAIL FROM:":
            if arguement == "-":
                self.code501(" You need to specify the sender address.", socket)
            else:
                validity = CommonFunctions.mailValidation(arguement)
                if validity == "OK":
                    self.state = "mail"
                    self.subStateMail = "init"
                    self.sequenceMAIL(dataDec, socket)
                else:
                    self.code501(validity, socket)
        else:
            self.code500(socket)

    def stateMAIL(self, dataDec, socket):
        command = CommonFunctions.commandOnly(dataDec)
        arguement = CommonFunctions.arguementOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " Arguement:" + arguement)

        if self.subStateMail == "data":
            if dataDec == ".":
                for rcpt in self.rcptBuffer:
                    temp = Storage.email(self.mailFromBuffer, rcpt, self.dataBuffer)
                    temp.saveEmail()
                    self.commandRSET(socket)
            else:
                self.dataBuffer = self.dataBuffer + dataDec + "\n"
                self.code250(socket, " OK")

        elif command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, socket)

        elif command == "RSET":
            self.commandRSET()

        elif self.subStateMail == "init":
            self.mailFromBuffer = arguement[1:-1]
            self.subStateMail = "rcpt"
            self.code250(socket, " OK")

        elif self.subStateMail == "rcpt":
            if command == "RCPT TO:":
                validity = CommonFunctions.mailValidation(arguement)
                if validity == "OK":
                    self.rcptBuffer.append(arguement[1:-1])
                    self.code250(socket, " OK")
                else:
                    self.code553(validity, socket)
            elif command == "DATA":
                if len(self.rcptBuffer) == 0:
                    self.code503(socket)
                else:
                    self.subStateMail = "data"
                    self.code354(socket)
            else:
                self.code500(socket)


    def commandsAnytimeRouter(self, data, socket):
        command = CommonFunctions.commandOnly(data)
        arguement = CommonFunctions.arguementOnly(data)
        if command == "VRFY":
            if commandW2!="-" and CommonFunctions.numberOfWords(data)==2:
                self.commandVRFY(commandW2, socket)
            else:
                self.code501("", socket)
        elif command == "EXPN":
            self.commandEXPN(socket)
        elif command == "HELP":
            self.commandHELP(arguement, socket)
        elif command == "NOOP":
            self.commandNOOP(socket)
        elif command == "QUIT":
            self.commandQUIT(socket)
        else:
            print("Wrong input")  # This would probably never occur due to the way the function is used.


    def commandHELO(self, socket):
        message = " " + serverDomain
        self.code250(socket, message)


    def commandRSET(self, socket):
        self.state = "default"
        self.subStateMail = "init"
        self.mailFromBuffer = ""
        self.rcptBuffer = []
        self.dataBuffer = ""
        self.code250(socket, " OK")


    def commandVRFY(self, data, socket):
        global accountEmailRegistry
        data = Storage.commandVRFY(accountEmailRegistry, data)
        CommonFunctions.sendData(data, socket, self.secrServer)


    def commandEXPN(self, socket):
        self.code250(socket, " TODO commandexpn")


    def commandHELP(self, arguement, socket):
        command = arguement.upper()
        if command == "-":
            self.code211(socket)
        else:
            if command in commandsImplemented:
                self.code214(command,socket)
            else:
                self.code504(socket)


    def commandNOOP(self, socket):
        self.code250(socket, " OK")


    def commandQUIT(self, socket):
        self.code221(socket)
        socket.close()


    def code211(self, socket):
        data = "For more information on a specific command, type HELP command-name \n" \
               "HELO          Identifies the sender-SMTP to the receiver-SMTP. \n" \
               "QUIT          Specifies that the receiver must send an OK reply, and then close the transmission channel. \n" \
               "MAIL FROM:    Initiates outbound mail sequence.\n" \
               "RCPT TO:      Identifies a recipient in mail sequence.\n" \
               "DATA          Indicates mmail data in mail sequence.\n" \
               "HELP          Provides help information for SMTP commands.\n" \
               "RSET          Aborts a mail transaction.\n" \
               "VRFY          Verfies a username exists.\n" \
               "NOOP          No action other than to send send an OK reply to the receiver. \n" \
               "EXPN          Expands a mailing list.\n" \
               "EHLO          Same as HELO but tells the server that the client may want to use the Extended SMTP (ESMTP) protocol instead.\n"
        CommonFunctions.sendData(data, socket, self.secrServer)

    def code214(self, arguement, socket):
        if arguement == "HELO":
            data = "The HELO command is the command used by the host sending the command to identify itself; the command may be interpreted as saying \"Hello, I am <domain>\" \n" \
                   "USAGE: "
        elif arguement == "QUIT":
            data = "The QUIT command specifies that the receiver must send an OK reply, and then close the transmission channel. \n" \
                   "USAGE: "
        elif arguement == "MAIL FROM:":
            data = "The MAIL FROM: command is used to initiate a mail transaction in which the mail data is delivered to one or more mailboxes. The argument field contains a reverse-path. \n" \
                   "USAGE: "
        elif arguement == "RCPT TO:":
            data = "The RCPT TO: command is used to identify an individual recipient of the mail data; multiple recipients are specified by multiple use of this command."
        elif arguement == "DATA":
            data = "The DATA command causes the mail data from this command to be appended to the mail data buffer. The mail data may contain any of the 128 ASCII character codes. The mail data is terminated by a line containing only a period, that is the character sequence \"<CRLF>.<CRLF>\" \n" \
                   "USAGE: "
        elif arguement == "HELP":
            data = "The HELP command provides help information for SMTP commands, if used with a command returns information on that command. \n" \
                   "USAGE: "
        elif arguement == "RSET":
            data = "The RSET command specifies that the current mail transaction is to be aborted. Any stored sender, recipients, and mail data must be discarded, and all buffers and state tables cleared. The server will send an OK reply."
        elif arguement == "VRFY":
            data = "The VRFY command asks the receiver to confirm that the argument identifies a user. If it is a user name, the full name of the user (if known) and the fully specified mailbox are returned.  \n" \
                   "USAGE: "
        elif arguement == "NOOP":
            data = "The NOOP command does not affect any parameters or previously entered commands. It specifies no action other than that the receiver send an OK reply."
        elif arguement == "EXPN":
            data = "The EXPN command asks the receiver to confirm that the argument identifies a mailing list, and if so, to return the membership of that list. The full name of the users (if known) and the fully specified mailboxes are returned in a multiline reply. \n" \
                   "USAGE: "
        elif arguement == "EHLO":
            data = "Same as HELO but tells the server that the client may want to use the Extended SMTP (ESMTP) protocol instead.\n" \
                   "USAGE: "
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code220(self, socket):
        data = "220 " + serverDomain + " Simple Mail Transfer Service Ready"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code221(self, socket):
        data = "221 " + serverDomain + " Service closing transmission channel"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code250(self, socket, message):
        data = "250" + message
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code251(self, socket, path):
        # path = <forward-path>
        data = "251 User not local; will forward to " + path
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code354(self, socket):
        data = "354 Start mail input; end with <CRLF>.<CRLF>"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code421(self, socket):
        data = "421" + serverDomain + " Service not available, closing transmission channel"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code450(self, socket):
        data = "450 Requested mail action not taken: mailbox unavailable"
        # [E.g., mailbox busy]
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code451(self, socket):
        data = "451 Requested action aborted: local error in processing"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code452(self, socket):
        data = "452 Requested action not taken: insufficient system storage"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code500(self, socket):
        data = "500 Syntax error, command unrecognized"
        # [This may include errors such as command line too long]
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code501(self, message, socket):
        data = "501 Syntax error in parameters or arguments" + message
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code502(self, socket):
        data = "502 Command not implemented"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code503(self, socket):
        data = "503 Bad sequence of commands"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code504(self, socket):
        data = "504 Command parameter not implemented"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code550(self, socket):
        data = "550 Requested action not taken: mailbox unavailable"
        # [E.g., mailbox not found, no access]
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code551(self, socket, path):
        # path = <forward-path>
        data = "551 User not local; please try " + path
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code552(self, socket):
        data = "552 Requested mail action aborted: exceeded storage allocation"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code553(self, message, socket):
        data = "553 Requested action not taken: mailbox name not allowed" + message
        # [E.g., mailbox syntax incorrect]
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code554(self, socket):
        data = "554 Transaction failed"
        CommonFunctions.sendData(data, socket, self.secrServer)
