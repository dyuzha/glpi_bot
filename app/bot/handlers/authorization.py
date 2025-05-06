import logging
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards import repeat_code_kb
from bot import dp
from bot.states import Authorization, Base
from services import mail_confirmation, get_email, DBInterface
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

REGISTER_NEEDED=(
    "Для продолжения взаимодействия с ботом необходима авторизация\n"
    "Введите свой логин, используемый в вашей организации (н-р: ivanov_ii):"
    )

REPEAT_REQUEST=(
    )

LOGIN_NOT_FOUND=(
    "❌ Пользователь с таким логином не найден.\n"
    "Попробуйте ввести логин еще раз:"
        )

@dp.message(Base.waiting_authorization)
async def authorization(messages: types.Message, state: FSMContext):
    await messages.answer(REGISTER_NEEDED,
                          reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Authorization.waiting_for_login)


@dp.message(Authorization.waiting_for_login, F.text)
async def handle_login(messages: types.Message, state: FSMContext):
    login = str(messages.text).strip()
    state_data = await state.get_data()

    # проверка временного ограничения на запрос кода
    last_request = state_data.get('last_request_time')
    if last_request and (datetime.now() - last_request) < timedelta(minutes=1):
        remaining = 60 - (datetime.now() - last_request).seconds
        await messages.answer(
            f"⏳ Повторный запрос кода возможен через {remaining} секунд"
        )
        return

    email = get_email(login)

    if email is False:
        await messages.answer(LOGIN_NOT_FOUND)
        return

    elif email is None:
        await messages.answer(
            "Сервис авторизации временно недоступен.\n"
            "Попробуйте позже или обратитесь в поддержку."
        )
        await state.clear()
        return

    try:
        code = await mail_confirmation.send_confirmation_email(email)

        if not code:
            raise Exception("Не удалось отправить код")

        await state.update_data(
            email=email,
            code=code,
            login=login,
            code_created_at=datetime.now(),
            last_request_time=datetime.now(),
        )

        await messages.answer(
            f"На <b>{email}</b> был отправлен 8-значный код авторизации.\n"
            f"⏳ Код действителен в течение 5 минут\n"
            f"Введите его для завершения авторизации:",
            parse_mode="HTML", reply_markup=repeat_code_kb,
        )
        await state.set_state(Authorization.waiting_for_code)

    except Exception as e:
        logger.error(f"Ошибка отправки кода на {email}: {e}")
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
        await message.answer("✅ Авторизация успешно завершена!")
        DBInterface.save_user(telegram_id=message.from_user.id, login=state_data['login'])
        await state.clear()
        await state.set_state(Base.authorization)
