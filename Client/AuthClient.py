import random
import socket
def initiateAUTHClient():
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 8080         # The port used by the server
    clientDomain = "AS-CLIENT.DERBY.AC.UK"
    running = 1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # b = random.randint(1, 10000)
        b = 9
        message = input("AUTHCLIENTINIT")
        s.send(message.encode())
        data = s.recv(8192)
        print('Received', data.decode())  # Server info
        data = s.recv(8192)
        print('Received', data.decode())  # Auth info
        s.send("testting attention please".encode())
        p = int(s.recv(8192).decode())
        g = int(s.recv(8192).decode())
        A = int(s.recv(8192).decode())
        print("A"+str(A))

        #data = s.recv(8192)
        #print('Received', data.decode())

        B = g ^ b % p
        s.sendall(str(B).encode())
        s.sendall("thanos".encode())
        s.sendall("1244".encode())


initiateAUTHClient()
