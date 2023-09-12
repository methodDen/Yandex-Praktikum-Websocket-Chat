def get_welcome_message(username: str) -> str:
    message = (
        f"Welcome to the chat, {username}!\n"
        """To get all available commands, please type in "/help" :\n"""
    )
    return message
