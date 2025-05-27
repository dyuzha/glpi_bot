# forms.py

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.handlers.ticket_handler.steps import FormStep
from typing import List


class Form:
    def __init__(self, steps: List[FormStep]):
        self.steps = steps
        self.current_step = 0

    async def start(self, message: Message, state: FSMContext):
        await state.set_state(self.steps[self.current_step].__class__.__name__)
        await message.answer(self.steps[self.current_step].prompt)

    async def process_input(self, message: Message, state: FSMContext):
        """Обрабатывает ввод для текущего шага."""
        current_step = self.steps[self.current_step]
        await current_step.handle_input(message, state)

        # Переходим к следующему шагу
        self.current_step += 1
        if self.current_step < len(self.steps):
            next_step = self.steps[self.current_step]
            await state.set_state(next_step.__class__.__name__)
            await message.answer(next_step.prompt)
        else:
            await message.answer(
                "Все переменные введены! Подтвердите или отредактируйте."
            )
