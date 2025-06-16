
from typing import Any, Awaitable, Callable, Iterable, Optional
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from glpi_bot.bot.handlers.tickets.models.steps.base_auto_step import BaseAutoStep
from .base_step import BaseStep
import logging


logger = logging.getLogger("__name__")


class AutoInlineStep(BaseAutoStep):

    def __init__(self,
                 state: Optional[State] = None,
                 filters: Optional[Iterable[Callable]] = None,
                 prompt: str = "Выберите действие:",
                 before_callback: Optional[Callable[[CallbackQuery, FSMContext], Awaitable[None]]] = None,
                 keyboard: Optional[InlineKeyboardMarkup] = None,
                 ):
        super().__init__(filters)
        self.state = state or None
        self.prompt = prompt
        self.before_callback = before_callback
        self._keyboard = keyboard


    def build_keyboard(self, **kwargs: Any) -> InlineKeyboardMarkup:
        """Строит inline-клавиатуру с кнопками для всех шагов"""
        buttons = [
            InlineKeyboardButton(
                text=name,
                callback_data=self._cb_factory(
                    action="execute",
                    target=name,
                    data=str(kwargs) if kwargs else None
                ).pack()
            )
            for name in self._steps
        ]
        return InlineKeyboardMarkup(inline_keyboard=[buttons])


    async def on_callback(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Обрабатывает callback и обновляет сообщение с клавиатурой"""
        if self.state:
            await state.set_state(self.state)

        if self.before_callback:
            await self.before_callback(callback, state)

        await super().on_callback(callback, state)

        if self._steps or self._keyboard:
            await callback.message.edit_text(
                text=self.prompt,
                reply_markup=self.build_keyboard()
            )
