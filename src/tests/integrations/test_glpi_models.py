import pytest
from glpi_bot.glpi.models import GLPIInterface, GLPIUser
from glpi_bot.glpi.session import GLPISessionManager
from tests.test_env import GLPIEnv

USERNAME="dyuzhev_mn"

import logging

logger = logging.getLogger(__name__)


@pytest.fixture
async def session_manager():
    manager = GLPISessionManager(
        url=GLPIEnv.URL,
        app_token=GLPIEnv.APP_TOKEN,
        username=GLPIEnv.USERNAME,
        password=GLPIEnv.PASSWORD,
    )
    yield manager
    await manager.shutdown()


async def test_create_ticket_integration(session_manager):
    async with session_manager.get_session() as session:
        data = {"login": "dyuzhev_mn",
                "name": "test",
                "content": "test content",
                "type": "1",
                "itilcategories_id": "1",
                }
        interface = GLPIInterface(session)
        await interface.create_ticket(**data)


async def test_get_user_found_integration(session_manager):
    async with session_manager.get_session() as session:
        interface = GLPIInterface(session)
        user = await interface.get_user(USERNAME)
        assert user is not None
        assert isinstance(user, GLPIUser)


async def test_get_all_entities_integration(session_manager, caplog):
    caplog.set_level(logging.DEBUG)

    async with session_manager.get_session() as session:
        interface = GLPIInterface(session)
        entities = await interface.get_all_entities()
        assert isinstance(entities, dict)
        for id, org in entities.items():
            logger.debug(f"{id}: {org}")
