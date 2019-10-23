import socket
import SecurityClient
import time
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8080         # The port used by the server
clientDomain = "AS-CLIENT.DERBY.AC.UK"
running = 1

def recieveData(socket,SecClient):
    data = socket.recv(8192)
    data = SecClient.decryptData(data)
    data = data.decode()
    return data


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # data = s.recv(8192)
    # print('Received', data.decode())  # server welcome message
    SecClient = SecurityClient.securityClient()
    message = "init"
    s.sendall(message.encode())
    transferKey = SecClient.initiateKeyExchangeClient(s)
    print(str(transferKey))
    while running == 1:
        message = input("Message for server:")
        if message == "":
            message == " "
        print(message)
        message = SecClient.encryptData(message)
        s.sendall(message)
        time.sleep(0.05)
        data = recieveData(s,SecClient)
        print(data)

