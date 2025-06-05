# bot.handler.models.fork_maker.py

from typing import Callable, Dict, Optional
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class BaseForkMaker:
    def __init__(self, base_buttons: Optional[list[InlineKeyboardButton]] = None):
        self._handlers: Dict[str, dict] = {}
        self._base_buttons = base_buttons

    def register_callback(self, name: str, text: str = "Нет подписи"):
        def decorator(func: Callable):
            self._handlers[name] = {
                "handler": func,
                "text": text
            }
            return func
        return decorator

    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        handler = self._handlers.get(callback.data) if callback.data else None
        if not handler:
            return
        await handler["handler"](callback, state)

    def build_keyboard(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for name, item in self._handlers.items():
            builder.button(text=item["text"], callback_data=name)

        builder.adjust(1)

        if self._base_buttons:
            builder.row(*self._base_buttons)

        return builder.as_markup()
