# bot/handlers/tickets/handlers/models/text_input_step.py

from typing import Awaitable, Callable, Optional
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
import logging

from glpi_bot.bot.handlers.models import DynamicBotMessage
from glpi_bot.bot.handlers.utils import default_handle
from glpi_bot.bot.keyboards import base_buttons


logger = logging.getLogger(__name__)


class TextInputStep:
    def __init__(
        self,
        state: State,
        prompt: str,
        bot_message: DynamicBotMessage,
        validate: Optional[Callable[[Message, FSMContext, DynamicBotMessage], Awaitable[bool]]] = None,
        final: Optional[Callable[[Message, FSMContext, DynamicBotMessage], Awaitable[None]]] = None,
    ):
        self.state = state
        self.prompt = prompt
        self.bot_message = bot_message
        self.validate = validate
        self.final = final


    async def show(self, callback: CallbackQuery, state: FSMContext):
        """Показ шага — задаёт состояние и показывает сообщение."""
        await state.set_state(self.state)
        rendered = await self.bot_message.render(state, self.prompt)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[base_buttons])
        await default_handle(callback, state, rendered, keyboard)


    async def __call__(self, message: Message, state: FSMContext):
        """
        Обработка ввода пользователя,
        возвращает True[False] при прохождении[не прохождении] валидации.
        """
        if self.validate:
            is_valid = await self.validate(message, state, self.bot_message)
            if not is_valid:
                return False
        else:
            is_valid = True

        if is_valid and self.final:
            logger.debug("Call final")
            await self.final(message, state, self.bot_message)
            logger.debug("Call final end")

        return True
