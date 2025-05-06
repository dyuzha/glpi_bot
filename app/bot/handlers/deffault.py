import logging
from aiogram import types
from aiogram.filters import Command
from bot.keyboards import main_kb
from bot import dp
from services import DBInterface
from aiogram.fsm.context import FSMContext
from bot.states import Base

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


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        logger.info(f"User {user_id} started bot")

        # Отправляем приветсвенное сообщение
        await message.answer(START_MESSAGE)

        # Получаем логин из БД с обработкой ошибок
        try:
            login = DBInterface.get_login(telegram_id=user_id)
        except Exception as e:
            logger.error(f"Database error for user {user_id}: {str(e)}")
            await message.answer("Произошла ошибка при проверке авторизации. Попробуйте позже.")
            return

        if login is None:
            await message.answer(AUTH_REQUIRED_MESSAGE, parse_mode="HTML")
            logger.info(f"User {user_id} needs authorization")
            await state.set_state(Base.waiting_authorization)


        else:
            logger.info(f"User {user_id} already authorized as {login}")
            await message.answer(START_MESSAGE, reply_markup=main_kb())
            await state.set_state(Base.authorization)

    except Exception as e:
        logger.error(f"Unexpected error in start command for user {user_id if 'user_id' in locals() else 'unknown'}: {str(e)}")
        await message.answer("Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.")
