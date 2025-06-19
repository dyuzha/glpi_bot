# tests/test_session.py

import pytest
import requests
from datetime import datetime, timedelta
from unittest.mock import patch

from glpi_bot.glpi.session import GLPISessionManager
from tests.test_env import GLPIEnv


@pytest.fixture
def session_manager():
    return GLPISessionManager(
        url=GLPIEnv.URL,
        app_token=GLPIEnv.APP_TOKEN,
        username=GLPIEnv.USERNAME,
        password=GLPIEnv.PASSWORD,
    )


@pytest.fixture
def frozen_now():
    """Фиксированная дата для тестов"""
    return datetime(2023, 1, 1, 12, 0, 0)


def test_init(session_manager):
    assert session_manager.url == GLPIEnv.URL
    assert session_manager._app_token == GLPIEnv.APP_TOKEN
    assert session_manager._auth_data == {
        'login': GLPIEnv.USERNAME,
        'password': GLPIEnv.PASSWORD,
        'app_token': GLPIEnv.APP_TOKEN
    }
    assert session_manager._session_token is None
    assert session_manager._token_expires is None


def test_token_expiration(session_manager, frozen_now):
    with patch("glpi_bot.glpi.session.datetime") as mock_datetime:
        mock_datetime.now.return_value = frozen_now
        session_manager._token_expires = frozen_now - timedelta(seconds=1)
        assert session_manager._is_token_expired() is True


def test_open_session_success(requests_mock, session_manager, frozen_now):

    # Подготавливаем мок-ответ API
    mock_response = {
        'session_token': 'test_session_token'
    }

    requests_mock.post(
        f"{GLPIEnv.URL}/initSession",
        json=mock_response,
        status_code=200
    )


    # Заменяем модуль datetime.datetime подменным модулем
    with patch("glpi_bot.glpi.session.datetime") as mock_datetime:
        # Подменяем текущую дату на конкретную (фиксированную)
        mock_datetime.now.return_value = frozen_now

        # Если кто-то вызовет datetime(...), не мок возвращай, а вызови реальный datetime.
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        # Делает патч безопасным: ты замещаешь только datetime.now(),
        # а всё остальное (например datetime(2023, 1, 1)) продолжает работать
        # как обычный Python datetime.

        # Вызываем тестируемый метод
        # (внутри него будет использоваться подменный datetime.now())
        session_manager._open_session()

        # Проверка токена
        assert session_manager._session_token == 'test_session_token'
        # Проверка времени истечения токена
        assert session_manager._token_expires == frozen_now + timedelta(minutes=5)


def test_open_session_failure(requests_mock, session_manager):
    session_manager._session_token = 'test_session_token'

    requests_mock.post(
        f"{GLPIEnv.URL}/initSession",
        status_code=401
    )

    with pytest.raises(ConnectionError):
        session_manager._open_session()
    assert session_manager._session_token is None


def test_close_session_success(requests_mock, session_manager):
    session_manager._session_token = 'test_session_token'

    requests_mock.get(
        f"{GLPIEnv.URL}/killSession",
        status_code=200
    )

    session_manager._close_session()
    assert session_manager._session_token is None
    assert session_manager._token_expires is None


def test_close_session_failure(requests_mock, session_manager, caplog):
    session_manager._session_token = "test_token"

    requests_mock.get(
        f"{GLPIEnv.URL}/killSession",
        exc=requests.exceptions.ConnectionError
    )

    session_manager._close_session()
    assert "Не удалось закрыть сессию" in caplog.text
    assert session_manager._session_token is None


def test_force_kill_previous_session(requests_mock, session_manager):
    session_manager._session_token = "old_token"

    requests_mock.get(
        f"{GLPIEnv.URL}/killSession",
        status_code=200
    )

    session_manager._force_kill_previous_session()
    assert "old_token" in requests_mock.last_request.headers['Session-Token']


def test_context_manager_success(requests_mock, session_manager):

    # Мокаем инициализацию сессии
    requests_mock.post(
        f"{GLPIEnv.URL}/initSession",
        json={'session_token': 'test_token'},
        status_code=200
    )

    # Мокаем завершение сессии
    requests_mock.get(
        f"{GLPIEnv.URL}/killSession",
        status_code=200
    )

    # Используем контекстный менеджер
    with session_manager.get_session() as sm:
        assert sm._session_token == 'test_token'
        assert sm._token_expires is not None

    # После выхода из контекста токен должен быть сброшен
    assert session_manager._session_token is None
    assert session_manager._token_expires is None

    assert requests_mock.called
    assert requests_mock.call_count == 2


def test_get_session_replaces_old_session(requests_mock, session_manager):

    # Старая сессия
    session_manager._session_token = "old_token"
    session_manager._token_expires = datetime.now() + timedelta(minutes=10)

    # Мокаем старое убийство
    requests_mock.get(
        f"{GLPIEnv.URL}/killSession",
        status_code=200
    )

    # Новая инициализация
    requests_mock.post(
        f"{GLPIEnv.URL}/initSession",
        json={'session_token': 'new_token'},
        status_code=200
    )

    with session_manager.get_session() as sm:
        assert sm._session_token == 'new_token'


@pytest.mark.parametrize(
    "initial_token, initial_expiry, expected_force_kill",
    [
        (None, None, True),
        ("token", datetime.now() - timedelta(seconds=1), True),  # просрочен
        ("token", datetime.now() + timedelta(minutes=1), False),
    ]
)
def test_get_session_force_kill_behavior(
    requests_mock,
    session_manager,
    initial_token,
    initial_expiry,
    expected_force_kill,
    frozen_now
):
    session_manager._session_token = initial_token
    session_manager._token_expires = initial_expiry

    # Мокаем оба запроса
    kill_session_mock = requests_mock.get(
            f"{GLPIEnv.URL}/killSession",
            status_code=200
    )

    init_session_mock = requests_mock.post(
        f"{GLPIEnv.URL}/initSession",
        json={"session_token": "new_token"},
        status_code=200
    )

    with patch("glpi_bot.glpi.session.datetime") as mock_datetime:
        mock_datetime.now.return_value = frozen_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with session_manager.get_session():
            pass

    # Проверяем, была ли попытка "убить" старую сессию
    assert kill_session_mock.called is expected_force_kill
    assert init_session_mock.called
    assert session_manager._session_token is None
