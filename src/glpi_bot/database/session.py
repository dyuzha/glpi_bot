# /database/session.py - Управление сессиями

from contextlib import asynccontextmanager
from glpi_bot.database import Database


class DBSessionManager:
    def __init__(self, database: Database):
        self.db = database

    @asynccontextmanager
    async def get_session(self):
        async with self.db.async_sessionmaker() as session:
            try:
                yield session
                await session.commit()

            except Exception:
                await session.rollback()
                raise
