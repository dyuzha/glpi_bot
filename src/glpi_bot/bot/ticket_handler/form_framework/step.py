# form_framework/step.py

from aiogram.types import InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class FormStep:
    key: str = ""
    show_key: str = ""
    prompt: str = ""

    def kb(self) -> InlineKeyboardMarkup:
        pass  # генерация клавиатуры с базовыми и кастомными кнопками

    async def handle_input(self, message: Message, state: FSMContext):
        pass  # базовая обработка данных пользователя

    async def handle_callback(self, callback_data: str, message: Message, state: FSMContext):
        pass  # кастомная обработка кнопок

