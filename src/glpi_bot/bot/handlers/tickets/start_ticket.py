from functools import partial
import logging
from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, InlineKeyboardMarkup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router

from glpi_bot.bot.handlers.tickets.models.steps import SelectInlineStep, BaseAutoStep
from glpi_bot.bot.handlers.utils import add_step
from glpi_bot.bot.states import TestStates, TicketStates, BaseStates, FlowStates
from glpi_bot.bot.text import *
from glpi_bot.bot.keyboards import incident_types_kb, request_types_kb, base_buttons
from glpi_bot.bot.handlers.tickets.instances import bot_message


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
        state=TicketStates.request,
        prompt = "🛠 Выберите тип запроса:",
        keyboard=request_types_kb(),
        before_callback=partial(set_type, type=2),
).register_handler(router)


request = BaseAutoStep(
        filters=(F.data == "test", StateFilter(TicketStates.type)),
        state=TestStates.test1,
        prompt = "🛠 Выберите тип запроса:",
        before_callback=partial(set_type, type=2),
        base_buttons=base_buttons,
        )


req_1c = BaseAutoStep(
        state=TestStates.test2,
        prompt = "Выберите направление запроса",
        base_buttons=base_buttons,
        )

req_it = BaseAutoStep(
        state=TestStates.test3,
        prompt = "Выберите направление запроса",
        base_buttons=base_buttons,
        )

async def set_category(callback: CallbackQuery, state: FSMContext,
                       id: int, category: str):
    await state.update_data(itilcategories_id = id)
    await state.update_data(title = category)
    await bot_message.add_field(state, "Категория", category)


req_it["Добавление/удаление прав/доступов/пользователей"] = BaseAutoStep(
        state=TestStates.test3, prompt="Тестовый",
        before_callback=partial(set_category, id=20, category="Настройка прав")
        )


req_it["Обслуживание орг техники, рабочих мест"] = BaseAutoStep(
        state=TestStates.test3, prompt="Тестовый")


req_it["Установка/удаление ПО"] = BaseAutoStep(
        state=TestStates.test3, prompt="Тестовый")


request["По 1с"] = req_1c
request["По IT"] = req_it


request.register_handler(router)


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
