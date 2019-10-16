import datetime
import os


class accountUser:
    def __init__(self, username, password, mailset):
        self.username = username
        self.password = password
        self.mailset = mailset


class accountEmail:
    def __init__(self, address, password):
        self.address = address
        self.password = password


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
        f = open(path, "a+")
        date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        f.write("From: " + self.mailFrom + "\n" +
                "To:" + self.rcptTo + "\n" +
                "At: " + date + "\n" +
                "Flags: TODO!!!" + "\n \n" +  # TODO
                self.contents)
        f.close()


