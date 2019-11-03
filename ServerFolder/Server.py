import CommonFunctions
import SecurityServer
import Storage
import Auditing
import time

serverDomain = "AS-SERVER.DERBY.AC.UK"
accountEmailRegistry = Storage.accountsLoad("Email")
accountUserRegistry = Storage.accountsLoad("User")
emailListRegistry = Storage.accountsLoad("MailList")
print("FILES LOADED")
commandsUnimplemented = {"SOML", "SEND", "SAML", "TURN"}  # Set containing unimplemented commands.
commandsAnytime = {"NOOP", "EXPN", "VRFY", "HELP", "QUIT"}  # Set of commands that can be executed at any time.
commandsImplemented = {"HELO","QUIT","MAIL FROM:","RCPT TO:","DATA","RSET","NOOP", "EXPN", "VRFY", "HELP","EHLO"}
 # primary use of commandsImplemented is for the command help


class serverInstance:
    def __init__(self):
        self.state = "keyExchange"
        self.transferKey = 0
        self.secrServer = SecurityServer.securityServer()
        self.subStateMail = "init"
        self.mailFromBuffer = ""
        self.rcptBuffer = []
        self.dataBuffer = ""
        self.clientDomain = "-"
        self.currentUser = []

    def commandRouter(self, dataEnc, socket):

        if self.state == "keyExchange":
            dataDec = dataEnc.decode()
            self.stateKeyExchange(dataDec, socket)

        elif self.state == "login":
            dataDec = self.secrServer.decryptData(dataEnc).decode()
            self.stateLogin(dataDec, socket)

        elif self.state == "greetings":
            dataDec = self.secrServer.decryptData(dataEnc).decode()
            self.stateGreetings(dataDec, socket)

        elif self.state == "default":
            dataDec = self.secrServer.decryptData(dataEnc).decode()
            self.stateDefault(dataDec, socket)

        elif self.state == "mail":
            dataDec = self.secrServer.decryptData(dataEnc).decode()
            self.stateMail(dataDec, socket)
        else:
            print("Command couldn't be routed state unknown")
            self.code421(socket)

    def stateKeyExchange(self, dataDec, socket):
        self.transferKey, completed = (self.secrServer.initiateKeyExchangeServer(dataDec, socket))
        if completed:
            self.state = "login"
            print(str(self.transferKey))

    def stateLogin(self, dataDec, socket):
        command = CommonFunctions.commandOnly(dataDec).upper()
        argument = CommonFunctions.argumentOnly(dataDec)
        if (command == "REGISTER" or command == "LOGIN") and CommonFunctions.numberOfWords(argument) == 2:
            userName = CommonFunctions.firstWord(argument)
            userPass = CommonFunctions.secondWord(argument)
            if CommonFunctions.userpassValidate(userName) and CommonFunctions.userpassValidate(userPass):
                if command == "REGISTER":
                    self.commandREGISTER(argument, socket)
                else:
                    self.commandLOGIN(argument, socket)
            else:
                self.code503(" Username and Password must be atleast 6 characters long and CAN contain numbers, letters including the following symbols !@#$%^&*()-=_+,.?", socket)
        else:
            self.code501(" Available commands: \n"
                         "login <username> <password> \n"
                         "register <username> <password>", socket)

    def stateGreetings(self, dataDec, socket):

        command = CommonFunctions.commandOnly(dataDec)
        argument = CommonFunctions.argumentOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " argument:" + argument)

        if command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, socket)
        elif command == "HELO":
            self.commandHELO(argument, socket)
        elif command == "EHLO":
            self.commandEHLO(argument, socket)
        elif command in commandsImplemented:
            self.code503("", socket)
        else:
            self.code500(socket)
        if self.clientDomain != "-":
            self.state = "default"

    def stateDefault(self, dataDec, socket):

        command = CommonFunctions.commandOnly(dataDec)
        argument = CommonFunctions.argumentOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " argument:" + argument)

        if command in commandsUnimplemented:
            self.code502(socket)
        elif command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, socket)
        elif command == "LOGOUT":
            self.commandLOGOUT(socket)
        elif command == "REGMAIL":
            self.commandREGMAIL(argument, socket)
        elif command == "ADDMAIL":
            self.commandADDMAIL(argument, socket)
        elif command == "RMVMAIL":
            self.commandRMVMAIL(argument, socket)
        elif command == "HELO":
            self.commandHELO(argument, socket)
        elif command == "EHLO":
            self.commandEHLO(argument, socket)
        elif command == "MAIL FROM:":
            self.commandMAIL(argument, socket)
        else:
            self.code500(socket)

    def stateMail(self, dataDec, socket):
        command = CommonFunctions.commandOnly(dataDec)
        argument = CommonFunctions.argumentOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " argument:" + argument)

        if self.subStateMail == "data":
            if dataDec == ".":
                for rcpt in self.rcptBuffer:
                    temp = Storage.email(self.mailFromBuffer, rcpt, self.dataBuffer)
                    temp.saveEmail()
                    Auditing.logMail(self.mailFromBuffer, rcpt)
                self.commandRSET(socket)
            else:
                if dataDec[0] == ".":
                    dataDec = dataDec[1:]
                self.dataBuffer = self.dataBuffer + dataDec + "\n"
                self.code250(" OK", socket)

        elif command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, socket)

        elif command == "RSET":
            self.commandRSET()

        elif self.subStateMail == "init":
            self.mailFromBuffer = argument[1:-1]
            self.subStateMail = "rcpt"
            self.code250(" OK", socket)

        elif self.subStateMail == "rcpt":
            if command == "RCPT TO:":
                validity = CommonFunctions.mailValidation(argument)
                if validity == "OK":
                    self.rcptBuffer.append(argument[1:-1])
                    self.code250(" OK", socket)
                else:
                    self.code553(validity, socket)
            elif command == "DATA":
                if len(self.rcptBuffer) == 0:
                    self.code503("", socket)
                else:
                    self.subStateMail = "data"
                    self.code354(socket)
            else:
                self.code500(socket)


    def commandsAnytimeRouter(self, data, socket):
        command = CommonFunctions.commandOnly(data)
        argument = CommonFunctions.argumentOnly(data)
        if command == "VRFY":
            self.commandVRFY(argument, socket)
        elif command == "EXPN":
            self.commandEXPN(argument, socket)
        elif command == "HELP":
            self.commandHELP(argument, socket)
        elif command == "NOOP":
            self.commandNOOP(socket)
        elif command == "QUIT":
            self.commandQUIT(socket)
        else:
            print("Wrong input")  # This would probably never occur due to the way the function is used.

    def commandREGISTER(self, argument, socket):
        userName = CommonFunctions.firstWord(argument)
        userPass = CommonFunctions.secondWord(argument)
        hashedPassword, salt = SecurityServer.hashPW(userPass)
        tuser = Storage.accountUser(userName, hashedPassword, salt, [])
        global accountUserRegistry
        Storage.accountAdd(accountUserRegistry, tuser)
        Storage.accountsSave(accountUserRegistry, "User")
        self.code250(" Account Registered Successfuly, Log in.", socket)


    def commandLOGIN(self, argument, socket):
        userName = CommonFunctions.firstWord(argument)
        userPass = CommonFunctions.secondWord(argument)
        global accountUserRegistry
        if Storage.accountValidateLogin(accountUserRegistry, userName, userPass):
            self.currentUser = Storage.accountGet(accountUserRegistry, userName)
            self.state = "greetings"
            Auditing.logLoginAttempt(userName,True)
            self.code250(" Logged in successfully", socket)
        else:
            Auditing.logLoginAttempt(userName, False)
            self.code554(", username password pair doesn't exist, try again.", socket)



    def commandLOGOUT(self, socket):
        self.state = "login"
        self.currentUser = []
        self.clientDomain = "-"
        self.code250(" Logged out successfully", socket)

    def commandMAIL(self, argument, socket):
        if argument == "-":
            self.code501(" You need to specify the sender address.", socket)
        else:
            validity = CommonFunctions.mailValidation(argument)
            if validity == "OK":
                self.state = "mail"
                self.subStateMail = "init"
                self.sequenceMAIL(dataDec, socket)
            else:
                self.code501(validity, socket)

    def commandHELO(self, argument, socket):
        self.clientDomain = argument
        message = " " + serverDomain
        self.code250(message, socket)

    def commandEHLO(self, argument, socket):
        self.clientDomain = argument
        message = "-" + serverDomain + " Hello " + self.clientDomain
        self.code250(message, socket)
        time.sleep(0.05)
        message = "-LOGOUT"
        self.code250(message, socket)
        time.sleep(0.05)
        message = "-MMAN"
        self.code250(message, socket)
        time.sleep(0.05)
        message = "-EXPN"
        self.code250(message, socket)
        time.sleep(0.05)
        message = "-VRFY"
        self.code250(message, socket)
        time.sleep(0.05)
        message = "-REGMAIL"
        self.code250(message, socket)
        time.sleep(0.05)
        message = "-ADDMAIL"
        self.code250(message, socket)
        time.sleep(0.05)
        message = "-RMVMAIL"
        self.code250(message, socket)
        time.sleep(0.05)
        self.commandRSET(socket)


    def commandRSET(self, socket):
        if self.state != "greetings":
            self.state = "default"
            self.subStateMail = "init"
            self.mailFromBuffer = ""
            self.rcptBuffer = []
            self.dataBuffer = ""
        self.code250(" OK", socket)



    def commandVRFY(self, argument, socket):
        if argument != "-" and CommonFunctions.numberOfWords(data) == 2:
            global accountEmailRegistry
            data = Storage.commandVRFY(accountEmailRegistry, argument)
            CommonFunctions.sendData(data, socket, self.secrServer)
        else:
            self.code501("", socket)


    def commandEXPN(self, argument, socket):
        if self.clientDomain == "-":
            self.code550(" No access", socket)
        else:
            if Storage.accountExists(emailListRegistry, argument):
                mailList = Storage.accountSearch(emailListRegistry, argument)
                for i in range(len(mailingList.mailList) - 1):
                    self.code250("-" + mailingList.mailList[i], socket)
                self.code250(" " + mailingList.mailList[-1], socket)
            else:
                self.code550(" List not found", socket)


    def commandHELP(self, argument, socket):
        command = argument.upper()
        if command == "-":
            self.code211(socket)
        else:
            if command in commandsImplemented:
                self.code214(command,socket)
            else:
                self.code504(socket)


    def commandNOOP(self, socket):
        self.code250(" OK", socket)


    def commandQUIT(self, socket):
        self.code221(socket)
        socket.close()

    def commandREGMAIL(self, argument, socket):
        address = CommonFunctions.firstWord(argument)
        addressPass = CommonFunctions.secondWord(argument)
        mailValid = CommonFunctions.mailValidation(address)
        if mailValid == "OK":
            if CommonFunctions.userpassValidate(addressPass):
                userName = CommonFunctions.firstWord(argument)
                userPass = CommonFunctions.secondWord(argument)
                hashedPassword, salt = SecurityServer.hashPW(userPass)
                tmail = Storage.accountEmail(address, hashedPassword, salt)
                global accountEmailRegistry
                Storage.accountAdd(accountEmailRegistry, tmail)
                Storage.accountsSave(accountEmailRegistry, "Email")
                self.code250(" Email Account Registered Successfuly. Don't forget to add it to your User Account", socket)
            else:
                self.code503(" Password must be atleast 6 characters long and CAN contain numbers, letters including the following symbols !@#$%^&*()-=_+,.?", socket)
        else:
            self.code501(mailValid, socket)
    def commandADDMAIL(self, argument, socket):
        address = CommonFunctions.firstWord(argument)
        addressPass = CommonFunctions.secondWord(argument)
        mailValid = CommonFunctions.mailValidation(address)
        if mailValid == "OK":
            if CommonFunctions.userpassValidate(addressPass):
                global accountEmailRegistry
                if Storage.accountValidateLogin(accountEmailRegistry, address, addressPass):
                    Storage.accountUserEmailAdd(accountUserRegistry, self.currentUser.getIdentifier(), address)
                    Storage.accountsSave(accountUserRegistry, "User")
                    self.code250(" Email added successfully", socket)
                else:
                    self.code550(" Email Password pair doesn't match anything.", socket)
            else:
                self.code503(" Password must be atleast 6 characters long and CAN contain numbers, letters including the following symbols !@#$%^&*()-=_+,.?", socket)
        else:
            self.code501(", " + mailValid, socket)

    def commandRMVMAIL(self, argument, socket):
        address = argument
        mailValid = CommonFunctions.mailValidation(address)
        if mailValid == "OK":
                global accountEmailRegistry
                if Storage.accountUserEmailExists(accountUserRegistry, self.currentUser.getIdentifier(), address):
                    Storage.accountUserEmailRemove(accountUserRegistry, self.currentUser.getIdentifier(), address)
                    Storage.accountsSave(accountUserRegistry, "User")
                    self.code250(" Email removed successfully", socket)
                else:
                    self.code550(" Email not in current users emails.", socket)
        else:
            self.code501(mailValid, socket)

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

    def code214(self, argument, socket):
        if argument == "HELO":
            data = "The HELO command is the command used by the host sending the command to identify itself; the command may be interpreted as saying \"Hello, I am <domain>\" \n" \
                   "USAGE: "
        elif argument == "QUIT":
            data = "The QUIT command specifies that the receiver must send an OK reply, and then close the transmission channel. \n" \
                   "USAGE: "
        elif argument == "MAIL FROM:":
            data = "The MAIL FROM: command is used to initiate a mail transaction in which the mail data is delivered to one or more mailboxes. The argument field contains a reverse-path. \n" \
                   "USAGE: "
        elif argument == "RCPT TO:":
            data = "The RCPT TO: command is used to identify an individual recipient of the mail data; multiple recipients are specified by multiple use of this command."
        elif argument == "DATA":
            data = "The DATA command causes the mail data from this command to be appended to the mail data buffer. The mail data may contain any of the 128 ASCII character codes. The mail data is terminated by a line containing only a period, that is the character sequence \"<CRLF>.<CRLF>\" \n" \
                   "USAGE: "
        elif argument == "HELP":
            data = "The HELP command provides help information for SMTP commands, if used with a command returns information on that command. \n" \
                   "USAGE: "
        elif argument == "RSET":
            data = "The RSET command specifies that the current mail transaction is to be aborted. Any stored sender, recipients, and mail data must be discarded, and all buffers and state tables cleared. The server will send an OK reply."
        elif argument == "VRFY":
            data = "The VRFY command asks the receiver to confirm that the argument identifies a user. If it is a user name, the full name of the user (if known) and the fully specified mailbox are returned.  \n" \
                   "USAGE: "
        elif argument == "NOOP":
            data = "The NOOP command does not affect any parameters or previously entered commands. It specifies no action other than that the receiver send an OK reply."
        elif argument == "EXPN":
            data = "The EXPN command asks the receiver to confirm that the argument identifies a mailing list, and if so, to return the membership of that list. The full name of the users (if known) and the fully specified mailboxes are returned in a multiline reply. \n" \
                   "USAGE: "
        elif argument == "EHLO":
            data = "Same as HELO but tells the server that the client may want to use the Extended SMTP (ESMTP) protocol instead.\n" \
                   "USAGE: "
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code220(self, socket):
        data = "220 " + serverDomain + " Simple Mail Transfer Service Ready"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code221(self, socket):
        data = "221 " + serverDomain + " Service closing transmission channel"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code250(self, message, socket):
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


    def code503(self, message, socket):
        data = "503 Bad sequence of commands" + message
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code504(self, socket):
        data = "504 Command parameter not implemented"
        CommonFunctions.sendData(data, socket, self.secrServer)


    def code550(self, message, socket):
        data = "550 Requested action not taken: mailbox unavailable" + message
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


    def code554(self, message, socket):
        data = "554 Transaction failed" + message
        CommonFunctions.sendData(data, socket, self.secrServer)
