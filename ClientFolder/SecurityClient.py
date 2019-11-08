import random
import socket
import blowfish
from os import urandom



class securityClient:
    def __init__(self):
        self.b = random.randint(1000, 10000)
        self.biv = urandom(8) # to be replaced with the recieved server's biv
        self.transferKey = 0
        self.cipher = blowfish.Cipher(("10"+"0000").encode())
        self.state = "init"
    def messageRouter(self, message, module):
        # diffie-hellman key exchange sequence
        if self.state == "init":
            print(message)
            self.state = "p"
        elif self.state == "p":
            self.p = int(message.decode())
            self.state = "g"
            #print("p" + str(self.p))
        elif self.state == "g":
            self.g = int(message.decode())
            self.state = "A"
            #print("g" + str(self.g))
        elif self.state == "A":
            self.A = int(message.decode())
            #print("A" + str(self.A))
            self.B = self.g ^ self.b % self.p
            module.create_message(str(self.B).encode())
            self.transferKey = self.A ^ self.b % self.p
            self.state = "biv"
        elif self.state == "biv":
            self.biv = message
            self.initializeEncryption()
            print(self.transferKey)
            self.state == "complete"
            module.responseProcessor.state = "default"
        else:
            print("Unknown state:" + self.state)

    def initializeEncryption(self):
        self.cipher = blowfish.Cipher((str(self.transferKey) + "0000").encode())
        print("encryption intialized")

    def encryptData(self, data):
        data = data.encode()
        dataEncrypted = b"".join(self.cipher.encrypt_cfb(data, self.biv))
        return dataEncrypted


    def decryptData(self, data):
        dataDecrypted = b"".join(self.cipher.decrypt_cfb(data, self.biv))
        return dataDecrypted
