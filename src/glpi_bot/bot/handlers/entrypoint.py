import logging
from typing import cast
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types.message import Message
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from glpi_bot.bot.keyboards import main_kb
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.states import BaseStates, AuthStates
from glpi_bot.services import DBService


logger = logging.getLogger(__name__)


START_MESSAGE = (
    "👋 Привет! Я ПРОФИТ-бот для работы с GLPI.\n"
    "С моей помощью вы можете создать заявку."
)

AUTH_REQUIRED_MESSAGE = (
    "Для продолжения взаимодействия с ботом необходима авторизация\n"
    "Введите свой логин, используемый в вашей организации "
    "(н-р: <code>ivanov_ii</code>):"
)


def setup_entrypoint(db: DBService) -> Router:
    router = Router()

    def check_register(user_id: int):
        try:
            login = db.get_login(telegram_id=user_id)
        except Exception as e:
            logger.error(f"Database error for user {user_id}: {str(e)}")
            raise
        return login


    async def main_menu(message: Message, state: FSMContext):
        logger.debug("Call main_menu")
        user_id = message.from_user.id

        login = check_register(user_id)

        if login is not None:
            await state.update_data(login=login)
            await state.set_state(AuthStates.LOGIN)
            # await state.set_state(BaseStates.waiting_autorisation)
            await message.answer(AUTH_REQUIRED_MESSAGE, parse_mode="HTML",
                                 reply_markup=ReplyKeyboardRemove())
            # await process_login(message, state)
            return

        await state.set_state(BaseStates.complete_autorisation)
        await message.answer(START_MESSAGE, reply_markup=main_kb())


    @router.message(Command("start"))
    async def cmd_start(message: Message, state: FSMContext):
        logger.debug("Call cmd_start")
        await state.clear()
        await main_menu(message, state)

    return router
