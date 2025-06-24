# /database/base.py - Инициализация бд

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, db_url: str):
        self.engine: AsyncEngine = create_async_engine(db_url, echo=False)
        self.async_sessionmaker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
