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


print("saying \"Hello, I am <domain>\"")
