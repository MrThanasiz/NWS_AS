import datetime


def logLoginAttempt(user, acccountType, success):
    f = open("loginLog.txt", "a+")
    time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    f.write("Login attempt at: "+time+" | Account Type: "+acccountType
            + " | User: "+user+" | Success: "+str(success)+"\n")
    f.close()
