import datetime
import os
import SecurityServer
import pickle

# accountUserRegistry & accountEmailRegistry aren't global here
# doing so would mean changing implementation of commands that apply to both


class accountUser:
    def __init__(self, username, passwordHashed, salt, mailSet):
        self.username = username
        self.passwordHashed = passwordHashed
        self.salt = salt
        self.mailSet = mailSet

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
    def __init__(self, name, mailList):
        self.name = name
        self.mailList = mailList

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
            print("ok")

def accountUserViewEmail(accountUserRegistry, username, emailid):
    print("ok")

def accountUserDeleteEmail(accountUserRegistry, username, emailid):
    print("ok")


def accountUserEmailAdd(accountUserRegistry, username, address):
    for account in accountUserRegistry:
        if account.username == username:
            account.mailset.add(address)


def accountUserEmailExists(accountUserRegistry, username, address):
    for account in accountUserRegistry:
        if account.username == username:
            return True
    return False

def accountUserEmailRemove(accountUserRegistry, username, address):
    for account in accountUserRegistry:
        if account.username == username:
            account.mailset.discard(address)


def accountAdd(accountsRegistry, account):
    # Make sure to check that the account doesn't exist already
    # input should be accountEmail type
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
        if account.getIdentifier == identity:
            return account


def accountValidateLogin(accountsRegistry, identity, password):
    # can be used for both Email & User type accounts
    for account in accountsRegistry:
        if account.getIdentifier() == identity:
            return SecurityServer.validatePW(account.passwordHashed, account.salt, password)
        else:
            return False
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
        print("404 - Returing Empty Variable")
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

#mailreg=[]
#mail1 = accountEmail("thanos@gmail.com","oopsie","001")
#accountAdd(mailreg,mail1)
#mail1 = accountEmail("thanos@hotmail.com","oopsie","001")
#accountAdd(mailreg,mail1)
#mail1 = accountEmail("thanos1@hotmail.com","oopsie","001")
#accountAdd(mailreg,mail1)

#for account in mailreg:
#    account.printAccountData()
#print(commandVRFY(mailreg,"thanos"))
