# models/dynamic_message/dinamic_bot_message.py

from typing import Optional
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from .message_flasher import MessageFlasher
import logging


logger = logging.getLogger(__name__)


class DynamicBotMessage:
    def __init__(self,
                 inline_keyboard: InlineKeyboardMarkup,
                 head: str = "📝 Детали заявки",
                 separator: str = "\n\n"):
        self._head = head
        self._separator = separator
        self._keyboard = inline_keyboard
        self.flasher = MessageFlasher(self)


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

        parts = [self._head]
        parts.extend(f"{key}: {value}" for key, value in fields.items())
        parts.extend(s for s in strings if s)

        return self._separator.join(parts)


    async def update_message(
            self,
            message: Message,
            state: FSMContext,
            *strings,
            keyboard: Optional[InlineKeyboardMarkup] = None
        ) -> Optional[Message]:

        """
        Редактирует последнее сообщение бота, извлекая его из state.
        Возвращает объект Message при успехе, иначе None.
        """
        data = await state.get_data()
        message_id = data.get("bot_message_id")

        if not message_id:
            logger.debug("Not bot_message_id")
            return None

        if not message.bot:
            logger.error("Message has no bot instance")
            return None

        text = await self.render(state, *strings)

        try:
            edited_message = await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard or self._keyboard,
            )
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
            return None

        return edited_message


    async def delete_message(self, message: Message, state: FSMContext) -> bool:
        """Удаляет сообщение бота. Возвращает True если удаление успешно."""
        try:
            data = await state.get_data()
            if (message_id := data.get("bot_message_id")) is None:
                logger.debug("bot_message_id не найден в state")
                return False

            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=message_id
            )
            # Очищаем message_id после удаления
            await state.update_data(bot_message_id=None)
            return True

        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")
            return False


    async def reset(self, state: FSMContext):
        """Очищает все динамические поля"""
        await state.update_data(dynamic_fields={})
