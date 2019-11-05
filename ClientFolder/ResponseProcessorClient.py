import time

class responceProcessor:
    def __init__(self):
        self.state = "keyExchange"


    def messageRouter(self, message, module):
        if self.state == "keyExchange":
            module.securityClient.messageRouter(message, module)
        else:
            contents = module.securityClient.decryptData(message)
            print(contents.decode())
