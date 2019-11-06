import datetime
import os
import SecurityServer
import pickle


class accountUser:
    def __init__(self, username, passwordHashed, salt, mailset):
        self.username = username
        self.passwordHashed = passwordHashed
        self.salt = salt
        self.mailset = mailset

    def getIdentifier(self):
        return self.username

    def printAccountData(self):
        print("Address:  " + self.address)
        print("password: " + self.passwordHashed)
        print("Salt:     " + self.salt)
        print("Mailset:  "+  self.mailset)



class accountEmail:
    def __init__(self, address, passwordHashed, salt):
        self.address = address
        self.passwordHashed = passwordHashed
        self.salt = salt

    def getIdentifier(self):
        return self.address

    def printAccountData(self):
        print("Address:  " + self.address)
        print("password: " + self.passwordHashed)
        print("Salt:     " + self.salt)


class mailingList:
    def __init__(self, name, mailset):
        self.name = name
        self.mailset = mailset

    def getIdentifier(self):
        return self.name


class email:
    def __init__(self, mailFrom, rcptTo, contents):
        self.mailFrom = mailFrom
        self.rcptTo = rcptTo
        self.contents = contents

    def saveEmail(self):
        self.createEmailFolder()
        self.saveEmailContents()

    def createEmailFolder(self):
        path = os.getcwd()
        path = path + "/emails/" + str(self.rcptTo) + "/"
        try:
            os.makedirs(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)

    def saveEmailContents(self):
        path = os.getcwd()
        date = datetime.datetime.now().strftime("%y-%m-%d %H-%M-%S")
        path = path + "/emails/" + str(self.rcptTo) + "/" + date + " " + str(self.mailFrom) + ".txt"
        print(path)
        f = open(path, "w+")
        date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        f.write("From: " + self.mailFrom + "\n" +
                "To:" + self.rcptTo + "\n" +
                "Sent: " + date + "\n \n" +
                self.contents)
        f.close()

def accountUserListEmail(accountUserRegistry, username):
    for account in accountUserRegistry:
        if account.username == username:
            maillist = []
            mailid = 0
            for mail in account.mailset:
                if os.path.isdir("emails/" + mail):
                    for file in os.listdir("emails/" + mail):
                        if file.endswith(".txt"):
                            maillist.append([os.path.join("emails/" + mail, file),
                            "ID: " + str(mailid) + " Date - Sender: " + file[:-4] + " Recipient: " + mail])
                            mailid = mailid + 1
            return maillist



def accountUserGetEmail(accountUserRegistry, username, emailid):
    maillist = accountUserListEmail(accountUserRegistry, username)
    try:
        f = open(maillist[emailid][0], 'r')
        mail = f.read()
        print(mail)
        f.close()
    except IndexError:
        return "IDERROR"
    else:
        return mail

def accountUserDeleteEmail(accountUserRegistry, username, emailid):
    maillist = accountUserListEmail(accountUserRegistry, username)
    try:
        if os.path.exists(maillist[emailid][0]):
            os.remove(maillist[emailid][0])
            return "OK"
        else:
            return "NFERROR"
    except IndexError:
        return "IDERROR"
    else:
        return "OK"


def accountUserEmailAdd(accountUserRegistry, username, address):
    for account in accountUserRegistry:
        if account.getIdentifier() == username:
            if not accountUserEmailExists(accountUserRegistry, username, address):
                account.mailset.append(address)


def accountUserEmailExists(accountUserRegistry, username, address):
    for account in accountUserRegistry:
        if account.getIdentifier() == username:
            for mail in account.mailset:
                if mail == address:
                    return True
    return False

def accountUserEmailRemove(accountUserRegistry, username, address):
    for account in accountUserRegistry:
        if account.getIdentifier() == username:
            account.mailset.remove(address)


def accountAdd(accountsRegistry, account):
    # Make sure to check that the account doesn't exist already
    # input should be account type
    accountsRegistry.append(account)
    return accountsRegistry


def accountDelete(accountsRegistry, identity):
    for account in accountsRegistry:
        if account.getIdentifier() == identity:
            accountsRegistry.remove(account)
    return accountsRegistry


def accountExists(accountsRegistry, identity):
    # can be used for both Email & User type accounts
    for account in accountsRegistry:
        if account.getIdentifier() == identity:
            return True
    return False

def accountGet(accountsRegistry, identity):
    for account in accountsRegistry:
        if account.getIdentifier() == identity:
            return account


def accountValidateLogin(accountsRegistry, identity, password):
    # can be used for both Email & User type accounts
    for account in accountsRegistry:
        if account.getIdentifier() == identity:
            return SecurityServer.validatePW(account.passwordHashed, account.salt, password)
    print("doesn't exist")
    return False


def accountsSave(accountsRegistry, accountsType):
    filename = "accounts" + accountsType
    f = open(filename, "wb")
    pickle.dump(accountsRegistry, f)
    f.close()


def accountsLoad(accountsType):
    accountsRegistry = []
    filename = "accounts" + accountsType
    try:
        f = open(filename, "rb")
    except FileNotFoundError:
        print("404 - Returing Test Variable")
        if accountsType == "Email":
            address = "testuser@gmail.com"
            addressPass = "testpass"
            hashedPassword, salt = SecurityServer.hashPW(addressPass)
            tmail = accountEmail(address, hashedPassword, salt)
            accountAdd(accountsRegistry, tmail)
            address = "testuser@hotmail.com"
            addressPass = "testpass"
            hashedPassword, salt = SecurityServer.hashPW(addressPass)
            tmail = accountEmail(address, hashedPassword, salt)
            accountAdd(accountsRegistry, tmail)
            address = "testuser@yahoo.com"
            addressPass = "testpass"
            hashedPassword, salt = SecurityServer.hashPW(addressPass)
            tmail = accountEmail(address, hashedPassword, salt)
            accountAdd(accountsRegistry, tmail)
            #accountsSave(accountsRegistry, "Email")
        elif accountsType == "User":
            userName = "testuser"
            userPass = "testpass"
            hashedPassword, salt = SecurityServer.hashPW(userPass)
            tuser = accountUser(userName, hashedPassword, salt, ["testuser@gmail.com", "testuser@yahoo.com"])
            accountAdd(accountsRegistry, tuser)
            #accountsSave(accountsRegistry, "User") # Will only be saved if something get's added.
        elif accountsType == "MailList":
            tmailList = mailingList("testlist", ["testuser@gmail.com", "testuser@hotmail.com", "testuser@yahoo.com"])
            accountAdd(accountsRegistry, tmailList)
        else:
            print("Unknown type, returning empty variable")
        return accountsRegistry
    else:
        accountsRegistry = pickle.load(f)
        f.close()
    return accountsRegistry

def commandVRFY(accountEmailRegistry,prefix):
    acclist=[]
    for account in accountEmailRegistry:
        email = account.getIdentifier()
        split = email.split("@")
        if split[0]==prefix:
            acclist.append(account)
    if len(acclist) == 0:
        return "550 String does not match anything."
    elif len(acclist) == 1:
        return "250 " + "<" + acclist[0].getIdentifier() + ">"
    else:
        return "553 User ambiguous."
