# bot/handlers/fork_makers.py

import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.handlers.tickets.models import DynamicBotMessage
from glpi_bot.bot.handlers.tickets.models import BaseForkMaker
from glpi_bot.bot.states import OneCStates, TicketStates, FinalStates, BaseStates
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from glpi_bot.bot.keyboards import base_buttons
from glpi_bot.bot.handlers.utils import default_handle


logger = logging.getLogger(__name__)
router = Router()

incident_1c_fork_maker = BaseForkMaker(base_buttons=base_buttons)


@router.callback_query(F.data == "inc_1c",
        StateFilter(TicketStates.type, OneCStates.inc_1c))
async def select_category(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите вашу проблему"
    keyboard = incident_1c_fork_maker.build_keyboard()
    await state.set_state(OneCStates.inc_1c)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(OneCStates.inc_1c))
async def callback_dispatcher(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await incident_1c_fork_maker(callback, state)


