import CommonFunctions


p = 23
g = 5


def initiateAUTHServer(data, socket):
    print("auth initialization")
    global p
    global g
    # a = random.randint(1, 10000)
    a = 4
    A = g ^ a % p
    data = data.decode()
    if data != "AUTH":
        message = "You're not connected please use local command AUTH to start the Authentication Sequence"
        CommonFunctions.sendData(message, socket)
    else:
        message = "Diffie-Hellman Exchange Initiated, sending in the following order" \
                  ": p,g,A and waiting for B, Username and Encrypted Password"
        CommonFunctions.sendData(message, socket)
        print(socket.recv(8192).decode())
        CommonFunctions.sendData(str(p), socket)
        CommonFunctions.sendData(str(g), socket)
        CommonFunctions.sendData(str(A), socket)
        B = int(CommonFunctions.recvData(socket))
        print("hii")
        transferKey = B ^ a % p
        print("TRANSFER KEY = "+transferKey)

        username = CommonFunctions.recvData(socket)
        encryptedpass = CommonFunctions.recvData(socket)

        if authenticate(username, encryptedpass, transferKey):
            return True
    return False


accounts = {'thanos':'1234','bob':'5678'}


def authenticate(username, encryptedpass, key):
    pword = encryptedpass
    if username in accounts and accounts.get(username) == pword:
        return True


