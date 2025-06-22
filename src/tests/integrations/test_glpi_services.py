from _pytest.mark.structures import _ParametrizeMarkDecorator
import pytest

from tests.test_env import GLPIEnv

from glpi_bot.glpi.session import GLPISessionManager
from glpi_bot.services.glpi_service import (
    TicketData, GLPITicketManager, OrganisationCache
)


@pytest.mark.parametrize("login", ["dyuzhev_mn", "admin"])
async def test_send_ticket_integration(login):
    session_manager = GLPISessionManager(
        url=GLPIEnv.URL,
        app_token=GLPIEnv.APP_TOKEN,
        username=GLPIEnv.USERNAME,
        password=GLPIEnv.PASSWORD,
    )

    org_cache = OrganisationCache(session_manager)
    manager = GLPITicketManager(session_manager, org_cache)

    ticket_data = TicketData(
        login=login,  # существующий логин
        name="Integration Test Ticket",
        content="Тестовая заявка, созданная автотестом",
        type=1,  # incident or request
        itilcategories_id=1,  # существующий ID категории
    )

    result = await manager.send_ticket(ticket_data)

    assert isinstance(result, dict)
    assert "id" in result
    print(f"Создана заявка: {result['id']}")
