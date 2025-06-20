# tests/test_glpi/test_models.py

import pytest
from unittest.mock import AsyncMock
from glpi_bot.glpi.models import GLPIInterface, GLPIUser
from glpi_bot.glpi.session import GLPISessionManager
from tests.test_env import GLPIEnv


@pytest.fixture
async def interface():
    session = GLPISessionManager(
        url=GLPIEnv.URL,
        app_token=GLPIEnv.APP_TOKEN,
        username=GLPIEnv.USERNAME,
        password=GLPIEnv.PASSWORD,
    )
    iface = GLPIInterface(session)
    return iface


@pytest.mark.asyncio
async def test_get_user_found(interface):
    login = "test_user"
    payload = {
        "totalcount": 1,
        "data": [{"1": login, "2": 42, "3": "Org"}]
    }
    interface.post = AsyncMock(return_value=payload)

    user = await interface.get_user(login)

    assert isinstance(user, GLPIUser)
    assert user._login == login
    assert user.id == 42
    assert user.organisation == "Org"


@pytest.mark.asyncio
async def test_get_user_not_found(interface):
    login = "ghost"
    payload = {
        "totalcount": 0,
        "data": []
    }
    interface.post = AsyncMock(return_value=payload)

    user = await interface.get_user(login)

    assert user is None


@pytest.mark.asyncio
async def test_get_all_users(interface):
    payload = {
        "data": [
            {"1": "user1", "2": 1, "3": "Org1"},
            {"1": "user2", "2": 2, "3": "Org2"}
        ]
    }
    interface.post = AsyncMock(return_value=payload)

    users = await interface.get_all_users()

    assert isinstance(users, list)
    assert len(users) == 2
    assert users[0]._login == "user1"
    assert users[1].id == 2


@pytest.mark.asyncio
async def test_create_ticket(interface):
    ticket_data = {"id": 123}
    interface.post = AsyncMock(return_value=ticket_data)

    result = await interface.create_ticket(name="Test Ticket")

    assert result == ticket_data


@pytest.mark.asyncio
async def test_get_all_entities(interface):
    payload = {
        "data": [
            {"1": "0 > Org1", "2": "Org1 Name"},
            {"1": "1 > Org2", "2": "Org2 Name"},
        ]
    }
    interface.post = AsyncMock(return_value=payload)

    result = await interface.get_all_entities()

    assert isinstance(result, dict)
    assert result == {
        "Org1": "Org1 Name",
        "Org2": "Org2 Name"
    }
