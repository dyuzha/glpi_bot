import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from bot.keyboards import auth_code_kb,  auth_login_kb, main_kb
from bot import dp, AuthState
from bot.states import Base, AuthStates
from .deffault import cmd_begin
from services import mail_confirmation, DBInterface, get_user_mail
from datetime import datetime, timedelta
from services.exceptions import LDAPError, LDAPUserNotFound, LDAPMailNotFound

TIMEOUT_REPEAT = 10
LENGTH_CODE = 4


logger = logging.getLogger(__name__)


REGISTER_NEEDED=(
    "Для продолжения взаимодействия с ботом необходима авторизация\n"
    "Введите свой логин, используемый в вашей организации (н-р: ivanov_ii):"
    )

MAIL_NOT_FOUND=(
    "Mail не найден для данного пользователя\n"
    "Обратитесь к вашему системному администратору"
    )

REPEAT_REQUEST=(
    )

USER_NOT_FOUND= (
    "Пользователь с данным логином не найден.\n"
    "Попробуйте еще раз."
    )

LOGIN_NOT_FOUND=(
    "❌ Пользователь с таким логином не найден.\n"
    "Попробуйте ввести логин еще раз:"
    )

LOGIN_FOUND=(
    "На вашу корпоративную почту: {} направлено письмо с кодом подтверждения.\n"
    )

AUTHORIZATION_ERROR=(
    "Сервис авторизации временно недоступен.\n"
    "Попробуйте позже или обратитесь в поддержку."
    )


async def get_auth_state(state: FSMContext) -> AuthState:
    data = await state.get_data()
    if 'auth_state' not in data:
        data['auth_state'] = AuthState()
        await state.set_data(data)
    return data['auth_state']


async def send_code(mail):
    """Выполняет отправку кода на mail"""
    logger.debug(f"Попытка отправить код на <{mail}>")
    code = await mail_confirmation.send_confirmation_email(mail, length=LENGTH_CODE)
    if code is None:
        raise Exception("Не удалось отправить код")
    return code


@dp.message(AuthStates.LOGIN, F.text != "Изменить логин")
async def process_login(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние LOGIN")
    auth_state = await get_auth_state(state)

    # проверка временного ограничения на изменения логина
    if not auth_state.login_handler.can_make_request():
        remaining = auth_state.login_handler.get_remaining_time()
        await message.answer(
            "⏳ Превышено максимальное число попыток."
            f"Ввести логин снова, будет возможно через {remaining} секунд.",
            reply_markup=auth_login_kb()
        )
        return

    auth_state.login_handler.last_request_time = datetime.now()
    # await state.update_data(auth_state = auth_state)
    # await message.answer(f"Введите свой логин для продолжения")
    await state.set_state(AuthStates.LOGIN_HANDLER)
    await login_handler(message, state)


@dp.message(AuthStates.LOGIN_HANDLER, F.text != "Изменить логин")
async def login_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние LOGIN_HANDLER")

    auth_state = await get_auth_state(state)
    login = message.text
    # Полкучение email
    try:
        logger.debug(f"Поиск email для <{login}>")
        mail = get_user_mail(login)
        logger.debug(f"Email получен: <{mail}>")

        # Обработка, если email не найден
        if mail == "None":
            raise LDAPMailNotFound

    except LDAPMailNotFound as e:
        logger.warning(f"Error: {e}")
        await message.answer(MAIL_NOT_FOUND)
        await state.clear()

    except LDAPUserNotFound as e:
        logger.warning(f"Error: {e}")
        await message.answer(USER_NOT_FOUND, reply_markup=auth_login_kb())
        if not auth_state.login_handler.add_attempt():
            remaining = auth_state.login_handler.get_remaining_time()
            await message.answer(f"Неверный логин. Превышено количество попыток.\
Попробуйте через {remaining} секунд.")

            attempts_left = auth_state.login_handler.max_attempts - auth_state.login_handler.attempts
            attempts = attempts_left / auth_state.login_handler.max_attempts

            await message.answer(
                "Пользователь с данным логином не найден.\n"
                "Попробуйте еще раз."
                f"Осталось попыток: {attempts}", reply_markup=auth_login_kb()
            )

    except LDAPError as e:
        logger.critical(f"Error: {e}")
        await message.answer(AUTHORIZATION_ERROR)
        await state.clear()

    except Exception as e:
        logger.critical(f"Error: {e}")
        await message.answer(AUTHORIZATION_ERROR)
        await state.clear()

    else:
        auth_state.mail = mail
        auth_state.login_handler.reset()
        auth_state.login = login
        await state.set_state(AuthStates.CODE)
        # Вручную вызываем следующий обработчик
        await process_code(message, state)


@dp.message(AuthStates.CODE, F.text)
async def process_code(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние CODE")
    auth_state = await get_auth_state(state)
    mail = auth_state.mail

    # Обработка возможности отправки кода
    if not auth_state.code_handler.can_make_request():
        remaining = auth_state.code_handler.get_remaining_time()
        await message.answer(f"Отправить код повторно возможно через \
{remaining} секунд", reply_markup=auth_code_kb())
        return

    # Отправка кода
    try:
        code = await send_code(mail)
    except Exception as e:
        logger.error(f"Ошибка отправки кода на {mail}: {e}")
        await message.answer(
            "⚠️ Не удалось отправить код подтверждения.\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=auth_code_kb()
        )
        await state.clear()
        return

    else:
        auth_state.code = code
        auth_state.code_handler.last_request_time = datetime.now()
        await message.answer(
            f"На <b>{mail}</b> был отправлен 4-значный код авторизации.\n"
            f"⏳ Код действителен в течение 5 минут\n"
            f"Введите его для завершения авторизации:",
            parse_mode="HTML", reply_markup=auth_code_kb(),
        )
        await state.set_state(AuthStates.CODE_HANDLER)


@dp.message(AuthStates.CODE_HANDLER, F.text.func(
    lambda text: text.isdigit() and len(text) == 4))
async def code_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние CODE_HANDLER")
    auth_state = await get_auth_state(state)

    auth_state.code_handler.add_attempt()

    # Проверка не истекло ли время действия кода
    if not auth_state.is_code_valid():
        logger.debug("Время действия кода истекло")
        await message.answer(
            "⌛️ Время действия кода истекло.\n"
            "Запросите новый код.",
            reply_markup=auth_code_kb()
        )
        return

    # Обработка неправильного кода
    if message.text != auth_state.code:
        logger.debug(f"Неудачная попытка ввода кода: {message.text}")


        # Если закончились попытки
        if auth_state.code_handler.get_remaining_time() != 0:
            remaining = auth_state.code_handler.get_remaining_time()
            await message.answer(f"❌ Неверный код подтверждения. \
Превышено количество попыток. Попробуйте через {remaining} секунд",
               reply_markup=auth_code_kb()
            )
            return

        attempts_left = auth_state.code_handler.max_attempts - auth_state.code_handler.attempts

        # Если попытки еще остались
        await message.answer(f"❌ Неверный код подтверждения. \
Осталось попыток: {attempts_left}/{auth_state.code_handler.max_attempts}",
            reply_markup=auth_code_kb()
        )
        return

    logger.debug(f"Успешная авторизация")
    await success_handler(message, state)


@dp.message(AuthStates.CODE_HANDLE R, F.text == "Изменить логин")
async def invalid_login_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Обработка нестандартного ответа")
    """Обработка нестандартного сообщения при вводе логина"""
    await message.answer("Введите другой логин")
    await state.set_state(AuthStates.LOGIN)


@dp.message(AuthStates.CODE_HANDLER, F.text)
async def invalid_code_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Обработка нестандартного ответа")
    """Обработка нестандартного сообщения на запрос кода"""
    match message.text:
        case "Изменить логин":
            await state.set_state(AuthStates.LOGIN)
            await invalid_login_handler(message, state)

        case "Отправить код повторно":
            await process_code(message, state)

        case _:
            await message.answer(f"Код должен содержать только цифры, длина \
должна быть равна {LENGTH_CODE}")


@dp.message(AuthStates.SUCCESS, F.text)
async def success_handler(message: types.Message, state: FSMContext):
    auth_state = await get_auth_state(state)
    await message.answer("✅ Авторизация успешно завершена!", reply_markup=main_kb())
    try:
        DBInterface.save_user(
            telegram_id=message.from_user.id,
            login=auth_state.login
        )
        logger.info(f"Добавлен новый пользоватьель в базу данных: \n\
tg_id: {message.from_user.id}\nlogin: {auth_state.login}")
    except Exception as e:
        logger.warning(f"Error: {e}")
    await state.clear()
    await cmd_begin()
