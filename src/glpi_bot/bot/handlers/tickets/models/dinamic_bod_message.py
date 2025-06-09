# bot/handlers/tickets/handlers/models/dinamic_bot_message.py

from typing import Optional, Union
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import logging


logger = logging.getLogger(__name__)


class DynamicBotMessage:
    def __init__(self, head: str = "📝 Детали заявки", separator: str = "\n\n"):
        self.head = head
        self.separator = separator


    async def add_field(self, state: FSMContext, key: str, value: str):
        """
        Добавляет или обновляет поле в хранилище состояния.
        key — имя поля (например, 'Описание')
        value — значение поля (например, 'У нас сломалась 1С')
        """
        data = await state.get_data()
        fields = data.get("dynamic_fields", {})
        fields[key] = value
        logger.debug(f"Добавлено поле {key}: {value}")
        await state.update_data(dynamic_fields=fields)


    async def del_field(self, state: FSMContext, key: str):
        """
        Удаляет поле в хранилище состояния.
        key — имя поля (например, 'Описание')
        """
        data = await state.get_data()
        fields = data.get("dynamic_fields", {})
        if key in fields:
            del fields[key]
            logger.debug(f"Удалено поле {key}")
            await state.update_data(dynamic_fields=fields)


    async def render(self, state: FSMContext, *strings) -> str:
        """
        Генерирует текст сообщения на основе всех сохранённых полей и
        дополнительных строк
        Возвращает строку для передачи в edit_message_text.
        """
        data = await state.get_data()
        fields = data.get("dynamic_fields", {})

        parts = [self.head]
        parts.extend(f"{key}: {value}" for key, value in fields.items())
        parts.extend(s for s in strings if s)

        return self.separator.join(parts)


    async def update_message(self, message: Message, state: FSMContext, *strings,
                             keyboard: Optional[InlineKeyboardMarkup] = None):
        """
        Редактирует последнее сообщение бота, извлекая его из navigation-стека.
        Используется для отображения обновлённой информации пользователю.
        """
        data = await state.get_data()
        message_id = data.get("bot_message_id")

        if not message_id:
            logger.debug("Not bot_message_id")
            return

        stack = data.get("navigation_data", {}).get("stack", [])

        if not keyboard:
            if stack and "keyboard" in stack[-1]:
                keyboard = InlineKeyboardMarkup(**stack[-1]["keyboard"])

        text = await self.render(state, *strings)

        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
            ) if message.bot else Exception
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")


    async def reset(self, state: FSMContext):
        """Очищает все динамические поля"""
        await state.update_data(dynamic_fields={})
