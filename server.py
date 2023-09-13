import asyncio
from config import (
    SERVER_HOST,
    SERVER_PORT,
    REPORTS_COUNT_LIMIT,
    CommandName,
    MessageType,
)
from asyncio import (
    StreamReader,
    StreamWriter,
)
from logger import logger
from service import (
    get_welcome_message,
    prepare_message,
)
from models import (
    ServerUser,
    Command,
)


class Server:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT,):
        self.host: str = host
        self.port: int = port
        self.online_users: dict[str, ServerUser] = {}

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
        logger.info("Client %s has connected to the server", writer.get_extra_info("peername"))
        user = ServerUser(reader, writer)
        self.online_users[user.username] = user
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
                username: str | None = message_elements[1] if len(message_elements) > 1 else None
            case CommandName.POSTPONE:
                seconds_for_delay: int = int(message_elements[1])
                message: str = ' '.join(message_elements[2:])
            case CommandName.QUIT:
                pass
            case _:
                message: str = command_name
                command_name: str = CommandName.UNKNOWN

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
                                logger.info("DM command is received from %s", user.username)
                                await self.send_message_to_dm(
                                    command.message,
                                    user.username,
                                    command.username,
                                )
                            case CommandName.CHANGE_USERNAME:
                                await self.change_username(command.username, user)
                            case CommandName.POSTPONE:
                                pass
                            case CommandName.QUIT:
                                pass
                            case CommandName.UNKNOWN:
                                logger.info("Unknown command is received from %s", user.username)
                                await user.send_message(
                                    f"Unknown command: {command.message if command.message else 'empty command'}"
                                )
                    else:
                        logger.info("Public message is received from %s", user.username)
                        await self.send_message_to_everyone(message, user.username,)
                else:
                    # user is banned
                    pass

    # main functionality
    async def send_message_to_everyone(self, message: str, from_username: str,):
        message = await prepare_message(
            message,
            MessageType.PUBLIC,
            from_username,
            self.online_users,
        )
        if message:
            for user in self.online_users.values():
                await user.send_message(message)

    async def send_message_to_dm(self, message: str, from_username: str, to_username: str,):
        message = await prepare_message(
            message,
            MessageType.PRIVATE,
            from_username,
            self.online_users,
        )
        user = self.online_users.get(to_username)
        if user:
            if from_username == to_username:
                await user.send_message(f"Cannot send messages to yourself!")
            else:
                if message:
                    await user.send_message(message)
        else:
            await user.send_message(f"User {to_username} is not online")

    async def change_username(self, new_username: str, user: ServerUser) -> None:
        if new_username is None or new_username.strip() == '':
            await user.send_message(f"Username cannot be empty")
            return
        elif new_username == user.username:
            await user.send_message(f"Username is already {new_username}")
            return
        old_username = user.username
        user.username = new_username
        self.online_users.pop(old_username)
        self.online_users[new_username] = user
        await user.send_message(f"Your username is changed to {new_username}")


if __name__ == '__main__':
    logger.info("Starting server")
    server = Server()
    asyncio.run(server.listen())
