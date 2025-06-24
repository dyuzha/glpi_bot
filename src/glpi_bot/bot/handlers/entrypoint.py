import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types.message import Message
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from glpi_bot.bot.states import BaseStates, AuthStates
from glpi_bot.services import DBService
from glpi_bot.bot.keyboards import main_kb
from glpi_bot.bot.text_constants import START_MESSAGE, AUTH_REQUIRED_MESSAGE


logger = logging.getLogger(__name__)


def setup_entrypoint(db: DBService) -> Router:
    router = Router()

    async def check_register(user_id: int):
        try:
            login = await db.get_login(telegram_id=user_id)
        except Exception as e:
            logger.error(f"Database error for user {user_id}: {str(e)}")
            raise
        return login


    async def main_menu(message: Message, state: FSMContext):
        logger.debug("Call main_menu")
        user_id = message.from_user.id

        login = await check_register(user_id)

        if login is None:
            await state.set_state(AuthStates.LOGIN)
            # await state.set_state(BaseStates.waiting_autorisation)
            await message.answer(AUTH_REQUIRED_MESSAGE, parse_mode="HTML",
                                 reply_markup=ReplyKeyboardRemove())
            # await process_login(message, state)
            return

        await state.update_data(login=login)
        await state.set_state(BaseStates.complete_autorisation)
        await message.answer(START_MESSAGE, reply_markup=main_kb())


    @router.message(Command("start"))
    async def cmd_start(message: Message, state: FSMContext):
        logger.debug("Call cmd_start")
        await state.clear()
        await main_menu(message, state)

    return router
