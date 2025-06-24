# tests/test_base.py

from sqlalchemy.ext.asyncio import AsyncSession

from glpi_bot.database.base import Database


async def test_create_tables():
    db = Database("sqlite+aiosqlite:///:memory:")
    await db.create_tables()

    async with db.async_sessionmaker() as session:
        assert isinstance(session, AsyncSession)
