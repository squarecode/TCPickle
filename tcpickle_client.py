# pylint: disable=line-too-long
import socket
import pickle
from time import sleep
from enum import Enum


class ResponseCode(Enum):
    """ Response codes for the communication between server & client """
    INVALID      = 0
    ACCEPT_DATA  = 1
    DECLINE_DATA = 2


class TCPickleException(Exception):
    """ Custom TCPickleException """
    def __init__(self, msg='Unknown TCPickle Exception'):
        self.value = msg

    def __str__(self):
        return repr(self.value)


class TCPickleClient:
    """ Client side object of the TCPickle interface

    Args:
        server_ip (str):  IP to connect to. Defaults to: `localhost`
        server_port (int):  Port of the Server to connect to. Defaults to: 50007
    """

    _ip: str
    _port: int
    _debug: bool

    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _has_file_descriptor: bool = False

    _CHUNK_SIZE = 4069

    def __init__(self, server_ip: str = 'localhost', server_port: int = 50007, debug: bool = False):
        self._ip = server_ip
        self._port = server_port
        self._debug = debug

    def initialize(self) -> bool:
        """ Initializes the TCPickle Client instance with
            the pre-provided information.
        Raises:
            exc: Raises ConnectionRefusedError in case of a blocked server
        Returns:
            bool: Returns connection information for a client
        """
        connection_not_ok = True
        while connection_not_ok:
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.connect((self._ip, self._port))
                connection_not_ok = False
            except socket.error as exc:
                if isinstance(exc, ConnectionRefusedError):
                    if self._debug:
                        print("[TCPickleClient] Connection refused by the server!")
                        print("[TCPickleClient] Retrying in 1s ...")
                    sleep(1)
                else:
                    raise exc
            # finally:
            #     self._sock.close()
        if self._debug:
            print("[TCPickleClient] Connected!")
        self._has_file_descriptor = True
        return True

    def _respond_to_server(self, response: ResponseCode):
        """ Transmits a response code to the server
        Args:
            response (ResponseCode): ResponseCode to send to the server
        """
        if not self._has_file_descriptor:
            self.initialize()
        self._sock.sendall(pickle.dumps(response.value))

    def grab_data_from_server(self) -> any:
        """ Function to grab data from the server
        Returns:
            any: Returns the received and unpickled python object
        """
        if not self._has_file_descriptor:
            self.initialize()
        self._respond_to_server(ResponseCode.ACCEPT_DATA)
        if self._debug:
            print("[TCPickleClient] Waiting for the server to send the data ...")
        # read the chunks from the server
        data = b''
        chunks = []
        while True:
            chunk = self._sock.recv(self._CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
        data += b''.join(chunks)
        self._sock.close()
        self._has_file_descriptor = False
        if len(data) > 0:
            rxed_obj = pickle.loads(data)
            if self._debug:
                print(f"[TCPickleClient] Rxed: {len(rxed_obj)} values")
        else:
            if self._debug:
                print("[TCPickleClient] ERROR: Didn't receive any data!")
                rxed_obj = None
        return rxed_obj

    def stop_server(self) -> None:
        """ Stops the server side from transferring more data """
        self._respond_to_server(ResponseCode.DECLINE_DATA)
        if self._debug:
            print("[TCPickleClient] Decline issued to server")
        self._sock.close()
        self._has_file_descriptor = False


if __name__ == '__main__':
    client = TCPickleClient(debug=True)
    client.initialize()
    print("\033[93mGrabbing some data ...\033[0m")
    data_1 = client.grab_data_from_server()
    print("\033[93mGrabbing some more data in 1 sec ...\033[0m")
    sleep(1)
    data_2 = client.grab_data_from_server()
    print("\033[93mEnough for now!\033[0m")
    client.stop_server()
    print("\033[93mClose connection. Bye!\033[0m")
