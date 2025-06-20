import pytest

from tests.conftest import session_manager
from tests.test_env import GLPIEnv


pytestmark = pytest.mark.integration


async def test_init(session_manager):
    assert session_manager.url == GLPIEnv.URL
    assert session_manager._app_token == GLPIEnv.APP_TOKEN
    assert session_manager._auth_data == {
        'login': GLPIEnv.USERNAME,
        'password': GLPIEnv.PASSWORD,
        'app_token': GLPIEnv.APP_TOKEN
    }
    assert session_manager._session_token is None
    assert session_manager._token_expires is None


async def test_live_session_creation_and_kill(session_manager):
    async with session_manager.get_session() as manager:
        assert manager._session_token is not None, "Session token should not be None"
        assert manager._token_expires is not None, "Token expiration should be set"

    # assert manager._session_token is not None
