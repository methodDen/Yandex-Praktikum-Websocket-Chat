from datetime import datetime
from config import TIME_FORMAT


def get_welcome_message(username: str) -> str:
    message = (
        f"Welcome to the chat, your username is {username}!\n"
        """To get all available commands, please type in "/help" :\n"""
        """For now, you are in public chat, so all your messages \n"""
        """will be seen by other online users\n"""
    )
    return message


def setup_message(message_type: str, message: str) -> str:
    now = datetime.now()
    current_time = now.strftime(TIME_FORMAT)
    formatted_message = f"|{message_type}|{current_time}|{message}"
    return formatted_message
