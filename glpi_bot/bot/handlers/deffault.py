import logging
from aiogram import types, F
from aiogram.filters import Command, StateFilter
from bot.keyboards import main_kb
from bot import dp
from services import DBInterface
from aiogram.fsm.context import FSMContext
from bot.states import Base, Authorization

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
    # Отправляем приветсвенное сообщение
    await message.answer(START_MESSAGE)
    # Вручную вызываем следующий обработчик
    await cmd_begin(message, state)


@dp.message(StateFilter(None))
async def handle_first_message(message: types.Message, state: FSMContext):
    await cmd_begin( message, state)


@dp.message(Command("begin"))
async def cmd_begin(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        logger.info(f"User {user_id} started bot")

        # Отправляем приветсвенное сообщение
        # await message.answer(START_MESSAGE)

        # Получаем логин из БД
        try:
            login = DBInterface.get_login(telegram_id=user_id)
        except Exception as e:
            logger.error(f"Database error for user {user_id}: {str(e)}")
            await message.answer("Произошла ошибка при проверке авторизации. Попробуйте позже.")
            return

        # Если пользователь не найден, отправляем на регистрацию
        if login is None:
            await message.answer(
                AUTH_REQUIRED_MESSAGE, parse_mode="HTML",
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.info(f"User {user_id} needs authorization")
            await state.set_state(Authorization.waiting_for_login)

        # Иначе перенаправляем на составление заявки
        else:
            logger.info(f"User {user_id} already authorized as {login}")
            await message.answer(
                "Воспользуйся кнопками ниже, для взаимодействия с ботом",
                reply_markup=main_kb()
            )
            await state.update_data(login=login)
            await state.set_state(Base.authorization)

    except Exception as e:
        logger.error(f"Unexpected error in start command for user {user_id if 'user_id' in locals() else 'unknown'}: {str(e)}")
        await message.answer("Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.")
