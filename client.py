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
import logger

logger = logger.get_logger(__name__)


class Client:
    def __init__(self, server_host=SERVER_HOST, server_port=SERVER_PORT):
        self.server_host = server_host
        self.server_port = server_port
        self.reader: StreamReader = None
        self.writer: StreamWriter = None

    async def connect_to_server(self):
        logger.info("Client connection is initialized at %s:%d", self.server_host, self.server_port)
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server_host, self.server_port,
            )
            await asyncio.gather(
                self.send_messages(),
                self.receive_messages(),
            )
        except Exception as ex:
            logger.error("An error has occurred: %s", ex)
        finally:
            await self.close_connection()

    async def close_connection(self):
        logger.info("Shutting down client connection at %s:%d", self.server_host, self.server_port,)
        self.writer.close()
        await self.writer.wait_closed()

    async def send_messages(self):
        while True:
            logger.info("Processing console input")
            if message := await aioconsole.ainput("~~~ "):
                self.writer.write(message.encode('utf-8'))
                await self.writer.drain()

    async def receive_messages(self):
        while message := (await self.reader.read(1024)).decode():
            logger.info("Message is received: %s", message)
            await aioconsole.aprint(message)


if __name__ == '__main__':
    logger.info("Starting client connection")
    client = Client()
    asyncio.run(client.connect_to_server())
