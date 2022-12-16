"""Connection flow for Cleanmate integration."""

import socket
import json
from .helpers import parse_value

class Connection:
    """Connection to a Cleanmate vacuum."""

    port = 8888

    host: str
    auth_code: str
    sock: socket.socket

    def __init__(self, host: str, auth_code: str) -> None:
        self.host = host
        self.auth_code = auth_code
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            raise err

    def connect(self) -> None:
        """Connect to the Cleanmate vacuum."""
        self.sock = socket.create_connection((self.host, self.port))
        self.sock.settimeout(10)

    def disconnect(self) -> None:
        """Disconnect from the Cleanmate vacuum."""
        self.sock.close()
        self.sock = None

    def _get_request_prefix(self, size: int) -> str:
        size_hex = "{0:x}".format(size)
        temp = f"{'0'*(8-len(size_hex))}{size_hex}"
        return "".join(map(str.__add__, temp[-2::-2] ,temp[-1::-2]))

    def send_request(self, data: dict[str, any]) -> None:
        """Send a request to the Cleanmate vacuum."""
        request = json.dumps({
            "version": "1.0",
            "control": {
                "authCode": self.auth_code,
            },
            "value": data,
        }, separators=(',', ':'))

        request_size = len(request) + 20
        request_hex = request.encode('utf-8').hex()
        prefix = self._get_request_prefix(request_size)
        
        packet = f"{prefix}fa00000001000000c527000001000000{request_hex}"
        return self.send_raw_request(bytes.fromhex(packet))
    
    def send_raw_request(self, raw_data: bytes) -> None:
        """Send a raw request to the Cleanmate vacuum."""
        self.connect()
        self.sock.sendall(raw_data)
        # Detect if vacuum closed the connection, then raise error
        # A FIN ACK is sent if the auth_code is wrong
    
    def read_data(self):
        try:
            # Read size from header
            header = self.sock.recv(20)
            raw_size_hex = header.hex().split("00")[0]
            size_hex: str = "".join(map(str.__add__, raw_size_hex[-2::-2] ,raw_size_hex[-1::-2]))
            size = int(size_hex, base=16) - 20 # Minus the header that we already gathered

            # Read actual data
            chunks = []
            bytes_recd = 0
            while bytes_recd < size:
                chunk = self.sock.recv(min(size - bytes_recd, 2048))
                if chunk == b'':
                    raise RuntimeError("Socket connection broken")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            data =  b''.join(chunks)
            response = parse_value(data.decode("ascii"))
            return response
        except TimeoutError as err:
            raise err
        
