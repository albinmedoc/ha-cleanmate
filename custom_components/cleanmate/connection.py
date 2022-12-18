"""Connection flow for Cleanmate integration."""

import asyncio
import json
from .helpers import parse_value


class Connection:
    """Connection to a Cleanmate vacuum."""

    port = 8888

    host: str
    auth_code: str

    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    def __init__(self, host: str, auth_code: str) -> None:
        self.host = host
        self.auth_code = auth_code

    async def connect(self) -> None:
        """Connect to the Cleanmate vacuum."""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.writer.write_timeout = 10
        self.writer.read_timeout = 10

    async def disconnect(self) -> None:
        """Disconnect from the Cleanmate vacuum."""
        self.writer.close()
        self.reader = None
        self.writer = None

    def _get_request_prefix(self, size: int) -> str:
        size_hex = "{0:x}".format(size)
        temp = f"{'0'*(8-len(size_hex))}{size_hex}"
        return "".join(map(str.__add__, temp[-2::-2], temp[-1::-2]))

    async def send_request(self, data: dict[str, any]) -> None:
        """Send a request to the Cleanmate vacuum."""
        request = json.dumps(
            {
                "version": "1.0",
                "control": {
                    "authCode": self.auth_code,
                },
                "value": data,
            },
            separators=(",", ":"),
        )

        request_size = len(request) + 20
        request_hex = request.encode("utf-8").hex()
        prefix = self._get_request_prefix(request_size)

        packet = f"{prefix}fa00000001000000c527000001000000{request_hex}"
        await self.send_raw_request(bytes.fromhex(packet))

    async def send_raw_request(self, raw_data: bytes) -> None:
        """Send a raw request to the Cleanmate vacuum."""
        await self.connect()
        self.writer.write(raw_data)
        await self.writer.drain()

    async def read_data(self, bytes: int) -> bytes:
        data = await self.reader.read(bytes)
        if(not data): 
            raise ConnectionError
        return data
    
    async def get_response(self):
        try:
            # Read size from header
            header = await self.read_data(20)

            raw_size_hex = header[:4].hex()

            # Reverse the order pairwise
            size_hex: str = "".join(
                map(str.__add__, raw_size_hex[-2::-2], raw_size_hex[-1::-2])
            )
            size = (
                int(size_hex, base=16) - len(header)
            )  # Minus the header that we already gathered

            # Read actual data
            data = b""
            while len(data) < size:
                data += await self.read_data(size)
            response = parse_value(data.decode("ascii"))
            return response
        except asyncio.TimeoutError as err:
            raise err
