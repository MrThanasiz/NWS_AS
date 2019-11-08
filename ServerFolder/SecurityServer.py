import CommonFunctions
import random
import time
import blowfish
from os import urandom
import hashlib
import os



class securityServer:
    def __init__(self):
        self.a = random.randint(1000, 10000)
        self.p = random.randint(1000, 10000)
        self.g = random.randint(1000, 10000)
        self.state = 0
        self.biv = urandom(8)  # Blowfish initialization vector
        self.transferKey = 0
        self.cipher = blowfish.Cipher("Hello World".encode())

    def initiateKeyExchangeServer(self, data, module):
        A = self.g ^ self.a % self.p
        if self.state == 0 and data.upper() == "INIT":
            message = "Diffie-Hellman Exchange Initiated, sending in the following order" \
                      ": p,g,A and waiting for B"

            # Tried several times and without a delay, either via time.sleep or
            # by priting the data, it wouldn't work properly.

            CommonFunctions.sendDataKeyExchange(message, module)
            time.sleep(0.005)
            CommonFunctions.sendDataKeyExchange(str(self.p), module)
            # print("p" + str(self.p))
            time.sleep(0.005)
            CommonFunctions.sendDataKeyExchange(str(self.g), module)
            # print("g" + str(self.g))
            time.sleep(0.005)
            CommonFunctions.sendDataKeyExchange(str(A), module)
            # print("A"+str(A))
            time.sleep(0.005)
            self.state = 1
        elif self.state == 1:
            B = int(data)
            self.transferKey = B ^ self.a % self.p
            module._send_data(self.biv)
            self.initializeEncryption()
            self.state = 2
        elif self.state == 2:
            print("Key exchange already completed.")
            # what should happen here? is it fine to return transfer key again?
            # transferKey = 0
        return self.transferKey,self.state==2


    def initializeEncryption(self):
        self.cipher = blowfish.Cipher((str(self.transferKey)+"0000").encode())

    def encryptData(self, data):
        dataEncrypted = b"".join(self.cipher.encrypt_cfb(data, self.biv))
        return dataEncrypted


    def decryptData(self, data):
        dataDecrypted = b"".join(self.cipher.decrypt_cfb(data, self.biv))
        return dataDecrypted


def hashPW(password):
    salt = os.urandom(16)
    hashedPassword = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return hashedPassword, salt


def validatePW(hashedPassword, salt, inputPassword):
    hashedInputPassword = hashlib.pbkdf2_hmac('sha256', inputPassword.encode(), salt, 100000)
    return hashedPassword == hashedInputPassword

