import logging
from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot import dp
from bot.states import Base
from services import DBInterface

logger = logging.getLogger(__name__)

@dp.message(Command("delete_me"))
async def delete_user(message: types.Message, state: FSMContext):
    """Удаляет пользователя из базы данных"""
    await state.clear()
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
