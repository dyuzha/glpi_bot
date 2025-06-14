from functools import partial
import logging
from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, InlineKeyboardMarkup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router

from glpi_bot.bot.handlers.tickets.models.steps.select_auto_step import SelectAutoInlineStep, SelectInlineStep
from glpi_bot.bot.handlers.utils import add_step
from glpi_bot.bot.states import TestStates, TicketStates, BaseStates
from glpi_bot.bot.text import *
from glpi_bot.bot.keyboards import incident_types_kb, request_types_kb, base_buttons


logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "Создать заявку", BaseStates.complete_autorisation)
async def init_create_ticket(message: Message, state: FSMContext):
    """Выбрать Инцидент/Запрос"""
    logger.debug(f"Call init_create_ticket")
    await state.set_state(TicketStates.type)

    prompt = SELECT_WILL_TYPE_TICKET
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛠 Инцидент", callback_data="incident")],
            [InlineKeyboardButton(text="📝 Запрос", callback_data="request")],
            [InlineKeyboardButton(text="ТЕСТ", callback_data="test")],
            [InlineKeyboardButton(text=CANCEL_KEY, callback_data="cancel")]
        ]
    )

    await add_step(state, prompt=prompt, keyboard=keyboard)

    # Запоминаем сообщение, чтобы его можно было всегда редактировать
    sent_msg = await message.answer(prompt, reply_markup=keyboard)
    await state.update_data(bot_message_id=sent_msg.message_id)


async def set_type(callback: CallbackQuery, state: FSMContext, type: int):
    await state.update_data(type=type)


SelectInlineStep(
        filters=(F.data == "incident", StateFilter(TicketStates.type)),
        state=TicketStates.incident,
        prompt = "🛠 Выберите тип инцидента:",
        keyboard=incident_types_kb(),
        before_callback=partial(set_type, type=1),
).register_handler(router)


SelectInlineStep(
        filters=(F.data == "request", StateFilter(TicketStates.type)),
        state=TicketStates.incident,
        prompt = "🛠 Выберите тип запроса:",
        keyboard=request_types_kb(),
        before_callback=partial(set_type, type=2),
).register_handler(router)


test_auto_inline = SelectAutoInlineStep(
        filters=(F.data == "test", StateFilter(TicketStates.type)),
        state=TestStates.test1,
        prefix = "main_prefix",
        prompt = "[Main] Выберите один из предложенных шагов",
        base_buttons = base_buttons,
        )

sub_2 = SelectInlineStep(
        state=TestStates.test2,
        prompt = "[Sub] Выберите один из предложенных шагов",
        keyboard=incident_types_kb(),
)

sub_3 = SelectInlineStep(
        state=TestStates.test2,
        prompt = "[Sub] Выберите один из предложенных шагов",
        keyboard=request_types_kb(),
)

test_auto_inline.set_steps({"sub_2": sub_2, "sub_3": sub_3 })
test_auto_inline.register_handler(router)



#
#
# SelectAutoInlineStep(
#         filters=(F.data == "inc_1c", StateFilter(TicketStates.incident)),
#         state=TestStates.test4,
#         steps = [...],
#         prefix = "prefix",
#         prompt = "Выберите один из предложенных шагов",
#         base_buttons = base_buttons)
# ).register_handler(router)


# @router.callback_query(F.data == "incident", StateFilter(TicketStates.type))
# async def process_incident(callback: CallbackQuery, state: FSMContext):
#     logger.debug(f"Call process_incident")
#     await state.set_state(TicketStates.incident)
#     await state.update_data(type=1)
#
#     prompt = "🛠 Выберите тип инцидента:"
#     keyboard = incident_types_kb()
#
#     await add_step(state=state, prompt=prompt, keyboard=keyboard)
#     if isinstance(callback.message, Message):
#         await callback.message.edit_text(prompt, reply_markup=keyboard)
#     await callback.answer()


# @router.callback_query(F.data == "request", StateFilter(TicketStates.type))
# async def process_request(callback: CallbackQuery, state: FSMContext):
#     logger.debug(f"Call process_request")
#     await state.set_state(TicketStates.request)
#     await state.update_data(type=2)
#
#     prompt = "📝 Выберите тип запроса:"
#     keyboard = request_types_kb()
#
#     await add_step(state=state, prompt=prompt, keyboard=keyboard)
#     if isinstance(callback.message, Message):
#         await callback.message.edit_text(prompt, reply_markup=keyboard)
#     await callback.answer()
