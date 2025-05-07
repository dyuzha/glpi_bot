import logging
from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from glpi.api import GLPIConnection
from bot.keyboards import main_kb, back_kb, confirm_kb, type_kb
from bot import dp
from bot.states import Base
from services import DBInterface

logger = logging.getLogger(__name__)

@dp.message(Command("delete_me"), Base.authorization)
async def start_ticket_creation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        if DBInterface.delete_user(telegram_id=user_id):
            await message.answer("Ваша запись удалена из бд")
            logger.error(f"Пользователь {user_id} успешно удален из бд")
        else:
            await message.answer("Пользователь с вашем id не найден")
    except Exception as e:
        logger.error(f"Ошибка при попытку удаления пользователя {user_id}: {e}")
        await message.answer(
        f"Ошибка при попытку удаления пользователя {user_id}: {e}"
        )
    finally:
        await state.clear()
