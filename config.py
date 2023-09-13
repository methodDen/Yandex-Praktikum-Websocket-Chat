from enum import Enum
from decouple import config

SERVER_HOST = config("SERVER_HOST", default="127.0.0.1", cast=str)
SERVER_PORT = config("SERVER_PORT", default=8080, cast=int)
REPORTS_COUNT_LIMIT = config("REPORTS_COUNT_LIMIT", default=3, cast=int)
TIME_FORMAT = config("TIME_FORMAT", default="%H:%M:%S", cast=str)


class CommandName(str, Enum):
    HELP = 'help'
    HISTORY = 'history'
    CHANGE_USERNAME = 'change_username'
    DM = 'dm'
    REPORT = 'report'
    POSTPONE = 'postpone'
    QUIT = 'quit'
    UNKNOWN = 'unknown'


class MessageType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    BANNED = "banned"
