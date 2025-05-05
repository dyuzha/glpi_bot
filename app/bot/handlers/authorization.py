import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards import main_kb
from bot import dp
from bot.states import Authorization
from mail import mail_confirmation

logger = logging.getLogger(__name__)  # Используем __name__ для автоматического определения имени модуля

@dp.message(Command('authorization'))
async def authorization(messages: types.Message, state: FSMContext):
    await messages.answer(
    "Для продолжения взаимодействия с ботом необходима авторизация\n"
    "Введите свой логин, используемый в вашей организации (н-р: ivanov_ii):"
    )
    await state.set_state(Authorization.waiting_for_login)

@dp.message(Authorization.waiting_for_login)
async def handle_email(messages: types.Message, state: FSMContext):
    # Проверка на корректность
    # ...
    login = messages.text
    email = str(login).join("@gmail.com")

    code = mail_confirmation.generate_confirmation_code()

    await messages.answer(
        f"На {email} был отправлен код авторизации.\n"
        f"Введите его для завершения авторизации"
    )
    await state.set_state(Authorization.waiting_for_code)


@dp.message(Authorization.waiting_for_code)
async def verify_code(messages: types.Message, state: FSMContext):
    code = mail_confirmation.generate_confirmation_code()
    mail_confirmation.send_confirmation_email(email)
    user_code = messages.text
    for _ in 5:
        if code_1 == code_2:
            break
        await messages.answer(
            f""
            f"Введите его для завершения авторизации"
        )
        login = messages.text
        email = str(login).join("@gmail.com")


    await messages.answer(
        f"На {email} был отправлен код авторизации.\n"
        f"Введите его для завершения авторизации"
    )
    await state.set_state(Authorization.waiting_for_code)

