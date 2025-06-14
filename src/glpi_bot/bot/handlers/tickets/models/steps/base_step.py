
from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram import Router, F
from aiogram.filters import StateFilter
from glpi_bot.bot.handlers.utils import default_handle
import logging


logger = logging.getLogger("__name__")


class BaseStep(ABC):
    def __init__(self, filters: Optional[Iterable[Callable]] = None):
        self.filters = filters

    def register_handler(self, router: Router) -> None:
        if not self.filters:
            raise ValueError("Нужно передать хотя бы один фильтр.")
        router.callback_query.register(self._handler, *self.filters)


    def get_router(self) -> Router:
        router = Router()
        self.register_handler(router)
        return router


    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        await self._handler(callback, state)


    async def _handler(self, callback: CallbackQuery, state: FSMContext):
        await self.on_callback(callback, state)


    @abstractmethod
    async def on_callback(self, callback: CallbackQuery, state: FSMContext):
        ...
