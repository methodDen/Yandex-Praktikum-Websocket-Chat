import asyncio
import aioconsole

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
        self.reader: StreamReader | None = None
        self.writer: StreamWriter | None = None

    async def connect_to_server(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.server_host, self.server_port,
        )
        try:
            await asyncio.gather(
                self.send_messages(),
                self.receive_messages(),
            )
        except asyncio.CancelledError:
            print("Client connection is closed")
            await self.close_connection()

    async def close_connection(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def send_messages(self):
        while True:
            message = await aioconsole.ainput()
            self.writer.write(message.encode())
            await self.writer.drain()

    async def receive_messages(self):
        while message := (await self.reader.read(1024)).decode():
            await aioconsole.aprint(f"{message}")


if __name__ == '__main__':
    print("Starting client connection")
    client = Client()
    try:
        asyncio.run(client.connect_to_server())
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, closing client connection")
