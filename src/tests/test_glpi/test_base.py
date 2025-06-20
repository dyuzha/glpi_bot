# glpi_bot/glpi/tests/test_base.py

import pytest
from aioresponses import aioresponses

from glpi_bot.glpi.base import GLPIBase, GLPIAPIError, GLPIUnauthorizedError
from glpi_bot.glpi.session import GLPISessionManager
from tests.test_env import GLPIEnv


@pytest.fixture
async def session_manager():
    manager = GLPISessionManager(
        url=GLPIEnv.URL,
        app_token=GLPIEnv.APP_TOKEN,
        username=GLPIEnv.USERNAME,
        password=GLPIEnv.PASSWORD,
    )
    manager._session_token = "session_token"
    yield manager
    await manager.shutdown()


async def test_init(session_manager):
    assert session_manager.url == GLPIEnv.URL
    assert session_manager._app_token == GLPIEnv.APP_TOKEN
    assert session_manager._auth_data == {
        'login': GLPIEnv.USERNAME,
        'password': GLPIEnv.PASSWORD,
        'app_token': GLPIEnv.APP_TOKEN
    }
    assert session_manager._session_token == "session_token"
    assert session_manager._token_expires is None


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
async def test_make_request_success(method, session_manager):
    base = GLPIBase(session_manager)

    with aioresponses() as m:
        getattr(m, method.lower())(
            url=f"{GLPIEnv.URL}/Ticket",
            status=200,
            payload={"data": f"{method.lower()}_ok"},
        )

        response = await base._make_request(method, "Ticket")
        assert response == {"data": f"{method.lower()}_ok"}


async def test_get_unauthrized(session_manager):
    session_manager._session_token = None
    base = GLPIBase(session_manager)

    with pytest.raises(GLPIUnauthorizedError):
        await base.get("Ticket")


async def test_get_api_error(session_manager):
    session_manager._session_token = "session_token"
    base = GLPIBase(session_manager)

    with aioresponses() as m:
        m.get(
                f"{GLPIEnv.URL}/Ticket",
                payload={"message": "Bad request"},
                status=400,
                )

        with pytest.raises(GLPIAPIError) as e:
            await base.get("Ticket")

        assert "Bad request" in str(e.value)
        assert e.value.status_code == 400


async def test_get_smoke(session_manager):
    base = GLPIBase(session_manager)

    with aioresponses() as m:
        m.get(f"{GLPIEnv.URL}/Ticket", payload={"data": "ok"}, status=200)
        result = await base.get("Ticket")
        assert result is not None
