import selectors
import queue
import traceback
import ResponseProcessor
from threading import Thread


class Module(Thread):
    def __init__(self, sock, addr):
        Thread.__init__(self)

        self._selector = selectors.DefaultSelector()
        self._sock = sock
        self._addr = addr

        self._incoming_buffer = queue.Queue()
        self._outgoing_buffer = queue.Queue()

        self.responseProcessor = ResponseProcessor.responseProcessor()

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._selector.register(self._sock, events, data=None)

    def run(self):
        try:
            while True:
                events = self._selector.select(timeout=None)
                for key, mask in events:
                    try:
                        if mask & selectors.EVENT_READ:
                            self._read()
                        if mask & selectors.EVENT_WRITE and not self._outgoing_buffer.empty():
                            self._write()
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{self._addr}:\n{traceback.format_exc()}",
                        )
                        self._sock.close()
                if not self._selector.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self._selector.close()

    def _read(self):
        try:
            data = self._sock.recv(8192)
        except BlockingIOError:
            print("blocked")
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._incoming_buffer.put(data)
            else:
                raise RuntimeError("Peer closed.")

        self._process_response()

    def _write(self):
        try:
            message = self._outgoing_buffer.get_nowait()
        except:
            message = None

        if message:
            try:
                print("message", str(self.responseProcessor.securityServer.decryptData(message).decode()),
                      "Response Processor State:", self.responseProcessor.state, "sending", repr(message), "to", self._addr)
            except UnicodeDecodeError:
                print("sending ", repr(message), "to", self._addr, "Response Processor State:", self.responseProcessor.state)
            try:
                sent = self._sock.send(message)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass

    def _send_data(self, data):
        self._outgoing_buffer.put(data)

    def _process_response(self):
        data = self._incoming_buffer.get()
        self._module_processor(data)

    def _module_processor(self, data):
        self.responseProcessor.commandRouter(data, self)

    def close(self):
        print("closing connection to", self._addr)
        try:
            self._selector.unregister(self._sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self._addr}: {repr(e)}",
            )
        try:
            self._sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self._addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self._sock = None

