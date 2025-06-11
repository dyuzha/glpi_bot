
from typing import Callable, Optional
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from glpi_bot.bot.handlers.tickets.base.navigation import back_handler
from glpi_bot.bot.handlers.tickets.models.dynamic_message import DynamicBotMessage
from glpi_bot.bot.handlers.utils import add_step
from glpi_bot.bot.states import FinalStates
from glpi_bot.services.glpi_service2_0 import GLPITicketManager, TicketData


class ConfirmStep:
    def __init__(self,
                 state: State,
                 prompt: str,
                 glpi: GLPITicketManager,
                 keyboard: InlineKeyboardMarkup,
                 bot_message: DynamicBotMessage,
                 prev_state: State,
                 keydata
            ):
        self.state = state
        self.prompt = prompt
        self.glpi = glpi
        self.keyboard = keyboard
        self.bot_message = bot_message
        self.keydata = keydata
        self.prev_state = prev_state


    async def show(self, callback: CallbackQuery, state: FSMContext, prompt: Optional[str] = None,
                   keyboard: Optional[InlineKeyboardMarkup] = None):

        prompt = prompt or self.prompt
        keyboard = keyboard or self.keyboard

        await add_step(state, prompt=prompt, keyboard=keyboard)

        try:
            d = await state.get_data()
        except Exception as e:
            await callback.answer("Произошла ошибка. Попробуйте сначала.")
            return


        ticket_data = TicketData(
                login = d['login'],
                name = d['title'],
                content = d['description'],
                type = d['type'],
                itilcategories_id = d['itilcategories_id']
        )

        try:
            # Создаем заявку в GLPI
            response = self.glpi.send_ticket(ticket_data)

        except Exception as e:
            await callback.message.answer("Ошибка при создании заявки", reply_markup=main_kb())

        else:
            await self.bot_message.update_message(
                    callback.message, state,
                    f"✅ Заявка успешно создана!\n\n"
                    f"<b>Номер:</b> #{response['id']}\n"
                    f"<b>Заголовок:</b> {d['title']}\n"
                    f"<b>Статус:</b> В обработке",
                    keyboard=InlineKeyboardMarkup(inline_keyboard=[])
                )

    async def callback_handler(self, callback: CallbackQuery, state: FSMContext):
        await self.bot_message.del_field(state, "Описание")
        await back_handler(callback, state)
        await callback.answer()
