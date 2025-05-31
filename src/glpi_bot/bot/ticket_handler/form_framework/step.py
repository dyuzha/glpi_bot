# form_framework/step.py
from abc import ABC, abstractmethod
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery, KeyboardButton
from aiogram.fsm.context import FSMContext
from typing import Optional, Awaitable, List
import logging


logger = logging.getLogger(__name__)


class FormStep(ABC):
    """Шаг для обычной формы"""
    key: str
    prompt: str
    show_key: str

    @abstractmethod
    async def process_input(self, message: Message, state: FSMContext) -> bool:
        """
        Обрабатывает пользовательский ввод.

        Возвращает:
            True — данные валидны, можно продолжать;
            False — ошибка, остаёмся на этом шаге.

        Если False, шаг сам выводит сообщение об ошибке.
        """
        ...


    def get_reply_custom_buttons(self) -> List[List[KeyboardButton]]:
        """
        Переопределяемая функция для пользовательских reply кнопок.
        По умолчанию — никаких.
        """
        return []


    def get_inline_custom_buttons(self) -> List[InlineKeyboardButton]:
        """
        Переопределяемая функция для пользовательских inline кнопок.
        По умолчанию — никаких.
        """
        return []



class EditFormStep(FormStep):
    """Шаг для редактируемой формы"""
    key: str
    prompt: str
    show_key: str

    edit_key: Optional[str] = None
    edit_prompt: Optional[str] = None
    edit_show_key: Optional[str] = None

    def __init__(self):
        if self.edit_show_key == None: self.edit_show_key = self.show_key
        if self.edit_key == None: self.edit_key = self.key


    def get_inline_custom_buttons(self) -> List[InlineKeyboardButton]:
        """ Переопределяемая функция для пользовательских inline кнопок. """
        return [InlineKeyboardButton(text=self.edit_show_key, callback_data=self.edit_key)]


    async def handle_callback(self, call: CallbackQuery, state: FSMContext):
        """
        Опционально переопределяется для обработки callback.
        По умолчанию — ничего не делает.
        """
        await call.answer("Нераспознанный callback.")
