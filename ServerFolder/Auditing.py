import datetime


def logLoginAttempt(user, accountType, success):
    f = open("loginLog.txt", "a+")
    time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    f.write("Login attempt at: "+time+" | Account Type: "+accountType
            + " | User: "+user+" | Success: "+str(success)+"\n")
    f.close()
