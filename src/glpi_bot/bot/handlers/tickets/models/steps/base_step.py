
from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router
import logging


logger = logging.getLogger("__name__")


class BaseStep(ABC):
    def __init__(self, filters: Optional[Iterable[Callable]] = None):
        self.filters = filters or []

    def register_handler(self, router: Router) -> None:
        if not self.filters:
            raise ValueError("Нужно передать хотя бы один фильтр.")
        router.callback_query.register(self.on_callback, *self.filters)


    def get_router(self) -> Router:
        router = Router()
        self.register_handler(router)
        return router


    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        await self.on_callback(callback, state)


    @abstractmethod
    async def on_callback(self, callback: CallbackQuery, state: FSMContext):
        ...
