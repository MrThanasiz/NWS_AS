import hashlib
import os


def hashPW(password):
    salt = os.urandom(16)
    hashedPassword = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return hashedPassword, salt


def validatePW(hashedPassword, salt, inputPassword):
    hashedInputPassword = hashlib.pbkdf2_hmac('sha256', inputPassword.encode(), salt, 100000)
    return hashedPassword == hashedInputPassword
