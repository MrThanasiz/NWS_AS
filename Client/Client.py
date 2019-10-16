import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8080         # The port used by the server
clientDomain = "AS-CLIENT.DERBY.AC.UK"
running = 1
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(8192)
    print('Received', data.decode())
    while running == 1:
        message = input("Message for server:")
        s.sendall(message.encode())
        data = s.recv(8192)
        print(data.decode())
