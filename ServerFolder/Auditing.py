import datetime


def logLoginAttempt(user, success):
    f = open("loginLog.txt", "a+")
    time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    f.write("Login attempt at: " + time + " | User: " + user + " | Success: " + str(success) + "\n")
    f.close()


def logMail(mailFrom, rcptTo):
    f = open("actionsLog.txt", "a+")
    time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    f.write("Mail sent at: " + time + " | From User: " + mailFrom + " | To User: " + rcptTo + "\n")
    f.close()
