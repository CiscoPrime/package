import logging
import socket
import threading
from io import BytesIO as StringIO

try:
    # Import AF_UNIX only if available (not on Windows)
    from socket import AF_UNIX, SOCK_STREAM
except ImportError:
    # Define dummy constants for compatibility
    AF_UNIX = None
    SOCK_STREAM = None

from ncclient.capabilities import Capabilities
from ncclient.logging_ import SessionLoggerAdapter
from ncclient.transport.errors import UnixSocketError
from ncclient.transport.session import Session
from ncclient.transport.parser import DefaultXMLParser

logger = logging.getLogger("ncclient.transport.unix")

DEFAULT_TIMEOUT = 120
BUF_SIZE = 4096

class UnixSocketSession(Session):
    """Implements a NETCONF Session over Unix Socket on local machine."""

    def __init__(self, device_handler):
        capabilities = Capabilities(device_handler.get_capabilities())
        Session.__init__(self, capabilities)
        self._connected = False
        self._socket = None
        self._buffer = StringIO()
        self._device_handler = device_handler
        self._message_list = []
        self._closing = threading.Event()
        self.parser = DefaultXMLParser(self)
        self.logger = SessionLoggerAdapter(logger, {'session': self})

    def _dispatch_message(self, raw):
        self.logger.info("Received message from host")
        self.logger.debug("Received:\n%s", raw)
        return super(UnixSocketSession, self)._dispatch_message(raw)

    def close(self):
        self._closing.set()
        if self._socket:
            self._socket.close()
        self._connected = False

    def connect(self, path=None, timeout=DEFAULT_TIMEOUT):
        if AF_UNIX is None:
            raise UnixSocketError("AF_UNIX is not supported on this platform.")
       
        sock = socket.socket(AF_UNIX, SOCK_STREAM)
        sock.settimeout(timeout)

        try:
            sock.connect(path)
        except Exception as e:
            raise UnixSocketError(f"Could not connect to {path}: {e}")

        self._socket = sock
        self._connected = True
        self._post_connect()

    def _transport_read(self):
        return self._socket.recv(BUF_SIZE)

    def _transport_write(self, data):
        return self._socket.send(data)

    def _transport_register(self, selector, event):
        selector.register(self._socket, event)

    def _send_ready(self):
        # In contrast to Paramiko's `Channel`, pure python sockets do not
        # expose `send_ready()` function.
        return True
