import logging
from aiogram import types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from bot import dp
from services import db_interface

logger = logging.getLogger(__name__)

@dp.message(Command("delete_me"), StateFilter('*'))
async def delete_user(message: types.Message, state: FSMContext):
    """Удаляет пользователя из базы данных"""
    await state.clear()
    user_id = message.from_user.id
    try:
        if db_interface.delete_user(telegram_id=user_id):
            await message.answer("Ваша запись удалена из бд")
            logger.error(f"Пользователь {user_id} успешно удален из бд")
        else:
            await message.answer("Пользователь с вашем id не найден")
    except Exception as e:
        logger.error(f"Ошибка при попытку удаления пользователя {user_id}: {e}")
        await message.answer(
            f"Ошибка при попытку удаления пользователя {user_id}: {e}"
        )
