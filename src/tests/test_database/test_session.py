import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from glpi_bot.database import DBSessionManager
from glpi_bot.database.base import Base
from glpi_bot.database.models import User
from glpi_bot.database.base import Database


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_db = Database(DATABASE_URL)
    async_db.engine = engine
    async_db.async_sessionmaker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    yield async_db

    await engine.dispose()


async def test_commit_called(db):
    manager = DBSessionManager(db)

    async with manager.get_session() as session:
        user = User(telegram_id=12345, login="test_user")
        session.add(user)

    # Проверяем, что пользователь добавлен
    async with db.async_sessionmaker() as session:
        result = await session.get(User, 1)
        assert result is not None
        assert result.telegram_id == 12345


async def test_rollback_called_on_exception(db):
    manager = DBSessionManager(db)

    class CustomError(Exception):
        pass

    with pytest.raises(CustomError):
        async with manager.get_session() as session:
            user = User(telegram_id=99999, login="bad_user")
            session.add(user)
            raise CustomError("Something went wrong")

    # Проверяем, что пользователь НЕ добавлен из-за rollback
    async with db.async_sessionmaker() as session:
        result = await session.get(User, 1)
        assert result is None
