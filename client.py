from config import (
    SERVER_HOST,
    SERVER_PORT,
)
from asyncio import (
    StreamReader,
    StreamWriter,
)


class Client:
    def __init__(self, server_host=SERVER_HOST, server_port=SERVER_PORT):
        self.server_host = server_host
        self.server_port = server_port
        self.reader: StreamReader = None
        self.writer: StreamWriter = None

    async def send(self, message=""):
        pass

    async def connect(self):
        pass

    async def receive(self):
        pass

