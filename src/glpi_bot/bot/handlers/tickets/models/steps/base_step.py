
from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram import Router
import logging

from glpi_bot.bot.handlers.utils import add_step


logger = logging.getLogger(__name__)


class BaseStep(ABC):
    def __init__(self, filters: Optional[Iterable[Callable]] = None):
        self.filters = filters or []
        self._keyboard: Optional[InlineKeyboardMarkup] = None
        self.prompt: Optional[str] = None

        self.parent_state: Optional[State] = None
        self.callback_target: Optional[str] = None


    @property
    def keyboard(self) -> InlineKeyboardMarkup:
        if self._keyboard:
            return self._keyboard
        raise ValueError("Клавиатура неопределена")


    def register_handler(self, router: Router) -> None:
        if not self.filters:
            raise ValueError("Нужно передать хотя бы один фильтр.")

        router.callback_query.register(
                self.handle,
                *self.filters
                )


    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        """Альтернативный вызов обработчика"""
        try:
            await self.handle(callback, state)
        except Exception as e:
            await self.handle_error(callback, e)


    async def handle_error(self, callback: CallbackQuery, error: Exception):
        """Базовый обработчик ошибок"""
        await callback.answer("Произошла ошибка")
        raise error


    async def base_action(self, callback: CallbackQuery, state: FSMContext):
        await add_step(state=state, prompt=self.prompt or "", keyboard=self.keyboard)


    async def handle(self, callback: CallbackQuery, state: FSMContext):
        await self.base_action(callback, state)
        await self.on_callback(callback, state)


    async def on_callback(self, callback: CallbackQuery, state: FSMContext):
        ...
