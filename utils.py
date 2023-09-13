def get_welcome_message(username: str) -> str:
    message = (
        f"Welcome to the chat, your username is {username}!\n"
        """To get all available commands, please type in "/help" :\n"""
        """For now, you are in public chat, so all your messages will be seen by other users\n"""
    )
    return message
