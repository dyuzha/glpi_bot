from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from glpi_bot.database import User, DBSessionManager
import logging


logger = logging.getLogger(__name__)


class DBService:
    def __init__(self, session_manager: DBSessionManager):
        self.session_manager = session_manager


    async def _get_user(self,
                        telegram_id: int,
                        session: Optional[AsyncSession] = None,
    ) -> Optional[User]:
        if session is not None:
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user

        async with self.session_manager.get_session() as session:
            return await self._get_user(telegram_id=telegram_id, session=session)


    async def save_user(self, telegram_id: int, login: str):
        async with self.session_manager.get_session() as session:
            user = await self._get_user(telegram_id=telegram_id, session=session)

            if user:
                user.login = login
            else:
                session.add(User(telegram_id=telegram_id, login=login))


    async def check_user(self, telegram_id: int) -> bool:
        async with self.session_manager.get_session() as session:
            user = await self._get_user(telegram_id=telegram_id, session=session)
            return user is not None


    async def get_login(self, telegram_id: int) -> Optional[str]:
        async with self.session_manager.get_session() as session:
            user = await self._get_user(telegram_id=telegram_id, session=session)
            return user.login if user else None


    async def delete_user(self, telegram_id: int) -> bool:
        async with self.session_manager.get_session() as session:
            user = await self._get_user(telegram_id=telegram_id, session=session)
            if user:
                await session.delete(user)
                return True
            return False
