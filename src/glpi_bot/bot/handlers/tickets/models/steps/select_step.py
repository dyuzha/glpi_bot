
from typing import Awaitable, Callable, Iterable, Optional
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from glpi_bot.bot.handlers.tickets.models.steps.base_step import BaseStep
import logging


logger = logging.getLogger(__name__)


class SelectInlineStep(BaseStep):
    def __init__(
            self,
            state: State,
            prompt: str,
            keyboard: Optional[InlineKeyboardMarkup] = None,
            before_callback: Optional[Callable[[CallbackQuery, FSMContext], Awaitable[None]]] = None,
            filters: Optional[Iterable[Callable]] = None,
            self_button_text: Optional[str] = None,
        ):
        super().__init__(filters)
        self.prompt = prompt
        self._keyboard = keyboard
        self.before_callback = before_callback
        self.state = state
        self.self_button_text = self_button_text


    async def on_callback(self,
                          callback: CallbackQuery,
                          state: FSMContext,
                          prompt: Optional[str] = None,
                          keyboard: Optional[InlineKeyboardMarkup] = None):

        current_state = await state.get_state()
        logger.debug(f"Handling callback. Current state: {current_state}, data: {callback.data}")

        if self.before_callback:
            await self.before_callback(callback, state)

        await state.set_state(self.state)

        prompt = prompt or self.prompt
        keyboard = keyboard or self.keyboard

        if not keyboard:
            raise ValueError("Необходимо сначала задать клавиатуру")

        # Обновляем сообщение бота с новым текстом и клавиатурой
        if isinstance(callback.message, Message):
            try:
                await callback.message.edit_text(prompt or "", reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Error editing message")

        # Подтверждаем callback без всплывающего уведомления
        await callback.answer()
