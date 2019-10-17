import datetime
import os
import TEMP_HASHING
import pickle


class accountUser:
    def __init__(self, username, passwordHashed, salt, mailset):
        self.username = username
        self.passwordHashed = passwordHashed
        self.salt = salt
        self.mailset = mailset

    def getIdentifier(self):
        return self.username


class accountEmail:
    def __init__(self, address, passwordHashed, salt):
        self.address = address
        self.passwordHashed = passwordHashed
        self.salt = salt

    def getIdentifier(self):
        return self.address


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
                "At: " + date + "\n" +
                "Flags: TODO!!!" + "\n \n" +  # TODO
                self.contents)
        f.close()


def accountUserEmailAdd(accountUserRegistry, username, address):
    for account in accountUserRegistry:
        if account.username == username:
            account.mailset.add(address)


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


def accountAddressExists(accountsRegistry, identity):
    # can be used for both Email & User type accounts
    for account in accountsRegistry:
        if account.getIdentifier() == identity:
            return True
    return False


def accountValidateLogin(accountsRegistry, identity, password):
    # can be used for both Email & User type accounts
    for account in accountsRegistry:
        if account.getIdentifier() == identity:
            return TEMP_HASHING.validatePW(account[1], account[2], password)


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
        print("File not found...")
    else:
        accountsRegistry = pickle.load(f)
        f.close()
    return accountsRegistry
