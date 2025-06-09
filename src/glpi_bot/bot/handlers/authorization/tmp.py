
import logging
from glpi_bot.services import db_service
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.keyboards import auth_code_kb, succ_kb
from glpi_bot.bot import AuthState
from glpi_bot.bot.states import AuthStates
from glpi_bot.services import mail_confirmation, get_user_mail
from datetime import datetime
from glpi_bot.services.exceptions import LDAPError, LDAPUserNotFound, LDAPMailNotFound

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

router = Router()

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


@router.message(AuthStates.LOGIN, F.text != "Изменить логин")
async def process_login(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние LOGIN")
    auth_state = await get_auth_state(state)

    # Проверка на наличие блокировки
    remaining_attempts_time = auth_state.login_handler.get_blocked_attempts_time()
    if remaining_attempts_time != 0:
        await message.answer(
            f"Превышено количество попыток. \
Попробуйте через {remaining_attempts_time} секунд",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    await state.set_state(AuthStates.LOGIN_HANDLER)
    await login_handler(message, state)


@router.message(AuthStates.LOGIN_HANDLER, F.text != "Изменить логин")
async def login_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние LOGIN_HANDLER")
    auth_state = await get_auth_state(state)

    # Проверка на наличие блокировки
    if auth_state.login_handler.get_blocked_attempts_time() != 0:
        remaining = auth_state.login_handler.get_blocked_attempts_time()
        await message.answer(
            f"Превышено количество попыток. Попробуйте через {remaining} секунд",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    auth_state.login_handler.add_attempt()
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
        await message.answer(
            USER_NOT_FOUND, reply_markup=types.ReplyKeyboardRemove()
        )
        logger.debug(f"Неудачная попытка ввода логина: {message.text}")


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


@router.message(AuthStates.CODE, F.text)
async def process_code(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние CODE")
    auth_state = await get_auth_state(state)
    mail = auth_state.mail

    # Обработка возможности отправки кода
    remaining_blocked_time = auth_state.code_handler.get_blocked_request_time()
    if remaining_blocked_time != 0:
        await message.answer(
            f"Отправить код повторно возможно через {remaining_blocked_time} \
секунд", reply_markup=auth_code_kb()
        )
        return

    # Отправка кода
    try:
        code = await send_code(mail)
    except Exception as e:
        logger.error(f"Ошибка отправки кода на {mail}: {e}")
        await message.answer(
            "⚠️ Не удалось отправить код подтверждения.\n"
            "Попробуйте позже или обратитесь в поддержку.",
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


@router.message(AuthStates.CODE_HANDLER, F.text.func(
    lambda text: text.isdigit() and len(text) == 4))
async def code_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Переход в состояние CODE_HANDLER")
    auth_state = await get_auth_state(state)

    # Проверка не истекло ли время действия кода
    if not auth_state.is_code_valid():
        logger.debug("Время действия кода истекло")
        await message.answer(
            "⌛️ Время действия кода истекло.\n"
            "Запросите новый код.",
            reply_markup=auth_code_kb()
        )
        auth_state.code_handler.reset()
        return

    # Проверка на наличие блокировки
    if auth_state.code_handler.get_blocked_attempts_time() != 0:
        remaining = auth_state.code_handler.get_blocked_attempts_time()
        await message.answer(
            f"Превышено количество попыток. Попробуйте через {remaining} секунд",
            reply_markup=auth_code_kb()
        )
        return

    auth_state.code_handler.add_attempt()

    # Обработка неправильного кода
    if message.text != auth_state.code:
        logger.debug(f"Неудачная попытка ввода кода: {message.text}")
        await message.answer(f"❌ Неверный код подтверждения")

        # Подсчет оставшихся попыток
        remaining_attempts = auth_state.code_handler.remaining_attempts
        logger.debug(f"Осталось попыток {remaining_attempts}")
        await message.answer(f"Осталось попыток: {remaining_attempts}")

        # Выставление блокировки, если попытки закончились
        if remaining_attempts == 0:
            remaining_time = auth_state.code_handler.set_attempts_blocked_until()
            logger.debug(f"Выставлена блокировка на {remaining_time} секунд")
            await message.answer(f"Попробуйте через {remaining_time} секунд")

        return

    logger.debug(f"Успешная авторизация")
    await success_handler(message, state)




@router.message(AuthStates.SUCCESS, F.text)
async def success_handler(message: types.Message, state: FSMContext):
    auth_state = await get_auth_state(state)
    await message.answer(
        "✅ Авторизация успешно завершена!", reply_markup=succ_kb()
    )
    try:
        db_service.save_user(
            telegram_id=message.from_user.id,
            login=auth_state.login
        )
        logger.info(f"Добавлен новый пользоватьель в базу данных: \n\
tg_id: {message.from_user.id}\nlogin: {auth_state.login}")
    except Exception as e:
        logger.warning(f"Error: {e}")
    await state.clear()
