# tests/test_session.py

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from aioresponses import aioresponses
from yarl import URL


from glpi_bot.glpi.session import GLPISessionManager
from tests.test_env import GLPIEnv
import aiohttp


pytestmark = pytest.mark.asyncio

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


@pytest.fixture
def frozen_now():
    return datetime(2023, 1, 1, 12, 0, 0)


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


async def test_token_expiration(session_manager, frozen_now):
    with patch("glpi_bot.glpi.session.datetime") as mock_datetime:
        mock_datetime.now.return_value = frozen_now
        session_manager._token_expires = frozen_now - timedelta(seconds=1)
        assert session_manager._is_token_expired() is True


async def test_open_session_success(session_manager, frozen_now):
    with aioresponses() as m:
        m.post(
            f"{GLPIEnv.URL}/initSession",
            payload={'session_token': 'test_session_token'},
            status=200
        )

        with patch("glpi_bot.glpi.session.datetime") as mock_datetime:
            mock_datetime.now.return_value = frozen_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            await session_manager._open_session()
            assert session_manager._session_token == 'test_session_token'
            assert session_manager._token_expires == frozen_now + timedelta(minutes=5)


async def test_open_session_failure(session_manager):
    with aioresponses() as m:
        m.post(
            f"{GLPIEnv.URL}/initSession",
            status=401
        )

        with pytest.raises(ConnectionError):
            await session_manager._open_session()
        assert session_manager._session_token is None


async def test_close_session_success(session_manager):
    session_manager._session_token = 'test_session_token'

    with aioresponses() as m:
        m.get(
            f"{GLPIEnv.URL}/killSession",
            status=200
        )

        await session_manager._close_session()
        assert session_manager._session_token is None
        assert session_manager._token_expires is None


async def test_close_session_failure(session_manager, caplog):
    session_manager._session_token = "test_token"

    with aioresponses() as m:
        m.get(
            f"{GLPIEnv.URL}/killSession",
            exception= aiohttp.ClientConnectionError("fail")
        )

        await session_manager._close_session()
        assert "Не удалось закрыть сессию" in caplog.text
        assert session_manager._session_token is None


async def test_force_kill_previous_session(session_manager):
    session_manager._session_token = "old_token"

    with aioresponses() as m:
        m.post(
            URL(f"{GLPIEnv.URL}/killSession"),
            status=200,
            # headers={"Session-Token": "old_token"}
        )

        await session_manager._force_kill_previous_session()


async def test_context_manager_success(session_manager):
    with aioresponses() as m:
        m.post(
            f"{GLPIEnv.URL}/initSession",
            payload={'session_token': 'test_token'},
            status=200
        )
        m.get(
            f"{GLPIEnv.URL}/killSession",
            status=200
        )

        async with session_manager.get_session() as sm:
            assert sm._session_token == 'test_token'
            assert sm._token_expires is not None


@pytest.mark.parametrize(
    "initial_token, ttl, expected_new_token",
    [
        (None, None, True),
        ("old_token", datetime.now() - timedelta(seconds=1), True),
        ("old_token", datetime.now() + timedelta(minutes=1), False),
    ]
)
async def test_get_new_token(
        session_manager,
        initial_token,
        ttl,
        expected_new_token,
        frozen_now):
    with patch("glpi_bot.glpi.session.datetime") as mock_datetime:
        mock_datetime.now.return_value = frozen_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        session_manager._session_token = initial_token
        session_manager._token_expires = ttl


    with aioresponses() as m:
        # m.get(
        #     f"{GLPIEnv.URL}/killSession",
        #     status=200
        #     )
        m.post(
            f"{GLPIEnv.URL}/initSession",
            payload={"session_token": "new_token"},
            status=200
            )

        async with session_manager.get_session() as sm:
            token_changed = sm._session_token != initial_token
            assert token_changed is expected_new_token
