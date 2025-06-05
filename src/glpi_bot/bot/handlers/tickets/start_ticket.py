import logging
from aiogram import F, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router
from glpi_bot.bot.handlers.deffault import BaseStates
from glpi_bot.bot.handlers.utils import add_step, default_handle, register_step
from glpi_bot.bot.states import TicketStates
from glpi_bot.bot.text import *
from bot.keyboards import incident_types_kb, request_types_kb


logger = logging.getLogger(__name__)
router = Router()


type_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛠 Инцидент", callback_data="incident")],
            [InlineKeyboardButton(text="📝 Запрос", callback_data="request")],
            [InlineKeyboardButton(text=CANCEL_KEY, callback_data="cancel")]
        ]
    )


@router.message(F.text == "Создать заявку", BaseStates.complete_autorisation)
async def init_create_ticket(message: Message, state: FSMContext):
    """Выбрать Инцидент/Запрос"""
    logger.debug(f"Call init_create_ticket")
    prompt = SELECT_WILL_TYPE_TICKET
    keyboard = type_kb

    await state.set_state(TicketStates.type)
    await add_step(state, prompt=prompt, keyboard=keyboard)
    sent_msg = await message.answer(prompt, reply_markup=keyboard)
    await state.update_data(bot_message_id=sent_msg.message_id)


@router.callback_query(F.data == "incident", StateFilter(TicketStates.type))
async def process_incident(callback: CallbackQuery, state: FSMContext):
    logger.debug(f"Call process_incident")

    prompt = "🛠 Выберите тип инцидента:"
    keyboard = incident_types_kb()

    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(F.data == "request", StateFilter(TicketStates.type))
async def process_request(callback: CallbackQuery, state: FSMContext):
    logger.debug(f"Call process_request")

    prompt = "📝 Выберите тип запроса:"
    keyboard = request_types_kb()

    await default_handle(callback, state, prompt, keyboard)
