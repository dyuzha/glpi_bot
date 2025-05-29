# form_framework/flow.py
from typing import List
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from .step import FormStep


class FormFlow:
    back_key = "🔙 Назад"
    disable_key = "🚫 Пропустить"
    complete_key = "✅ Завершить"
    edit_key = "✏️ Изменить"

    def __init__(self, steps: List[FormStep]):
        self.steps = steps

    async def start(self, message: Message, state: FSMContext):
        pass  # запуск формы

    async def handle_input(self, message: Message, state: FSMContext):
        pass  # обработка пользовательского ввода

    async def handle_callback(self, callback: CallbackQuery, state: FSMContext):
        pass  # обработка нажатий на inline-кнопки

    async def confirm(self, message: Message, state: FSMContext):
        pass  # подтверждение заполнения

    async def show_edit_menu(self, message: Message):
        pass  # отображение меню редактирования шагов
