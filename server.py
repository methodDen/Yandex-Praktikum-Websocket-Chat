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
    CommandName,
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

    @staticmethod
    def parse_message(message: str):
        message_elements = message.split(' ')
        command_name = message_elements[0][1:]
        username = message = seconds_for_delay = None
        match command_name:
            case CommandName.HELP:
                pass
            case CommandName.HISTORY:
                pass
            case CommandName.REPORT:
                username: str = message_elements[1]
            case CommandName.DM:
                username: str = message_elements[1]
                message: str = ' '.join(message_elements[2:])
            case CommandName.CHANGE_USERNAME:
                username: str = message_elements[1]
            case CommandName.POSTPONE:
                username: str = message_elements[1]
                seconds_for_delay: int = int(message_elements[2])
                message: str = ' '.join(message_elements[3:])
            case CommandName.QUIT:
                pass
            case _:
                command_name = CommandName.UNKNOWN

        return Command(command_name, username, message, seconds_for_delay)

    async def process_message(self, user: ServerUser):
        while True:
            message = await user.receive_message()
            if message:
                logger.info("Received a message from %s: %s", user.username, message)
                if user.report_count < REPORTS_COUNT_LIMIT:
                    if message.startswith('/'):
                        command = self.parse_message(message.strip())
                        logger.info("Command %s is received from %s", command.command_name, user.username)
                        match command.command_name:
                            case CommandName.HELP:
                                pass
                            case CommandName.HISTORY:
                                pass
                            case CommandName.REPORT:
                                pass
                            case CommandName.DM:
                                pass
                            case CommandName.CHANGE_USERNAME:
                                pass
                            case CommandName.POSTPONE:
                                pass
                            case CommandName.QUIT:
                                pass
                            case CommandName.UNKNOWN:
                                pass
                    else:
                        pass
                else:
                    pass


if __name__ == '__main__':
    logger.info("Starting server")
    server = Server()
    asyncio.run(server.listen())
