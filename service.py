from datetime import datetime
from config import (
    TIME_FORMAT,
    MessageType,
)


def get_welcome_message(username: str) -> str:
    message = (
        f"Welcome to the chat!"
        f" Нour username is {username}!\n"
        """To get all available commands, please type in "/help"\n"""
        "For now, you are in public chat, so all your messages\n"
        "will be seen by other online users\n"
    )
    return message


def add_message_author(message: str, username: str) -> str:
    return f"{username}: {message}"


def setup_message(message_type: str, message: str) -> str:
    now = datetime.now()
    current_time = now.strftime(TIME_FORMAT)
    formatted_message = f"|{message_type}|{current_time}|{message}"
    return formatted_message


async def prepare_message(
        message: str,
        message_type: MessageType,
        from_username: str,
        online_users: dict = None,
) -> str | None:
    message = message.strip()
    if message == '':
        current_user = online_users.get(from_username)
        await current_user.send_message("Cannot send empty message!")
        return
    else:
        message_with_author = add_message_author(message, from_username, )
        formatted_message = None
        if message_type == MessageType.PUBLIC:
            formatted_message = setup_message(MessageType.PUBLIC, message_with_author, )
        elif message_type == MessageType.PRIVATE:
            formatted_message = setup_message(MessageType.PRIVATE, message_with_author, )
        return formatted_message
