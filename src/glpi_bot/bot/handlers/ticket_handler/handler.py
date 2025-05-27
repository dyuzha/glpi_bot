
# handler.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.handlers.ticket_handler.registration_flow import RegistrationFlow
from glpi_bot.bot.handlers.ticket_handler.steps import TypeStep, CategoryStep

router = Router()
registration = RegistrationFlow([TypeStep(), CategoryStep()])

@router.message(Command("reg"))
async def start_registration(message: Message, state: FSMContext):
    await registration.start(message, state)

# @router.message()
# async def process_steps(message: Message, state: FSMContext):
#     text = message.text.strip()
#     if text == "✅ Подтвердить":
#         await message.answer("Спасибо! Данные сохранены.")
#         await state.clear()

@router.callback_query(F.data == "confirm")
async def confirm_data(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    summary = "\n".join(f"{step.key}: {data.get(step.key)}" for step in registration.steps)
    await call.message.answer(f"✅ Данные подтверждены:\n{summary}")
    await state.clear()
    await call.answer()


@router.callback_query(F.data == "edit")
async def edit_menu(call: CallbackQuery):
    await registration.show_edit_menu(call.message)
    await call.answer()
