import logging
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware
from typing import Union, Callable, Dict, Any, Awaitable
from services import DBInterface

logger = logging.getLogger(__name__)

PUBLIC_COMMANDS = ['/authorization']

class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:

        # Пропускаем команду публичные команды
        if isinstance(event, Message) and event.text in PUBLIC_COMMANDS:
            return await handler(event, data)

        # Пропускаем команды в которых event содержит from_user
        if not hasattr(event, 'from_user'):
            logger.warning(f"Событие {type(event)} не содержит from_user")
            return await handler(event, data)

        user = DBInterface.check_user(telegram_id=event.from_user.id)

        if not user:
            # Отвечаем только если событие поддерживает answer
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer("❌ Для использования бота требуется авторизация. Введите /authorization")
            return

        return await handler(event, data)
