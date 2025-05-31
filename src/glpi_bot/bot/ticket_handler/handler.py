# handler.py

from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, KeyboardButton, Message, ReplyKeyboardMarkup
from glpi_bot.bot.keyboards import main_kb
from glpi_bot.bot.states import MainStates, TicketStates
from glpi_bot.bot.ticket_handler.form_framework.routers import FormRouter
from glpi_bot.bot.ticket_handler.form_framework.keyboard import FormKeyboardBuilder
from glpi_bot.bot.ticket_handler.form_framework.step import FormStep
from glpi_bot.bot.ticket_handler.steps import TitleStep, TypeStep
from typing import List, Type

from glpi_bot.bot.ticket_handler.form_framework.flow import (
    EditModeHandler,
    FormFlow,
    InputModeHandler,
)

BACK_KEY = "🔙 Назад"
CANCEL_KEY = "🚫 Отмена"

steps = [TypeStep(), TitleStep()]

class TicketInputModeHandler(InputModeHandler):
    """Кастомный обработчик ввода для тикетов. Обрабатывает кнопки "Назад" и "Отмена"."""
    sys_buttons = [[KeyboardButton(text=CANCEL_KEY), KeyboardButton(text=BACK_KEY)]]
    async def base_input(self, message: Message, state: FSMContext) -> bool:
            text = message.text
            data = await state.get_data()
            index = data.get("step_index", 0)

            if text == BACK_KEY:
                new_index = max(0, index - 1)
                await self.go_to_step(new_index, message, state)
                return True

            if text == CANCEL_KEY:
                await state.clear()
                await message.answer("Форма отменена.",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text="Вернуться в главное меню")]],
                        resize_keyboard=True
                ))
                return True

            return False

class TicketEditModeHandler(EditModeHandler):
    sys_buttons = [
        [InlineKeyboardButton(text=BACK_KEY, callback_data="back")],
        [InlineKeyboardButton(text=CANCEL_KEY, callback_data="cancel")]
    ]

    async def base_input(self) -> bool:
        pass

flow = FormFlow(steps=steps, input_handler_cls=TicketInputModeHandler)
form_router = FormRouter(flow=flow, state=TicketStates.create_ticket, command="create_ticket")
router = Router()
form_router.register(router)

async def start_flow(message: Message, state: FSMContext):
    await form_router.start_flow(message, state)
