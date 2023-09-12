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
        return (await self.reader.read(1024)).decode()


Command = namedtuple('Command', ['command_name', 'val_1', 'val_2'])
