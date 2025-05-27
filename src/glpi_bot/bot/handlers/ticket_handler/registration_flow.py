
# registration_flow.py

from typing import List
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.handlers.ticket_handler.steps import FormStep, DISABLE_KEY, COMPLETE_KEY, BACK_KEY


class RegistrationFlow:
    def __init__(self, steps: List[FormStep]):
        self.steps = steps
        self.current_step_index = 0

    @property
    def current_step(self) -> FormStep:
        return self.steps[self.current_step_index]

    async def start(self, message: Message, state: FSMContext):
        self.current_step_index = 0
        await self._call_current_step(message, state)

    async def handle_input(self, message: Message, state: FSMContext):
        await self.current_step.handle_input(message, state)

        if message.text == BACK_KEY:
            await self._call_prev_step(message, state)
        else:
            self.current_step_index += 1
            if self.current_step_index < len(self.steps):
                await self._call_current_step(message, state)
            else:
                await self.confirm(message, state)

    async def _call_prev_step(self, message: Message, state: FSMContext):
        if self.current_step_index > 0:
            self.current_step_index -= 1
        await self._call_current_step(message, state)

    async def go_to(self, index: int, message: Message, state: FSMContext):
        if 0 <= index < len(self.steps):
            self.current_step_index = index
            await self._call_current_step(message, state)

    async def _call_current_step(self, message: Message, state: FSMContext):
        await message.answer(
            self.current_step.prompt,
            reply_markup=self.current_step.kb(),
        )

    async def confirm(self, message: Message, state: FSMContext):
        data = await state.get_data()
        summary = "\n".join(f"{step.key}: {data.get(step.show_key)}" for step in self.steps)

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")],
                [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit")],
            ]
        )
        await message.answer(f"Подтверждение данных:\n{summary}", reply_markup=kb)

    async def show_edit_menu(self, message: Message):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [ InlineKeyboardButton(text=step.key, callback_data=f"edit:{step.show_key}")]
                for step in self.steps
            ]
        )
        await message.answer("Выберите поле для редактирования:", reply_markup=keyboard)
