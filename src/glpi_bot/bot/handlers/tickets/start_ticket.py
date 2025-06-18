import logging
from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, InlineKeyboardMarkup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router

from glpi_bot.bot.handlers.utils import add_step, default_handle
from glpi_bot.bot.states import TicketStates, BaseStates
from glpi_bot.bot.text import CANCEL_KEY, SELECT_TYPE_TICKET
from glpi_bot.bot.keyboards import incident_types_kb, request_types_kb


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
    prompt = SELECT_TYPE_TICKET
    keyboard = type_kb

    # Добавляем текущий шаг (как-будто он был вызван с inline_keyboard и в type state)
    await state.set_state(TicketStates.type)
    await add_step(state, prompt=prompt, keyboard=keyboard)

    # Запоминаем сообщение, чтобы его можно было всегда редактировать
    sent_msg = await message.answer(prompt, reply_markup=keyboard)
    await state.update_data(bot_message_id=sent_msg.message_id)


@router.callback_query(F.data == "incident", StateFilter(TicketStates.type))
async def process_incident(callback: CallbackQuery, state: FSMContext):
    logger.debug(f"Call process_incident")
    await state.set_state(TicketStates.incident)
    await state.update_data(type=1)

    prompt = "🛠 Выберите направление инцидента:"
    keyboard = incident_types_kb()
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(F.data == "request", StateFilter(TicketStates.type))
async def process_request(callback: CallbackQuery, state: FSMContext):
    logger.debug(f"Call process_request")
    await state.set_state(TicketStates.request)
    await state.update_data(type=2)

    prompt = "📝 Выберите направление запроса:"
    keyboard = request_types_kb()

    await default_handle(callback, state, prompt, keyboard)
