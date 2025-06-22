# tests/services/test_glpiservice.py
# Не работают

import pytest
from unittest.mock import AsyncMock, MagicMock

from glpi_bot.services.glpi_service import (
    TicketData,
    GLPITicketManager,
    OrganisationCache,
    REQUEST_TYPE_TELEGRAM
)
from glpi_bot.glpi.models import GLPIUser



async def test_send_ticket_success():

    # Arrange
    mock_session_manager = MagicMock()
    mock_session = MagicMock()
    mock_interface = AsyncMock()
    mock_user = GLPIUser(id=1, name="Test User", organisation="Test Org")

    # Контекстный менеджер
    mock_session_manager.get_session.return_value.__aenter__.return_value = mock_session
    mock_interface_cls = AsyncMock(return_value=mock_interface)

    mock_interface.get_user.return_value = mock_user
    mock_interface.get_all_entities.return_value = {"Test Org": 123}
    mock_interface.create_ticket.return_value = {"id": 42}

    org_cache = OrganisationCache(mock_session_manager)
    org_cache.load = AsyncMock(return_value={"Test Org": 123})

    ticket_data = TicketData(
        login="testuser",
        name="Ticket Title",
        content="Ticket Content",
        type=1,
        itilcategories_id=5
    )

    manager = GLPITicketManager(mock_session_manager, org_cache)

    # patch interface to return our mock
    GLPIInterface_mock = AsyncMock(return_value=mock_interface)

    # Act
    result = await manager.send_ticket(ticket_data)

    # Assert
    assert result == {"id": 42}
    mock_interface.get_user.assert_awaited_once_with("testuser")
    mock_interface.create_ticket.assert_awaited_once_with(
        name="Ticket Title",
        content="Ticket Content",
        type=1,
        requesttypes_id=REQUEST_TYPE_TELEGRAM,
        itilcategories_id=5,
        _users_id_requester=1,
        entities_id=123,
    )



async def test_send_ticket_user_not_found():
    mock_session_manager = MagicMock()
    mock_interface = AsyncMock()
    mock_interface.get_user.return_value = None

    mock_session_manager.get_session.return_value.__aenter__.return_value = MagicMock()

    org_cache = OrganisationCache(mock_session_manager)
    org_cache.get = AsyncMock()

    manager = GLPITicketManager(mock_session_manager, org_cache)

    ticket_data = TicketData(
        login="missinguser",
        name="Ticket Title",
        content="Ticket Content",
        type=1,
        itilcategories_id=5
    )

    with pytest.raises(ValueError, match="Пользователь 'missinguser' не найден"):
        await manager.send_ticket(ticket_data)


async def test_send_ticket_unknown_org():
    mock_session_manager = MagicMock()
    mock_session = MagicMock()
    mock_user = GLPIUser(id=2, name="NoOrg User", organisation="Unknown Org")

    mock_interface = AsyncMock()
    mock_interface.get_user.return_value = mock_user
    mock_interface.get_all_entities.return_value = {"Other Org": 456}

    mock_session_manager.get_session.return_value.__aenter__.return_value = mock_session

    org_cache = OrganisationCache(mock_session_manager)
    org_cache.get = AsyncMock(return_value={"Other Org": 456})

    manager = GLPITicketManager(mock_session_manager, org_cache)

    ticket_data = TicketData(
        login="noorguser",
        name="Title",
        content="Content",
        type=1,
        itilcategories_id=5
    )

    with pytest.raises(ValueError, match="Организация 'Unknown Org' не найдена"):
        await manager.send_ticket(ticket_data)
