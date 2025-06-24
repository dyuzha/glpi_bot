import pytest
from unittest.mock import AsyncMock, MagicMock
from glpi_bot.database import User
from glpi_bot.services.db_service import DBService  # путь подкорректируй под себя
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


# Контекстный менеджер для async with
class MockAsyncContextManager:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_session_manager(mock_session):
    session_manager = MagicMock()
    session_manager.get_session.return_value = MockAsyncContextManager(mock_session)
    return session_manager


@pytest.mark.asyncio
async def test_save_user_creates_new_user(mock_session, mock_session_manager):
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    await service.save_user(telegram_id=123, login="test_login")

    mock_session.add.assert_called_once()
    args, _ = mock_session.add.call_args
    assert isinstance(args[0], User)
    assert args[0].telegram_id == 123
    assert args[0].login == "test_login"


@pytest.mark.asyncio
async def test_save_user_updates_existing_user(mock_session, mock_session_manager):
    existing_user = User(telegram_id=123, login="old_login")

    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = existing_user
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    await service.save_user(telegram_id=123, login="new_login")

    assert existing_user.login == "new_login"
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_check_user_exists(mock_session, mock_session_manager):
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = User()
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    result = await service.check_user(telegram_id=123)

    assert result is True


@pytest.mark.asyncio
async def test_check_user_not_exists(mock_session, mock_session_manager):
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    result = await service.check_user(telegram_id=123)

    assert result is False


@pytest.mark.asyncio
async def test_get_login_found(mock_session, mock_session_manager):
    user = User(telegram_id=123, login="test_login")

    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = user
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    login = await service.get_login(telegram_id=123)

    assert login == "test_login"


@pytest.mark.asyncio
async def test_get_login_not_found(mock_session, mock_session_manager):
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    login = await service.get_login(telegram_id=123)

    assert login is None


@pytest.mark.asyncio
async def test_delete_user_found(mock_session, mock_session_manager):
    user = User(telegram_id=123, login="to_delete")

    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = user
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    result = await service.delete_user(telegram_id=123)

    mock_session.delete.assert_awaited_once_with(user)
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_not_found(mock_session, mock_session_manager):
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result

    service = DBService(mock_session_manager)

    result = await service.delete_user(telegram_id=123)

    mock_session.delete.assert_not_called()
    assert result is False
