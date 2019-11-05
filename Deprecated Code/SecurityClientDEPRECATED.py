import random
import socket
import blowfish
from os import urandom



class securityClient:
    def __init__(self):
        self.b = random.randint(1000, 10000)
        self.biv = urandom(8) # to be replaced with the recieved server's biv
        self.transferKey = 0
        self.cipher =blowfish.Cipher(("10"+"0000").encode())
    def initiateKeyExchangeClient(self, s):
        data = s.recv(8192)
        print('Received', data.decode())  # Auth info
        p = int(s.recv(8192).decode())
        # print("p" + str(p))
        g = int(s.recv(8192).decode())
        # print("g" + str(g))
        A = int(s.recv(8192).decode())
        # print("A" + str(A))
        B = g ^ self.b % p
        s.sendall(str(B).encode())
        self.transferKey = A ^ self.b % p
        self.biv = s.recv(8192)
        self.initializeEncryption()
        return self.transferKey

    def initializeEncryption(self):
        self.cipher = blowfish.Cipher((str(self.transferKey) + "0000").encode())

    def encryptData(self, data):
        data = data.encode()
        dataEncrypted = b"".join(self.cipher.encrypt_cfb(data, self.biv))
        return dataEncrypted


    def decryptData(self, data):
        dataDecrypted = b"".join(self.cipher.decrypt_cfb(data, self.biv))
        return dataDecrypted
