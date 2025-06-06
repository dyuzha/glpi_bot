import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from glpi_bot.bot.handlers.utils import default_handle
from glpi_bot.bot.states import FinalStates
from glpi_bot.bot.keyboards import base_buttons
from glpi_bot.bot.handlers.tickets import bot_message, incident_1c_fork_maker


logger = logging.getLogger(__name__)


@incident_1c_fork_maker.register_callback(name="lic", text="Проблема с лицензией")
async def lic_handler(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call lic_handler")
    await bot_message.add_field(state, "Категория", "Проблема с лицензией")

    prompt = await bot_message.render(state,
                                      "💬 Введите заголовок заявки"
                                      "(Краткое описание проблемы)"
                                      )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[base_buttons])
    await state.set_state(FinalStates.title)
    await default_handle(callback, state, prompt, keyboard)


@incident_1c_fork_maker.register_callback(name="obmen", text="Проблема с обменом")
async def obmen_handler(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call obmen_handler")
    await bot_message.add_field(state, "Категория", "Проблема с обменом")

    prompt = await bot_message.render(state,
                                      "💬 Введите заголовок заявки"
                                      "(Краткое описание проблемы)"
                                      )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[base_buttons])

    await state.set_state(FinalStates.title)
    await default_handle(callback, state, prompt, keyboard)
