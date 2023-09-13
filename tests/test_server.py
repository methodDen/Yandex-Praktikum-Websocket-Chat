from datetime import datetime

import pytest
from asyncio import StreamReader, StreamWriter
from unittest.mock import AsyncMock
from server import Server


@pytest.fixture
def server():
    return Server()


@pytest.fixture
def mock_reader_writer():
    reader = AsyncMock(spec=StreamReader)
    writer = AsyncMock(spec=StreamWriter)
    return reader, writer


@pytest.mark.asyncio
async def test_parse_message(server):
    message = "/help"
    command = server.parse_message(message)
    assert command.command_name == "help"

    message = "/report username"
    command = server.parse_message(message)
    assert command.command_name == "report"
    assert command.username == "username"


@pytest.mark.asyncio
async def test_send_message_to_everyone(server):
    user1 = AsyncMock()
    user1.username = "user1"
    user2 = AsyncMock()
    user2.username = "user2"

    server.online_users = {"user1": user1, "user2": user2}
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    await server.send_message_to_everyone("Test message", "user1")
    assert f'|public|{current_time}|user1: Test message' in server.message_history


@pytest.mark.asyncio
async def test_change_username(server):
    user = AsyncMock()
    user.username = "user1"

    server.online_users = {"user1": user}

    await server.change_username("new_username", user)

    assert user.username == "new_username"
    assert "user1" not in server.online_users
    assert "new_username" in server.online_users


@pytest.mark.asyncio
async def test_report_user(server):
    from_user = AsyncMock()
    from_user.username = "from_user"
    to_user = AsyncMock()
    to_user.username = "to_user"
    to_user.report_count = 0

    server.online_users = {"from_user": from_user, "to_user": to_user}

    await server.report_user("to_user", from_user)

    assert to_user.report_count == 1


@pytest.mark.asyncio
async def test_unban_user(server):
    user = AsyncMock()
    user.report_count = 3

    await server.unban_user(user)

    assert user.report_count == 0
