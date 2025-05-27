# steps.py

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from glpi_bot.bot.states import FormState
from abc import ABC, abstractmethod
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


DISABLE_KEY = "❌ Отмена"
COMPLETE_KEY = "✅ Подтвердить"
BACK_KEY = "🔙 Назад"


class FormStep(ABC):
    key = "abs"
    show_key = "abs"

    @property
    @abstractmethod
    def prompt(self) -> str:
        """Промт для текущего шага."""
        pass

    @abstractmethod
    async def handle_input(self, message: Message, state: FSMContext):
        """Обработчик ввода для текущего шага."""
        pass

    def kb(self):
        return ReplyKeyboardMarkup(
            keyboard=[
            [KeyboardButton(text=DISABLE_KEY), KeyboardButton(text=BACK_KEY)]
            ],
            resize_keyboard=True
        )


class TypeStep(FormStep):
    key = "type"
    show_key = "Тип заявки"


    @property
    def prompt(self) -> str:
        return "Введите первую переменную (A):"

    async def handle_input(self, message: Message, state: FSMContext):
        await state.update_data({self.key: message.text})


class CategoryStep(FormStep):
    key = "category"
    show_key = "Категория"

    @property
    def prompt(self) -> str:
        return "Введите вторую переменную (B):"

    async def handle_input(self, message: Message, state: FSMContext):
        await state.update_data({self.key: message.text})

