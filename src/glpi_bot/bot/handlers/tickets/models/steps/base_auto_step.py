
from typing import Awaitable, Callable, Iterable, Optional
from aiogram.filters import Filter, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder

from glpi_bot.bot.handlers.utils import add_step

from .base_step import BaseStep
import logging
import uuid
import hashlib


logger = logging.getLogger(__name__)


class CallbackTargetFilter(Filter):
    """Фильтр для проверки target в callback данных"""
    def __init__(self, cb_factory, target: str, *, exclude_data: Optional[set[str]]):
        self.cb_factory = cb_factory
        self.target = target
        self.exclude_data = exclude_data or set()

    async def __call__(self, callback: CallbackQuery) -> bool:
        if callback.data in self.exclude_data:
            return False
        try:
            data = self.cb_factory.unpack(callback.data)
            return data.target == self.target
        except (ValueError, AttributeError):
            logger.debug("ошибка")
            return False


class BaseAutoStep(BaseStep):

    def __init__(self,
                 state: State,
                 prompt: str,
                 filters: Optional[Iterable[Callable]] = [],
                 before_callback: Optional[Callable[[CallbackQuery, FSMContext], Awaitable[None]]] = None,
                 base_buttons: Optional[list[InlineKeyboardButton]] = None,
                 prefix: Optional[str] = None,
                 ):

        self._steps: dict[str, BaseStep] = {}
        self.state = state
        self.prompt = prompt
        self.filters = filters or []
        self.base_buttons = base_buttons or None
        self._prefix = prefix or self._generete_unical()
        self.cb_factory = self._create_callback_factory()
        self.before_callback = before_callback


    @property
    def _excluded_callbacks(self) -> list:
        if self.base_buttons:
            return [btn.callback_data for btn in self.base_buttons]
        return []


    @property
    def keyboard(self) -> InlineKeyboardMarkup:
        return self.build_keyboard()


    def build_keyboard(self, **kwargs) -> InlineKeyboardMarkup:
        """
        Формирует клавиатуру, где:
        - text_button: текст кнопки (ключ из self._steps)
        - target: уникальный числовой ID для идентификации
        """

        builder = InlineKeyboardBuilder()

        for text_button, step in self._steps.items():
            callback_data = self.cb_factory(
                    action="execute",
                    target=str(step.callback_target),
                    data=str(kwargs) if kwargs else None
                    ).pack()
            builder.button(text=text_button, callback_data=callback_data)

        builder.adjust(1)

        if self.base_buttons:
            builder.row(*self.base_buttons)

        return builder.as_markup()


    async def on_callback(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Обрабатывает callback и обновляет сообщение с клавиатурой"""

        logger.debug(f"Processing callback in {self.__class__.__name__}")

        if self.state:
            await state.set_state(self.state)
            logger.debug(f"Set state {self.state}")

        await add_step(state, self.prompt or "", self.keyboard)
        # await super().on_callback(callback, state)

        if self.before_callback:
            await self.before_callback(callback, state)
            logger.debug(f"Call before_callback")


        if not self._steps:
            logger.error(f"Ошибка: нет закрепленных шагов")
            raise ValueError # "Нет закрепленных шагов"

        try:
            await callback.message.edit_text(
                text=self.prompt or "",
                reply_markup=self.keyboard
            )
        except Exception as e:
            logger.debug(f"Invalid edit message: {e}")

        logger.debug(f"End processing callback in {self.__class__.__name__}")



    def _create_callback_factory(self):
        """Создает фабрику callback-данных с уникальным префиксом"""
        class DynamicCallbackData(
                CallbackData,
                prefix=self._prefix,
            ):
            action: str = "execute"
            target: str
            data: Optional[str] = None  # Дополнительные данные

        return DynamicCallbackData


    def register_handler(self, router: Router) -> None:
        """Регистрирует обработчики с учетом иерархии состояний"""
        super().register_handler(router)

        # Регистрируем все вложенные шаги
        for step in self._steps.values():
            step.register_handler(router)


    def attach_step(self, step: BaseStep):

        if not hasattr(step, 'callback_target') or not step.callback_target:
            # Генерируем уникальный callback_target
            callback_target = self._generete_unical(6)
            step.callback_target = callback_target

        # Устанавливаем фильтры для вложенного шага
        step.filters = self._generate_attach_filters(step.callback_target)


    def __setitem__(self, text_button: str, step: BaseStep):
        """Добавляет шаг с автоматической регистрацией callback фильтров"""
        self._steps[text_button] = step
        self.attach_step(step)


    def __iter__(self):
        """Итерация по ключам шагов: for key in step"""
        return iter(self._steps)


    def update(self, *steps_dicts: dict[str, BaseStep]):
        """Обновляет шаги из одного или нескольких словарей"""
        for steps_dict in steps_dicts:
            for key, step in steps_dict.items():
                self[key] = step


    def _generate_attach_filters(self, target: str) -> list:
        """Генерирует фильтры на основе target"""
        filters = [
                StateFilter(self.state),
                CallbackTargetFilter(
                    self.cb_factory,
                    target,
                    exclude_data=self._excluded_callbacks)
        ]
        return filters


    @staticmethod
    def _generete_unical(lenght: int = 8) -> str:
        """Генерирует уникальную строчу на основе хеша от UUID."""
        return hashlib.md5(uuid.uuid4().bytes).hexdigest()[:lenght]
