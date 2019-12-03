import CommonFunctions
import SecurityServer
import Storage
import Auditing
import time

serverDomain = "AS-SERVER.DERBY.AC.UK"
commandsUnimplemented = {"SOML", "SEND", "SAML", "TURN"}  # Set containing unimplemented commands.
commandsAnytime = {"NOOP", "EXPN", "VRFY", "HELP", "QUIT"}  # Set of commands that can be executed at any time.
commandsImplemented = {"HELO", "QUIT", "MAIL FROM:", "RCPT TO:", "DATA", "RSET", "NOOP", "EXPN", "VRFY", "HELP",
                       "EHLO", "ADDMAIL", "REGMAIL", "RMVMAIL", "MYMAILS", "LISTMAIL", "VIEWMAIL", "DELMAIL"}
# primary use of commandsImplemented is for the command help


class responseProcessor:
    def __init__(self):
        self.state = "keyExchange"
        self.transferKey = 0
        self.securityServer = SecurityServer.securityServer()

        self.accountEmailRegistry = Storage.accountsLoad("Email")
        self.accountUserRegistry = Storage.accountsLoad("User")
        self.emailListRegistry = Storage.accountsLoad("MailList")

        print("FILES LOADED")
        self.subStateMail = "init"
        self.mailFromBuffer = ""
        self.rcptBuffer = []
        self.dataBuffer = ""
        self.clientDomain = "-"
        self.currentUser = []

    def commandRouter(self, dataEnc, module):

        if self.state == "keyExchange":
            dataDec = dataEnc.decode()
            self.stateKeyExchange(dataDec, module)

        elif self.state == "login":
            dataDec = self.securityServer.decryptData(dataEnc).decode()
            self.stateLogin(dataDec, module)

        elif self.state == "greetings":
            dataDec = self.securityServer.decryptData(dataEnc).decode()
            self.stateGreetings(dataDec, module)

        elif self.state == "default":
            dataDec = self.securityServer.decryptData(dataEnc).decode()
            self.stateDefault(dataDec, module)

        elif self.state == "mail":
            dataDec = self.securityServer.decryptData(dataEnc).decode()
            self.stateMail(dataDec, module)
        else:
            print("Command couldn't be routed state unknown")
            self.code421(module)

    def stateKeyExchange(self, dataDec, module):
        self.transferKey, completed = (self.securityServer.initiateKeyExchangeServer(dataDec, module))
        if completed:
            self.state = "login"
            print(str(self.transferKey))

    def stateLogin(self, dataDec, module):
        command = CommonFunctions.commandOnly(dataDec).upper()
        argument = CommonFunctions.argumentOnly(dataDec)
        if (command == "REGISTER" or command == "LOGIN") and CommonFunctions.numberOfWords(argument) == 2:
            userName = CommonFunctions.firstWord(argument)
            userPass = CommonFunctions.secondWord(argument)
            if CommonFunctions.userpassValidate(userName) and CommonFunctions.userpassValidate(userPass):
                if command == "REGISTER":
                    self.commandREGISTER(argument, module)
                else:
                    self.commandLOGIN(argument, module)
            else:
                self.code503(" Username and Password must be atleast 6 characters long and CAN contain numbers, letters including the following symbols !@#$%^&*()-=_+,.?", module)
        else:
            self.code501(" Available commands: \n"
                         "login <username> <password> \n"
                         "register <username> <password>", module)

    def stateGreetings(self, dataDec, module):

        command = CommonFunctions.commandOnly(dataDec)
        argument = CommonFunctions.argumentOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " argument:" + argument)

        if command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, module)
        elif command == "HELO":
            self.commandHELO(argument, module)
        elif command == "EHLO":
            self.commandEHLO(argument, module)
        elif command in commandsImplemented:
            self.code503("", module)
        else:
            self.code500(module)
        if self.clientDomain != "-":
            self.state = "default"

    def stateDefault(self, dataDec, module):

        command = CommonFunctions.commandOnly(dataDec)
        argument = CommonFunctions.argumentOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " argument:" + argument)

        if command in commandsUnimplemented:
            self.code502(module)
        elif command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, module)
        elif command == "LOGOUT":
            self.commandLOGOUT(module)
        elif command == "REGMAIL":
            self.commandREGMAIL(argument, module)
        elif command == "ADDMAIL":
            self.commandADDMAIL(argument, module)
        elif command == "RMVMAIL":
            self.commandRMVMAIL(argument, module)
        elif command == "MYMAILS":
            self.commandMYMAILS(module)
        elif command == "LISTMAIL":
            self.commandLISTMAIL(module)
        elif command == "VIEWMAIL":
            self.commandVIEWMAIL(argument, module)
        elif command == "DELMAIL":
            self.commandDELMAIL(argument, module)
        elif command == "MAIL":  # added so that if its just mail and from is missing it throws a 501 error
            self.code501(" valid parameter is FROM:", module)
        elif command == "MAIL FROM:":
            self.commandMAIL(dataDec, module)
        else:
            self.code500(module)

    def stateMail(self, dataDec, module):
        command = CommonFunctions.commandOnly(dataDec)
        argument = CommonFunctions.argumentOnly(dataDec)
        print("State:" + self.state + " Data:" + dataDec + " Command:" + command + " argument:" + argument)

        if self.subStateMail == "data":
            if dataDec == ".":
                for rcpt in self.rcptBuffer:
                    temp = Storage.email(self.mailFromBuffer, rcpt, self.dataBuffer)
                    temp.saveEmail()
                    Auditing.logMail(self.mailFromBuffer, rcpt)
                self.commandRSET(module)
            else:
                if dataDec[0] == ".":
                    dataDec = dataDec[1:]
                self.dataBuffer = self.dataBuffer + dataDec + "\n"
                self.code250(" OK", module)

        elif command in commandsAnytime:
            self.commandsAnytimeRouter(dataDec, module)

        elif command == "RSET":
            self.commandRSET(module)

        elif self.subStateMail == "init":
            self.mailFromBuffer = argument[1:-1]
            self.subStateMail = "rcpt"
            self.code250(" OK", module)

        elif self.subStateMail == "rcpt":
            if command == "RCPT TO:":
                validity = CommonFunctions.mailValidationSMTP(argument)
                if validity == "OK":
                    self.rcptBuffer.append(argument[1:-1])
                    self.code250(" OK", module)
                else:
                    self.code553(validity, module)
            elif command == "DATA":
                if len(self.rcptBuffer) == 0:
                    self.code503("", module)
                else:
                    self.subStateMail = "data"
                    self.code354(module)
            else:
                self.code500(module)


    def commandsAnytimeRouter(self, data, module):
        command = CommonFunctions.commandOnly(data)
        argument = CommonFunctions.argumentOnly(data)
        if command == "VRFY":
            self.commandVRFY(argument, module)
        elif command == "EXPN":
            self.commandEXPN(argument, module)
        elif command == "HELP":
            self.commandHELP(argument, module)
        elif command == "NOOP":
            self.commandNOOP(module)
        elif command == "QUIT":
            self.commandQUIT(module)
        else:
            print("Wrong input")  # This would probably never occur due to the way the function is used.

    def commandREGISTER(self, argument, module):
        userName = CommonFunctions.firstWord(argument)
        if Storage.accountExists(self.accountUserRegistry, userName):
            self.code554(", account already exists.", module)
        else:
            userPass = CommonFunctions.secondWord(argument)
            hashedPassword, salt = SecurityServer.hashPW(userPass)
            tuser = Storage.accountUser(userName, hashedPassword, salt, ["",""])
            Storage.accountAdd(self.accountUserRegistry, tuser)
            Storage.accountsSave(self.accountUserRegistry, "User")
            self.code250(" Account Registered Successfuly, Log in.", module)


    def commandLOGIN(self, argument, module):
        userName = CommonFunctions.firstWord(argument)
        userPass = CommonFunctions.secondWord(argument)
        if Storage.accountValidateLogin(self.accountUserRegistry, userName, userPass):
            self.currentUser = Storage.accountGet(self.accountUserRegistry, userName)
            self.state = "greetings"
            Auditing.logLoginAttempt(userName,True)
            self.code250(" Logged in successfully", module)
        else:
            Auditing.logLoginAttempt(userName, False)
            self.code554(", username password pair doesn't exist, try again.", module)



    def commandLOGOUT(self, module):
        self.state = "login"
        self.currentUser = []
        self.clientDomain = "-"
        self.code250(" Logged out successfully", module)

    def commandMAIL(self, dataDec, module):
        argument = CommonFunctions.argumentOnly(dataDec)
        if argument == "-":
            self.code501(" You need to specify the sender address.", module)
        else:
            validity = CommonFunctions.mailValidationSMTP(argument)
            if validity == "OK":
                self.state = "mail"
                self.subStateMail = "init"
                self.stateMail(dataDec, module)
            else:
                self.code501(validity, module)

    def commandHELO(self, argument, module):
        self.clientDomain = argument
        message = " " + serverDomain
        self.code250(message, module)

    def commandEHLO(self, argument, module):
        self.clientDomain = argument
        message = "-" + serverDomain + " Hello " + self.clientDomain
        self.code250(message, module)
        message = "-LOGOUT"
        self.code250(message, module)
        message = "-EXPN"
        self.code250(message, module)
        message = "-VRFY"
        self.code250(message, module)
        message = "-REGMAIL"
        self.code250(message, module)
        message = "-ADDMAIL"
        self.code250(message, module)
        message = "-RMVMAIL"
        self.code250(message, module)
        message = "-MYMAILS"
        self.code250(message, module)
        message = "-LISTMAIL"
        self.code250(message, module)
        message = "-VIEWMAIL"
        self.code250(message, module)
        message = "-DELMAIL"
        self.code250(message, module)
        self.commandRSET(module)

    def commandRSET(self, module):
        if self.state != "greetings":
            self.state = "default"
            self.subStateMail = "init"
            self.mailFromBuffer = ""
            self.rcptBuffer = []
            self.dataBuffer = ""
        self.code250(" OK", module)



    def commandVRFY(self, argument, module):
        if argument != "-":
            data = Storage.commandVRFY(self.accountEmailRegistry, argument)
            CommonFunctions.sendData(data, module, self.securityServer)
        else:
            self.code501("", module)


    def commandEXPN(self, argument, module):
        if self.clientDomain == "-":
            self.code550(" No access", module)
        else:
            mailListAcc = Storage.accountGet(self.emailListRegistry, argument)
            if Storage.accountExists(self.emailListRegistry, argument) and len(mailListAcc.mailset) >= 1:
                for i in range(len(mailListAcc.mailset) - 1):
                    self.code250("-" + mailListAcc.mailset[i], module)
                self.code250(" " + mailListAcc.mailset[-1], module)
            else:
                self.code550(",  not found", module)


    def commandHELP(self, argument, module):
        command = argument.upper()
        if command == "-":
            self.code211(module)
        else:
            if command in commandsImplemented:
                self.code214(command,module)
            else:
                self.code504(module)


    def commandNOOP(self, module):
        self.code250(" OK", module)



    def commandQUIT(self, module):
        self.code221(module)
        module.close()

    def commandREGMAIL(self, argument, module):
        address = CommonFunctions.firstWord(argument)
        addressPass = CommonFunctions.secondWord(argument)
        mailValid = CommonFunctions.mailValidation(address)
        if mailValid == "OK":
            if CommonFunctions.userpassValidate(addressPass):
                hashedPassword, salt = SecurityServer.hashPW(addressPass)
                tmail = Storage.accountEmail(address, hashedPassword, salt)
                Storage.accountAdd(self.accountEmailRegistry, tmail)
                Storage.accountsSave(self.accountEmailRegistry, "Email")
                self.code250(" Email Account Registered Successfuly. Don't forget to add it to your User Account", module)
            else:
                self.code503(" Password must be atleast 6 characters long and CAN contain numbers, letters including the following symbols !@#$%^&*()-=_+,.?", module)
        else:
            self.code501(mailValid, module)

    def commandADDMAIL(self, argument, module):
        address = CommonFunctions.firstWord(argument)
        addressPass = CommonFunctions.secondWord(argument)
        mailValid = CommonFunctions.mailValidation(address)
        if mailValid == "OK":
            if CommonFunctions.userpassValidate(addressPass):
                if Storage.accountValidateLogin(self.accountEmailRegistry, address, addressPass):
                    Storage.accountUserEmailAdd(self.accountUserRegistry, self.currentUser.getIdentifier(), address)
                    Storage.accountsSave(self.accountUserRegistry, "User")
                    self.code250(" Email added successfully", module)
                else:
                    self.code550(" Email Password pair doesn't match anything.", module)
            else:
                self.code503(" Password must be atleast 6 characters long and CAN contain numbers, letters including the following symbols !@#$%^&*()-=_+,.?", module)
        else:
            self.code501(", " + mailValid, module)

    def commandRMVMAIL(self, argument, module):
        address = argument
        mailValid = CommonFunctions.mailValidation(address)
        if mailValid == "OK":
                if Storage.accountUserEmailExists(self.accountUserRegistry, self.currentUser.getIdentifier(), address):
                    Storage.accountUserEmailRemove(self.accountUserRegistry, self.currentUser.getIdentifier(), address)
                    Storage.accountsSave(self.accountUserRegistry, "User")
                    self.code250(" Email removed successfully", module)
                else:
                    self.code550(" Email not in current users emails.", module)
        else:
            self.code501(mailValid, module)

    def commandMYMAILS(self, module):
        mailset = self.currentUser.mailset
        if len(mailset) >= 1:
            for i in range(len(mailset) - 1):
                self.code250("-" + mailset[i],  module)
            self.code250(" " + mailset[-1], module)
        else:
            self.code554(", no mails in your mailboxes",module)

    def commandLISTMAIL(self, module):
        maillist = Storage.accountUserListEmail(self.accountUserRegistry, self.currentUser.getIdentifier())
        if len(maillist) >= 1:
            for i in range(len(maillist) - 1):
                self.code250("-" + maillist[i][1],  module)
            self.code250(" " + maillist[-1][1], module)
        else:
            self.code554(", no mails in your mailboxes",module)
    def commandVIEWMAIL(self, argument, module):
        try:
            emailid = int(argument)
        except ValueError:
            self.code501(" emailid can only be integer",module)
        else:
            contents = Storage.accountUserGetEmail(self.accountUserRegistry, self.currentUser.getIdentifier(), emailid)
            if contents == "IDERROR":
                self.code554(", mail id doesn't exist", module)
            else:
                splt = contents.splitlines()
                if len(splt) >= 1:
                    for i in range(len(splt) - 1):
                        self.code250("-" + splt[i], module)
                    self.code250(" " + splt[-1], module)
                else:
                    self.code554(", empty mail", module)
    def commandDELMAIL(self, argument, module):
        try:
            emailid = int(argument)
        except ValueError:
            self.code501(" emailid can only be integer", module)
        else:
            returnCode = Storage.accountUserDeleteEmail(self.accountUserRegistry, self.currentUser.getIdentifier(), emailid)
            if returnCode == "IDERROR":
                self.code554(", mail id doesn't exist", module)
            elif returnCode == "NFERROR":
                self.code554(", mail file doesn't exist", module)
            else:
                self.code250(" OK",module)


    def code211(self, module):
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
               "EHLO          Same as HELO but tells the server that the client may want to use the Extended SMTP (ESMTP) protocol instead.\n" \
               "REGMAIL       Registers a new email address to the server. \n" \
               "ADDMAIL       Adds a registered email address to the current users mail accounts list. \n" \
               "RMVMAIL       Removes an email address from the current users mail list. \n" \
               "MYMAILS       Displays the current users mail accounts list. \n" \
               "LISTMAIL      Lists mails accessible to the current user with their corresponding ID. \n" \
               "VIEWMAIL      Sends the client a copy of a mail associated with the ID provided. \n" \
               "DELMAIL       Deletes the mail that is associated with the ID provided."

        CommonFunctions.sendData(data, module, self.securityServer)


    def code214(self, argument, module):
        if argument == "HELO":
            data = "The HELO command is the command used by the host sending the command to identify itself; the command may be interpreted as saying \"Hello, I am <domain>\" \n" \
                   "USAGE: HELO clientdomain"
        elif argument == "QUIT":
            data = "The QUIT command specifies that the receiver must send an OK reply, and then close the transmission channel. \n" \
                   "USAGE: QUIT"
        elif argument == "MAIL FROM:":
            data = "The MAIL FROM: command is used to initiate a mail transaction in which the mail data is delivered to one or more mailboxes. The argument field contains a reverse-path. \n" \
                   "USAGE: MAIL FROM: <senderemail@domain.com>"
        elif argument == "RCPT TO:":
            data = "The RCPT TO: command is used to identify an individual recipient of the mail data; multiple recipients are specified by multiple use of this command. \n" \
                   "USAGE: RCPT TO: <recipientmail@domain.com>"
        elif argument == "DATA":
            data = "The DATA command causes the mail data from this command to be appended to the mail data buffer. The mail data may contain any of the 128 ASCII character codes. The mail data is terminated by a line containing only a period, that is the character sequence \"<CRLF>.<CRLF>\" \n" \
                   "USAGE: DATA"
        elif argument == "HELP":
            data = "The HELP command provides help information for SMTP commands, if used with a command returns information on that command. \n" \
                   "USAGE: HELP COMMAND"
        elif argument == "RSET":
            data = "The RSET command specifies that the current mail transaction is to be aborted. Any stored sender, recipients, and mail data must be discarded, and all buffers and state tables cleared. The server will send an OK reply. \n" \
                   "USAGE: RSET"
        elif argument == "VRFY":
            data = "The VRFY command asks the receiver to confirm that the argument identifies a user. If it is a user name, the full name of the user (if known) and the fully specified mailbox are returned.  \n" \
                   "USAGE: VRFY name"
        elif argument == "NOOP":
            data = "The NOOP command does not affect any parameters or previously entered commands. It specifies no action other than that the receiver send an OK reply. \n" \
                   "USAGE: NOOP"
        elif argument == "EXPN":
            data = "The EXPN command asks the receiver to confirm that the argument identifies a mailing list, and if so, to return the membership of that list. The full name of the users (if known) and the fully specified mailboxes are returned in a multiline reply. \n" \
                   "USAGE: EXPN nameoflist"
        elif argument == "EHLO":
            data = "Same as HELO but tells the server that the client may want to use the Extended SMTP (ESMTP) protocol instead.\n" \
                   "USAGE: EHLO clientdomain"
        elif argument == "REGMAIL":
            data = "Registers a new email address to the server. \n " \
                   "USAGE: REGMAIL email@domain.com password"
        elif argument == "ADDMAIL":
            data = "Adds a registered email address to the current users mail accounts list. \n " \
                   "USAGE: ADDMAIL email@domain.com password"
        elif argument == "RMVMAIL":
            data = "Removes an email address from the current users mail list. \n " \
                   "USAGE: RMVMAIL email@domain.com"
        elif argument == "MYMAILS":
            data = "Displays the current users mail accounts list. \n " \
                   "USAGE: MYMAILS"
        elif argument == "LISTMAIL":
            data = "Lists mails accessible to the current user with their corresponding ID. \n " \
                   "USAGE: LISTMAIL"
        elif argument == "VIEWMAIL":
            data = "Sends the client a copy of a mail associated with the ID provided. \n " \
                   "USAGE: VIEWMAIL 2"
        elif argument == "DELMAIL":
            data = "Deletes the mail that is associated with the ID provided. \n " \
                   "USAGE: DELMAIL 2"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code220(self, module):
        data = "220 " + serverDomain + " Simple Mail Transfer Service Ready"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code221(self, module):
        data = "221 " + serverDomain + " Service closing transmission channel"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code250(self, message, module):
        data = "250" + message
        CommonFunctions.sendData(data, module, self.securityServer)


    def code251(self, module, path):
        # path = <forward-path>
        data = "251 User not local; will forward to " + path
        CommonFunctions.sendData(data, module, self.securityServer)


    def code354(self, module):
        data = "354 Start mail input; end with <CRLF>.<CRLF>"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code421(self, module):
        data = "421" + serverDomain + " Service not available, closing transmission channel"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code450(self, module):
        data = "450 Requested mail action not taken: mailbox unavailable"
        # [E.g., mailbox busy]
        CommonFunctions.sendData(data, module, self.securityServer)


    def code451(self, module):
        data = "451 Requested action aborted: local error in processing"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code452(self, module):
        data = "452 Requested action not taken: insufficient system storage"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code500(self, module):
        data = "500 Syntax error, command unrecognized"
        # [This may include errors such as command line too long]
        CommonFunctions.sendData(data, module, self.securityServer)


    def code501(self, message, module):
        data = "501 Syntax error in parameters or arguments" + message
        CommonFunctions.sendData(data, module, self.securityServer)


    def code502(self, module):
        data = "502 Command not implemented"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code503(self, message, module):
        data = "503 Bad sequence of commands" + message
        CommonFunctions.sendData(data, module, self.securityServer)


    def code504(self, module):
        data = "504 Command parameter not implemented"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code550(self, message, module):
        data = "550 Requested action not taken: mailbox unavailable" + message
        # [E.g., mailbox not found, no access]
        CommonFunctions.sendData(data, module, self.securityServer)


    def code551(self, module, path):
        # path = <forward-path>
        data = "551 User not local; please try " + path
        CommonFunctions.sendData(data, module, self.securityServer)


    def code552(self, module):
        data = "552 Requested mail action aborted: exceeded storage allocation"
        CommonFunctions.sendData(data, module, self.securityServer)


    def code553(self, message, module):
        data = "553 Requested action not taken: mailbox name not allowed" + message
        # [E.g., mailbox syntax incorrect]
        CommonFunctions.sendData(data, module, self.securityServer)


    def code554(self, message, module):
        data = "554 Transaction failed" + message
        CommonFunctions.sendData(data, module, self.securityServer)
