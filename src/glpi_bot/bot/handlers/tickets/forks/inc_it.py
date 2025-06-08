# bot/handlers/tickets/forks/inc_it.py

import logging
from typing import Optional
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from glpi_bot.bot.handlers.tickets.models.text_input_step import TextInputStep
from glpi_bot.bot.handlers.tickets.steps.title_step import title_step
from glpi_bot.bot.handlers.utils import default_handle
from glpi_bot.bot.states import FinalStates
from glpi_bot.bot.keyboards import base_buttons
from glpi_bot.bot.handlers.tickets import bot_message, inc_it_fork_maker

logger = logging.getLogger(__name__)


async def call_title(
        callback: CallbackQuery,
        state: FSMContext,
        prompt:str = "💬 Введите заголовок заявки\n(Краткое описание проблемы)"
    ):

    rendered = await bot_message.render(state, prompt)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[base_buttons])

    await state.set_state(FinalStates.title)
    await default_handle(callback, state, rendered, keyboard)

# await title_step.show(callback, state)

async def deffault_call_title(callback: CallbackQuery,
                              state: FSMContext,
                              category: str):

    await bot_message.add_field(state, "Категория", category)
    await title_step.show(callback, state)



@inc_it_fork_maker.register_callback(name="no_inet", text="Нет интернета")
async def inet_truble(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call no_inet_handler")
    await bot_message.add_field(state, "Категория", "Отстуствие интернета")
    await call_title(callback, state)


@inc_it_fork_maker.register_callback(name="invalid_mail", text="Не работает почта")
async def mail_truble(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call invalid_mail_handler")
    await bot_message.add_field(state, "Категория", "Не работает почта")
    await call_title(callback, state)


@inc_it_fork_maker.register_callback(name="invalid_mail", text="Не работает почта")
async def rdp_truble(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call invalid_mail_handler")
    await call_title(callback, state)

