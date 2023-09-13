from enum import Enum
from decouple import config

SERVER_HOST = config("SERVER_HOST", default="127.0.0.1", cast=str)
SERVER_PORT = config("SERVER_PORT", default=8080, cast=int)
REPORTS_COUNT_LIMIT = config("REPORTS_COUNT_LIMIT", default=3, cast=int)
TIME_FORMAT = config("TIME_FORMAT", default="%H:%M:%S", cast=str)
BAN_TIME = config("BAN_TIME", default=30, cast=int)


class CommandName(str, Enum):
    HELP = 'help'
    HISTORY = 'history'
    CHANGE_USERNAME = 'change_username'
    DM = 'dm'
    REPORT = 'report'
    POSTPONE = 'postpone'
    UNKNOWN = 'unknown'


class MessageType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    BANNED = "banned"
    WARNING = "warning"


HELP_MESSAGE = (
    "\nAvailable commands:\n"
    "/help — get a list of commands\n"
    "/history — chat history\n"
    "/change_username <new_username> — change your username\n"
    "/dm <username> <message> — send a private message\n"
    "/report <username> — report a user\n"
    "/postpone <seconds> <message> — postpone message sending\n"
    "The project was created by Daniyar Absatov\n"
    "All rights reserved (c) 2023\n"
)