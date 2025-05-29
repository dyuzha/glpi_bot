# form_framework/step.py
from abc import ABC, abstractmethod
from aiogram.types import Message, CallbackQuery, KeyboardButton
from aiogram.fsm.context import FSMContext
from typing import Optional, Awaitable, List


class FormStep(ABC):
    def __init__(self, key: str, prompt: str, optional: bool = False, show_key: Optional[str] = None):
        self.key = key
        self.prompt = prompt
        self.optional = optional
        self.show_key = show_key or key

    @abstractmethod
    async def process_input(self, message: Message, state: FSMContext) -> bool:
        """
        Обрабатывает пользовательский ввод.
        Возвращает True, если можно переходить к следующему шагу.
        """
        pass

    def get_custom_buttons(self) -> List[List[KeyboardButton]]:
        """
        Переопределяемая функция для пользовательских кнопок.
        По умолчанию — никаких.
        """
        return []

    async def handle_callback(self, call: CallbackQuery, state: FSMContext):
        """
        Опционально переопределяется для обработки callback.
        По умолчанию — ничего не делает.
        """
        await call.answer("Нераспознанный callback.")
