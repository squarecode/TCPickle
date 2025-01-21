# pylint: disable=line-too-long
from enum import Enum
import socket
import pickle


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


class TCPickleServer:
    """ Server side object of the TCPickle interface

    Args:
        server_ip (str):  IP to bind to.Usually just `localhost` or `127.0.0.1`.
                            Defaults to: `localhost`
        server_port (int):  Port to bind to. Can be any unoccupied port.
                            Defaults to: 50007
    """

    _ip: str
    _port: int
    _debug: bool

    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    _MAX_CONNECTIONS: int = 1

    def __init__(self, server_ip: str = 'localhost', server_port: int = 50007, debug: bool = False):
        self._ip = server_ip
        self._port = server_port
        self._debug = debug

    def initialize(self) -> str:
        """ Initializes the TCPickle Server instance with
            the pre-provided information.
        Raises:
            exc: Raises common socket exceptions
        Returns:
            str: Returns connection information for a client
        """
        try:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind((self._ip, self._port))
            self._sock.listen(self._MAX_CONNECTIONS)
        except socket.error as exc:
            raise exc
        if self._debug:
            print("[TCPickleServer] Initialized!")
            print(f"[TCPickleServer] Ready as: \033[93m{socket.getfqdn()}\033[0m on \033[93m{self._port}\033[0m")
        return socket.getfqdn(), self._port

    def _eval_answer_to_offer(self, client: socket.socket) -> bool:
        """ *Private function* Evaluates the response code of the client.
        Raises:
            Exception: Raises a TCPickleException with an unknown response code
        Returns:
            bool: Returns `True` if the client is willing to accept more data.
        """
        serialized_resp = client.recv(1024)
        response_code = pickle.loads(serialized_resp)
        if isinstance(response_code, int):
            response_code = ResponseCode(response_code)
            if self._debug:
                print(f"[TCPickleServer] Got response code: {response_code}")
            match response_code:
                case ResponseCode.DECLINE_DATA:
                    return False
                case ResponseCode.ACCEPT_DATA:
                    return True
                case _:
                    err = f"[TCPickleServer] ERROR: Got an invalid response from the client! {response_code.value}"
                    raise TCPickleException(err)
        else:
            raise ValueError

    def offer_data_to_client(self, data: any) -> bool:
        """ Offering some data to a client. *BLOCKING!*
            The input `data` will be pickled and transferred
            to a connecting client. Transfer is initiated as soon
            as a client connects.

        Args:
            data (any): Can be any python object.
        Returns:
            bool: True if the response of the client
        """
        if self._debug:
            print("[TCPickleServer] Waiting for a client to connect ...")
        client, addr = self._sock.accept()
        if self._debug:
            print(f"[TCPickleServer] Incomming connection from {addr}")

        if not self._eval_answer_to_offer(client):
            # Client requests to close the connection and referes from receiving more data
            if self._debug:
                print("[TCPickleServer] Closing the connection on client request")
            client.close()
            self._sock.close()
            return False
        # Got'it! You want all the data!
        # Let's pickle the data and flush it down the link
        if self._debug:
            print("[TCPickleServer] Sending data ...")
        try:
            pickled = pickle.dumps(data)
            client.sendall(pickled)
            client.close()
        except socket.error as exc:
            raise TCPickleException(f"Failed to send the data to the client! {exc}") from exc
        if self._debug:
            print("[TCPickleServer] Data has been sent!")
        return True

#pylint: disable=C0103
if __name__ == '__main__':
    server = TCPickleServer(debug=True)
    server.initialize()
    client_wants_data = True
    while client_wants_data:
        client_wants_data = server.offer_data_to_client([1.0, 2.0, 3.0, 4.0, 5.0])
    print("Server has been closed!")
