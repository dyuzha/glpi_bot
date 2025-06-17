from abc import abstractmethod
from typing import Callable, Iterable, Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from glpi_bot.bot.handlers.tickets.models.steps.base_step import BaseStep


class BaseTextStep(BaseStep):
    def __init__(self, filters: Optional[Iterable[Callable]] = None):
        self.filters = filters or []
        self._keyboard: Optional[InlineKeyboardMarkup] = None
        self.prompt: Optional[str] = None

        self.parent_state: Optional[State] = None
        self.callback_target: Optional[str] = None
        self.custom_func: None


    @abstractmethod
    async def handle(self, message: Message, state: FSMContext) -> bool:
        """
        Обработка ввода пользователя,
        возвращает True[False] при прохождении[не прохождении] валидации.
        """
        ...


    @abstractmethod
    async def validate(self,
                       message: Message,
                       state: FSMContext,
                       prompt: Optional[str] = None):
        ...


    async def on_callback(self, callback: CallbackQuery, state: FSMContext):
        is_validate = await self.handle(callback.message, state)
        if not is_validate:
            return
