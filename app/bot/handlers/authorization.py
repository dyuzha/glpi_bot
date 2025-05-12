import logging
from aiogram import types, F
# from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards import auth_kb, main_kb
from bot import dp
from bot.states import Authorization, Base
from services import mail_confirmation, DBInterface, get_user_mail
from datetime import datetime, timedelta
from services.exceptions import LDAPError, LDAPUserNotFound, LDAPMailNotFound
# from services import ldap_service


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

# @dp.message(Base.waiting_authorization)
# async def authorization(messages: types.Message, state: FSMContext):
#     await messages.answer(REGISTER_NEEDED,
#                           reply_markup=types.ReplyKeyboardRemove())
#     await state.set_state(Authorization.waiting_for_login)


@dp.message(Authorization.change_login, F.text)
@dp.message(Authorization.waiting_for_login, F.text)
async def handle_login(messages: types.Message, state: FSMContext):
    login = str(messages.text).strip()
    logging.debug(f"Получен логин от пользоватля: {login}")
    await state.update_data(login=login)

    state_data = await state.get_data()

    # проверка временного ограничения на запрос кода
    last_request = state_data.get('last_request_time')
    if last_request and (datetime.now() - last_request) < timedelta(minutes=1):
        remaining = 60 - (datetime.now() - last_request).seconds
        await messages.answer(
            f"⏳ Повторный запрос кода возможен через {remaining} секунд"
        )
        return

    # Полкучение email
    try:
        logger.debug(f"Поиск email для {login}")
        mail = get_user_mail(login)
        logger.debug(f"Email получен:{mail}")

        # Обработка, если email не найден
        if mail == "None":
            raise LDAPMailNotFound

        await state.update_data(email=mail)
        await state.set_state(Authorization.send_code)

    except LDAPMailNotFound as e:
        logger.warning(f"Error: {e}")
        await messages.answer(MAIL_NOT_FOUND)
        await state.clear()

    except LDAPUserNotFound as e:
        logger.warning(f"Error: {e}")
        await messages.answer(USER_NOT_FOUND)
        await state.clear()

    except LDAPError as e:
        logger.critical(f"Error: {e}")
        await messages.answer(AUTHORIZATION_ERROR)
        await state.clear()

    except Exception as e:
        logger.critical(f"Error: {e}")
        await messages.answer(AUTHORIZATION_ERROR)
        await state.clear()


@dp.message(Authorization.send_code, F.text)
async def send_code(messages: types.Message, state: FSMContext):
    """Выполняет отправку кода на email"""
    state_data = await state.get_data()
    mail = state_data["email"]
    try:
        code = await mail_confirmation.send_confirmation_email(mail)
        if code is None:
            raise Exception("Не удалось отправить код")

        await state.update_data(
            email=mail,
            code=code,
            code_created_at=datetime.now(),
            last_request_time=datetime.now(),
        )

        await messages.answer(
            f"На <b>{mail}</b> был отправлен 8-значный код авторизации.\n"
            f"⏳ Код действителен в течение 5 минут\n"
            f"Введите его для завершения авторизации:",
            parse_mode="HTML", reply_markup=auth_kb(),
        )
        await state.set_state(Authorization.waiting_for_code)

    except Exception as e:
        logger.error(f"Ошибка отправки кода на {mail}: {e}")
        await messages.answer(
            "⚠️ Не удалось отправить код подтверждения.\n"
            "Попробуйте позже или обратитесь в поддержку."
        )
        await state.clear()


@dp.message(Authorization.waiting_for_code, F.text.func(
    lambda text: text.isdigit() and len(text) == 8))
async def handle_code(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    # Проверка срока действия кода
    code_created_at = state_data.get('code_created_at')
    if code_created_at and (datetime.now() - code_created_at) > timedelta(minutes=5):
        await message.answer(
            "⌛️ Время действия кода истекло.\n"
            "Запросите новый код, введя логин снова."
        )
        await state.set_state(Authorization.waiting_for_login)
        return

    if message.text != state_data['code']:
        await message.answer("❌ Неверный код подтверждения. \
                Попробуйте еще раз:")
    else:
        await message.answer("✅ Авторизация успешно завершена!", reply_markup=main_kb())
        DBInterface.save_user(telegram_id=message.from_user.id, login=state_data['login'])
        await state.clear()
        await state.set_state(Base.authorization)


# Обработчик для команды "отправить код повторно"
@dp.message(Authorization.waiting_for_code, F.text.lower() == "отправить код повторно")
async def resend_code_handler(messages: types.Message, state: FSMContext):
    state_data = await state.get_data()
    email = state_data['email']

    # проверка временного ограничения на запрос кода
    last_request = state_data.get('last_request_time')
    if last_request and (datetime.now() - last_request) < timedelta(minutes=1):
        remaining = 60 - (datetime.now() - last_request).seconds
        await messages.answer(
            f"⏳ Повторный запрос кода возможен через {remaining} секунд"
        )
        return

    try:
        new_code = await mail_confirmation.send_confirmation_email(email)

        if not new_code:
            raise Exception("Не удалось отправить код")

        await state.update_data(
            email=email,
            code=new_code,
            code_created_at=datetime.now(),
            # last_request_time=datetime.now(),
        )

        await messages.answer(
            f"На <b>{email}</b> повторно был отправлен 8-значный код авторизации.\n"
            f"⏳ Код действителен в течение 5 минут\n"
            f"Введите его для завершения авторизации:",
            parse_mode="HTML", reply_markup=auth_kb(),
        )
        await state.set_state(Authorization.waiting_for_code)

    except Exception as e:
        logger.error(f"Ошибка отправки кода на {email}: {e}")
        await messages.answer(
            "⚠️ Не удалось отправить код подтверждения.\n"
            "Попробуйте позже или обратитесь в поддержку."
        )
        await state.clear()


@dp.message(Authorization.waiting_for_code, F.text.lower() == "Изменить логин")
async def change_login_handler(messages: types.Message, state: FSMContext):
    await messages.answer(
        "Введите свой логин, используемый в вашей организации (н-р: ivanov_ii):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Authorization.change_login)
