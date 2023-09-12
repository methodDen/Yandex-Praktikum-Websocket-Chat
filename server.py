import asyncio

from config import (
    SERVER_HOST,
    SERVER_PORT, REPORTS_COUNT_LIMIT,
)
from asyncio import (
    StreamReader,
    StreamWriter,
)
from logger import logger
from utils import get_welcome_message
from models import (
    ServerUser,
    Command,
)


class Server:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT,):
        self.host = host
        self.port = port

    async def listen(self):
        try:
            server = await asyncio.start_server(
                self.process_client, self.host, self.port,
            )
            logger.info("Server is initialized at %s", server.sockets[0].getsockname())
            async with server:
                await server.serve_forever()
        except Exception as e:
            logger.error("Error detected: %s", e)
        except KeyboardInterrupt:
            logger.info("Shutting down the server")

    async def process_client(self, reader: StreamReader, writer: StreamWriter):
        # add client
        logger.info("Client %s has connected to the server", writer.get_extra_info("peername"))
        user = ServerUser(reader, writer)
        welcome_message = get_welcome_message(user.username)
        await user.send_message(welcome_message)
        await self.process_message(user)

    async def process_message(self, user: ServerUser):
        while True:
            message = await user.receive_message()
            if message:
                logger.info("Received a message from %s: %s", user.username, message)
                if user.report_count < REPORTS_COUNT_LIMIT:
                    if message.startswith('/'):
                        command = self.parse_message(message)
                else:
                    # send ban message
                    pass

    def parse_message(self, message: str):
        print(message.split(' '))
        command = Command(message.split(' '))
        print(command)
        return None


if __name__ == '__main__':
    logger.info("Starting server")
    server = Server()
    asyncio.run(server.listen())