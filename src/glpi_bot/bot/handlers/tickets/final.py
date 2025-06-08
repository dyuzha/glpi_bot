# bot/handlers/final.py

import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from glpi_bot.bot.handlers.tickets.base import back_handler
from glpi_bot.bot.handlers.tickets.models.dinamic_bod_message import DynamicBotMessage
from glpi_bot.bot.handlers.tickets.models.text_input_step import TextInputStep
from glpi_bot.bot.handlers.tickets.steps.title_step import title_step
from glpi_bot.bot.handlers.utils import add_step
from glpi_bot.bot.states import FinalStates, BaseStates
from glpi_bot.bot.keyboards import base_buttons, confirm_kb, main_kb


logger = logging.getLogger(__name__)
router = Router()
bot_message = DynamicBotMessage()


@router.message(StateFilter(FinalStates.title))
async def process_title(message: Message , state: FSMContext):
    logger.debug(f"Call process_title")
    await title_step(message, state)

    # Переход к следующему шагу
    prompt = await bot_message.render(state, "💬 Опишите проблему более подробно")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[base_buttons])
    await state.set_state(FinalStates.description)
    await add_step(state, prompt=prompt, keyboard=keyboard)
    await bot_message.update_message(message, state, "💬 Опишите проблему более подробно")


 # @router.message(StateFilter(FinalStates.title))
# async def process_title(message: Message , state: FSMContext):
#     logger.debug(f"Call process_title")
#
#     text = message.text.strip()
#     await message.delete()
#
#     # Валидация
#     if len(text) < 10:
#         await bot_message.update_message(message, state,
#                              f"❗Заголовок:\n{text} - слишком короткий\n"
#                              "Минимальная длина 10 символов\n"
#                              "Попробуйте еще раз")
#         return
#
#     # Сохраняем поле в общий шаблон
#     await state.update_data(title=text)
#     await bot_message.add_field(state, "Заголовок", text)
#
#     # Переход к следующему шагу
#     prompt = await bot_message.render(state, "💬 Опишите проблему более подробно")
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[base_buttons])
#     await state.set_state(FinalStates.description)
#     await add_step(state, prompt=prompt, keyboard=keyboard)
#     await bot_message.update_message(message, state, "💬 Опишите проблему более подробно")


@router.callback_query(F.data == "navigation_back", StateFilter(FinalStates.description))
async def local_back_in_title(callback: CallbackQuery, state: FSMContext):
    logger.debug("local_back_in_title")
    await bot_message.del_field(state, "Заголовок")
    await back_handler(callback, state)
    await callback.answer()


@router.message(StateFilter(FinalStates.description))
async def process_description(message: Message , state: FSMContext):
    logger.debug(f"Call process_description")

    text = message.text.strip()
    await message.delete()

    # Валидация
    if len(text) < 10:
        await bot_message.update_message(message, state,
                             f"❗Описание:\n{text} - слишком короткий\n"
                             "Минимальная длина 10 символов\n"
                             "Попробуйте еще раз")
        return

    # Сохраняем поле в общий шаблон
    await state.update_data(description=text)
    await bot_message.add_field(state, "Описание", text)

    # Переход к следующему шагу
    prompt = await bot_message.render(state)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[base_buttons])
    await state.set_state(FinalStates.confirm)
    await add_step(state, prompt=prompt, keyboard=keyboard)
    await bot_message.update_message(message, state, "⏳Подтвердите отправку заявки!", keyboard=confirm_kb())


@router.callback_query(F.data == "navigation_back", StateFilter(FinalStates.confirm))
async def local_back_in_description(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call local_back_in_description")
    await bot_message.del_field(state, "Описание")
    await back_handler(callback, state)
    await callback.answer()


@router.callback_query(F.data == "confirm", StateFilter(FinalStates.confirm))
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call process_confirm")
    await bot_message.update_message(callback.message, state,
            "✅ Заявка успешно отправлена!",
            keyboard=InlineKeyboardMarkup(inline_keyboard=[])
    )
    await state.clear()
    await state.set_state(BaseStates.complete_autorisation)
    await callback.answer()
    await callback.message.answer(
            "Чтобы создать заявку: воспользуйтесь кнопками ниже 👇",
            reply_markup=main_kb()
    )
