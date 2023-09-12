from decouple import config

SERVER_HOST = config("SERVER_HOST", default="127.0.0.1", cast=str)
SERVER_PORT = config("SERVER_PORT", default=8000, cast=int)