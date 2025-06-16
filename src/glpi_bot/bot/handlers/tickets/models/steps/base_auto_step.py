
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Optional
from aiogram.filters import Filter, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram import Router
from .base_step import BaseStep
import logging
import uuid
import hashlib


logger = logging.getLogger("__name__")


class CallbackTargetFilter(Filter):
    """Фильтр для проверки target в callback данных"""
    def __init__(self, cb_factory, target: str):
        self.cb_factory = cb_factory
        self.target = target

    async def __call__(self, callback: CallbackQuery) -> bool:
        try:
            data = self.cb_factory.unpack(callback.data)
            return data.target == self.target
        except:
            return False


class BaseAutoStep(BaseStep):

    def __init__(self,
                 filters: Optional[Iterable[Callable]] = [],
                 ):
        self._steps: dict[str, BaseStep] = {}
        self.cb_factory = self._create_callback_factory()
        self.filters = filters
        self._parent_state = None  # Состояние родительского шага


    def _generate_step_filters(self, target: str) -> list:
        """Генерирует фильтры для конкретного шага"""
        # Используем состояние родителя, а не текущее
        filters = [StateFilter(self._parent_state)] if self._parent_state else []
        filters.append(CallbackTargetFilter(self._cb_factory, target))
        return filters


    def _create_callback_factory(self, prefix: Optional[str] = None):
        """Создает фабрику callback-данных с уникальным префиксом"""
        class DynamicCallbackData(
                CallbackData,
                prefix=prefix or self._generete_prefix(),
            ):
            action: str = "execute"
            target: str
            data: Optional[str] = None  # Дополнительные данные

        return DynamicCallbackData


    def register_handler(self, router: Router) -> None:
        """Регистрирует обработчики с автоматическими фильтрами"""
        if self.filters:
            super().register_handler(router)

        # Регистрируем все вложенные шаги
        for step in self._steps.values():
            step.register_handler(router)


    def __setitem__(self, key: str, value: BaseStep):
        """Магический метод для добавления шага через квадратные скобки"""
        self._steps[key] = value
        logger.debug(f"Добавлен шаг '{key}'")


    def __iter__(self):
        """Итерация по ключам шагов: for key in step"""
        return iter(self._steps)


    def update(self, *steps_dicts: dict[str, BaseStep]):
        """Обновляет шаги из одного или нескольких словарей"""
        for steps_dict in steps_dicts:
            self._steps.update(steps_dict)
            logger.debug(f"Обновлены шаги: {list(steps_dict.keys())}")


    def _generete_prefix(self) -> str:
        """
        Генерирует уникальный префикс для callback-данных на основе хеша от UUID.
        Returns: Уникальный строковый префикс
        """
        return hashlib.md5(uuid.uuid4().bytes).hexdigest()[:8]
