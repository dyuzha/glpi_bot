import pytest

from tests.test_env import GLPIEnv

from glpi_bot.glpi.session import GLPISessionManager
from glpi_bot.services.glpi_service import (
    TicketData, GLPITicketManager, OrganisationCache
)


@pytest.mark.asyncio
async def test_send_ticket_integration():
    session_manager = GLPISessionManager(
        url=GLPIEnv.URL,
        app_token=GLPIEnv.APP_TOKEN,
        username=GLPIEnv.USERNAME,
        password=GLPIEnv.PASSWORD,
    )

    org_cache = OrganisationCache(session_manager)
    manager = GLPITicketManager(session_manager, org_cache)

    ticket_data = TicketData(
        login="admin",  # существующий логин
        name="Integration Test Ticket",
        content="Тестовая заявка, созданная автотестом",
        type=1,  # incident or request
        itilcategories_id=1,  # существующий ID категории
    )

    result = await manager.send_ticket(ticket_data)

    assert isinstance(result, dict)
    assert "id" in result
    print(f"Создана заявка: {result['id']}")
