__author__ = "Christopher Windmill, Brad Solomon"

__version__ = "1.0.1"
__status__ = "Development"

import time
import socket
import selectors
import SMTPClientLib
import traceback


class NWSThreadedClient ():
    def __init__(self, host="127.0.0.1", port=9999):
        if __debug__:
            print("NWSThreadedClient.__init__", host, port)

        # Network components
        self._host = host
        self._port = port
        self._listening_socket = None
        self._selector = selectors.DefaultSelector()

        self._module = None

    def start_connection(self, host, port):
        addr = (host, port)
        print("starting connection to", addr)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)

        self._module = SMTPClientLib.Module(sock, addr)
        self._module.start()

    def run(self):
        self.start_connection(self._host, self._port)

        if self._module.responseProcessor.state == "keyExchange":
            self._module.create_message("init".encode())

        time.sleep(0.2)

        while True:
            userInput = input("Send a message:")

            if len(userInput) == 0:  # This is used to prevent sending an empty message
                userInput = userInput + " "
            if userInput[0] == "." and len(userInput) > 1:  # This is used for the DATA part, is a "requirement" of RFC821
                userInput = "." + userInput

            message = self._module.securityClient.encryptData(userInput)
            self._module.create_message(message)
            time.sleep(0.1)


if __name__ == "__main__":
    client = NWSThreadedClient()
    client.run()
