from os import urandom
import blowfish

num = 10
cipher = blowfish.Cipher((str(num)+"0000").encode())


data = "Hello World!"  # data to encrypt
data = data.encode()
iv = urandom(8)  # initialization vector
print(str(iv))

data_encrypted = b"".join(cipher.encrypt_cfb(data, iv))

data_decrypted = b"".join(cipher.decrypt_cfb(data_encrypted, iv))

print(data_decrypted, data_encrypted, data)
print(data == data_decrypted)

def mailValidation(arguement):
    charset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.@'

    if arguement[0] == "<" and arguement[-1] == ">":
        arguement = arguement[1:-1]
        arguement = arguement.split("@")
        if len(arguement) == 2:
            if all(char in charset for char in arguement[0]):
                if len(arguement[1].split(".")) >1:
                    return "OK"
                else:
                    return "Domain name must include atleast 1 period (.)"
            else:
                return "Sorry, only letters (a-Z), numbers (0-9), and periods (.) are allowed."
        else:
            return "There must be exactly 1 at symbol (@) in the address"
    else:
        return "Sender address must be enclosed in \"< >\" "


#print(mailValidation("<Thanos@gmail.com>"))


test=[]
print(len(test))