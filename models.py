from asyncio import (
    StreamReader,
    StreamWriter,
)
from enum import Enum
from collections import namedtuple


class ServerUser:
    def __init__(self, reader: StreamReader, writer: StreamWriter, report_count: int = 0):
        self.reader = reader
        self.writer = writer
        self.report_count = report_count
        self.username = f'username_{id(self)}'

    async def send_message(self, message: str):
        self.writer.write(message.encode('utf-8'))
        await self.writer.drain()

    async def receive_message(self) -> str:
        return (await self.reader.read(1024)).decode("utf-8")


class CommandName(str, Enum):
    HELP = 'help'
    HISTORY = 'history'
    CHANGE_USERNAME = 'change_username'
    DM = 'dm'
    REPORT = 'report'
    POSTPONE = 'postpone'
    QUIT = 'quit'
    UNKNOWN = 'unknown'


Command = namedtuple('Command', ['command_name', 'username', 'message', 'seconds_for_delay'])
