import asyncore
import socket
import ResponseProcessor
import CommonFunctions

responseProcessorInstance = ResponseProcessor.responseProcessorInstance()


class EchoHandler(asyncore.dispatcher_with_send):
    global responseProcessorInstance

    def handle_read(self):
        data = self.recv(8192)
        if data:
            responseProcessorInstance.commandRouter(data, self)


class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print('Incoming connection from %s' % repr(addr))
            handler = EchoHandler(sock)
            #Server.code220(sock)  # TODO


server = EchoServer('127.0.0.1', 9999)
asyncore.loop()
