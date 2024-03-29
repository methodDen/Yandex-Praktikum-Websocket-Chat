import asyncio

from config import (
    SERVER_HOST,
    SERVER_PORT,
    REPORTS_COUNT_LIMIT,
    BAN_TIME,
    HELP_MESSAGE,
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
        self.message_history: list[str] = []

    async def listen(self):
        server = await asyncio.start_server(
            self.process_client, self.host, self.port,
        )
        logger.info("Server is initialized at %s", server.sockets[0].getsockname())
        async with server:
            try:
                await server.serve_forever()
            except asyncio.CancelledError:
                logger.info("Server is shutting down")
                await self.disconnect_all_clients()
                server.close()
                await server.wait_closed()

    async def process_client(self, reader: StreamReader, writer: StreamWriter):
        logger.info("Client %s has connected to the server", writer.get_extra_info("peername"))
        user = ServerUser(reader, writer)
        self.online_users[user.username] = user
        welcome_message = get_welcome_message(user.username)
        await user.send_message(welcome_message)
        await self.show_history(user)
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
                username: str | None = message_elements[1] if len(message_elements) > 1 else None
            case CommandName.DM:
                username: str = message_elements[1]
                message: str = ' '.join(message_elements[2:])
            case CommandName.CHANGE_USERNAME:
                username: str | None = message_elements[1] if len(message_elements) > 1 else None
            case CommandName.POSTPONE:
                seconds_for_delay: int = int(message_elements[1])
                message: str = ' '.join(message_elements[2:])
            case _:
                message: str = command_name
                command_name: str = CommandName.UNKNOWN

        return Command(command_name, username, message, seconds_for_delay)

    async def process_message(self, user: ServerUser):
        while message := await user.receive_message():
            if message:
                logger.info("Received a message from %s: %s", user.username, message)
                if user.report_count < REPORTS_COUNT_LIMIT:
                    if message.startswith('/'):
                        command = self.parse_message(message.strip())
                        logger.info("Command %s is received from %s", command.command_name, user.username)
                        match command.command_name:
                            case CommandName.HELP:
                                await user.send_message(
                                    HELP_MESSAGE,
                                )
                            case CommandName.HISTORY:
                                await self.show_history(user)
                            case CommandName.REPORT:
                                await self.report_user(command.username, user)
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
                                logger.info("Postpone command is received from %s", user.username)
                                loop = asyncio.get_event_loop()
                                loop.call_later(
                                    command.seconds_for_delay,
                                    lambda: asyncio.create_task(
                                        self.send_message_to_everyone(
                                            command.message,
                                            user.username
                                        )
                                    )
                                )
                                await user.send_message(f"Message will be sent in {command.seconds_for_delay} seconds")
                            case CommandName.UNKNOWN:
                                logger.info("Unknown command is received from %s", user.username)
                                await user.send_message(
                                    f"Unknown command: {command.message if command.message else 'empty command'}"
                                )
                    else:
                        logger.info("Public message is received from %s", user.username)
                        await self.send_message_to_everyone(message, user.username,)
                else:
                    logger.info("User %s is banned", user.username)
                    await user.send_message(f"You are banned, cannot send messages")
        await self.disconnect_client(user, user.writer)

    async def send_message_to_everyone(self, message: str, from_username: str,):
        message = await prepare_message(
            message,
            MessageType.PUBLIC,
            from_username,
            self.online_users,
        )
        if message:
            self.message_history.append(message)
            for user in self.online_users.values():
                await user.send_message(message)

    async def send_message_to_dm(self, message: str, from_username: str, to_username: str,):
        message = await prepare_message(
            message,
            MessageType.PRIVATE,
            from_username,
            self.online_users,
        )
        from_user = self.online_users.get(from_username)
        to_user = self.online_users.get(to_username)
        if to_user:
            if from_username == to_username:
                await from_user.send_message(f"Cannot send messages to yourself!")
            else:
                if message:
                    await to_user.send_message(message)
        else:
            await from_user.send_message(f"User {to_username} is not online")

    async def change_username(self, new_username: str, user: ServerUser) -> None:
        if new_username is None or new_username.strip() == '':
            await user.send_message(f"Username cannot be empty")
            return
        elif new_username == user.username:
            await user.send_message(f"Username is already {new_username}")
            return
        elif new_username in self.online_users:
            await user.send_message(f"Username {new_username} is already taken")
            return
        old_username = user.username
        user.username = new_username
        self.online_users.pop(old_username)
        self.online_users[new_username] = user
        await user.send_message(f"Your username is changed to {new_username}")

    async def report_user(self, username: str, from_user: ServerUser, ) -> None:
        if username is None or username.strip() == '':
            await from_user.send_message(f"Username cannot be empty")
            return
        elif username == from_user.username:
            await from_user.send_message(f"Cannot report yourself")
            return

        user = self.online_users.get(username)
        if not user:
            await from_user.send_message(f"User {username} is not online")
            return
        user.report_count += 1
        await user.send_message(f"You are reported by {from_user.username}")
        if user.report_count >= REPORTS_COUNT_LIMIT:
            logger.info("User %s is banned", username)
            await user.send_message(f"\nYou are banned for {BAN_TIME} seconds")
            loop = asyncio.get_event_loop()
            loop.call_later(
                BAN_TIME,
                lambda: asyncio.create_task(
                    self.unban_user(user)
                )
            )

    @staticmethod
    async def unban_user(user: ServerUser,) -> None:
        user.report_count = 0
        await user.send_message(f"\nYou are unbanned")

    async def show_history(self, user: ServerUser,) -> None:
        logger.info("History is requested by %s", user.username)
        for message in self.message_history[-20:]:
            await user.send_message(f'{message}\n')

    async def disconnect_client(self, user: ServerUser, writer: StreamWriter,):
        logger.info(
            "Client %s has disconnected",
            writer.get_extra_info("peername"),
        )
        self.online_users.pop(user.username)
        writer.close()
        await writer.wait_closed()

    async def disconnect_all_clients(self,):
        tasks = []
        for user in self.online_users.values():
            tasks.append(self.disconnect_client(user, user.writer))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    logger.info("Starting server")
    server = Server()
    try:
        asyncio.run(server.listen())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected, server is shutting down")

"""

От автора проекта: 

Доброго времени суток!
Похоже, что та проблема, которая была в переподключении клиента к серверу, была связана с тем, что я не закрывал 
соединение в сокетах.
Прямо сейчас я схэндлил эту проблему, и все более менее работает. 
Однако, иногда проблема с отправкой данных с клиента на сервер все еще возникает, но это по моим предположениям
возникает из-за самих сокетов, не из-за кода.

"""