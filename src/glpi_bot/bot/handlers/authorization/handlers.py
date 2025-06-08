from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from datetime import datetime
from typing import Callable
import logging

from glpi_bot.bot.handlers.authorization.models import AuthState
from glpi_bot.services import DBService, EmailConfirmation
from glpi_bot.bot.states import AuthStates

from .models import AuthState
from glpi_bot.bot.keyboards import auth_code_kb, succ_kb
from .settings import LENGTH_CODE, MAIL_NOT_FOUND, USER_NOT_FOUND, AUTHORIZATION_ERROR


logger = logging.getLogger(__name__)


def setup_authorization(
    db_service: DBService,
    mail_confirmation: EmailConfirmation,
    get_user_mail: Callable[[str], str]
) -> Router:
    router = Router()

    async def get_auth_state(state: FSMContext) -> AuthState:
        data = await state.get_data()
        if 'auth_state' not in data:
            data['auth_state'] = AuthState()
            await state.set_data(data)
        return data['auth_state']

    async def send_code(mail):
        logger.debug(f"Отправка кода на <{mail}>")
        code = await mail_confirmation.send_confirmation_email(mail, length=LENGTH_CODE)
        if code is None:
            raise Exception("Не удалось отправить код")
        return code

    @router.message(AuthStates.LOGIN, F.text != "Изменить логин")
    async def process_login(message: types.Message, state: FSMContext):
        auth_state = await get_auth_state(state)

        if auth_state.login_handler.get_blocked_attempts_time() != 0:
            await message.answer("Превышено количество попыток. Попробуйте позже.")
            return

        await state.set_state(AuthStates.LOGIN_HANDLER)
        await login_handler(message, state)

    @router.message(AuthStates.LOGIN_HANDLER, F.text)
    async def login_handler(message: types.Message, state: FSMContext):
        auth_state = await get_auth_state(state)

        if auth_state.login_handler.get_blocked_attempts_time() != 0:
            await message.answer("Превышено количество попыток.")
            return

        login = message.text
        auth_state.login_handler.add_attempt()

        try:
            mail = get_user_mail(login)
            if mail == "None":
                raise LDAPMailNotFound
        except LDAPMailNotFound:
            await message.answer(MAIL_NOT_FOUND)
            await state.clear()
            return
        except LDAPUserNotFound:
            await message.answer(USER_NOT_FOUND)
            return
        except LDAPError:
            await message.answer(AUTHORIZATION_ERROR)
            await state.clear()
            return
        except Exception:
            await message.answer(AUTHORIZATION_ERROR)
            await state.clear()
            return

        auth_state.mail = mail
        auth_state.login = login
        auth_state.login_handler.reset()

        await state.set_state(AuthStates.CODE)
        await process_code(message, state)

    @router.message(AuthStates.CODE, F.text)
    async def process_code(message: types.Message, state: FSMContext):
        auth_state = await get_auth_state(state)
        mail = auth_state.mail

        if auth_state.code_handler.get_blocked_request_time() != 0:
            await message.answer("Ждите перед следующей отправкой.", reply_markup=auth_code_kb())
            return

        try:
            code = await send_code(mail)
        except Exception:
            await message.answer("Ошибка отправки кода.")
            await state.clear()
            return

        auth_state.code = code
        auth_state.code_handler.last_request_time = datetime.now()

        await message.answer(
            f"Код отправлен на <b>{mail}</b>", parse_mode="HTML", reply_markup=auth_code_kb()
        )
        await state.set_state(AuthStates.CODE_HANDLER)

    @router.message(AuthStates.CODE_HANDLER, F.text.func(lambda t: t.isdigit() and len(t) == 4))
    async def code_handler(message: types.Message, state: FSMContext):
        auth_state = await get_auth_state(state)

        if not auth_state.is_code_valid():
            await message.answer("Код просрочен.", reply_markup=auth_code_kb())
            auth_state.code_handler.reset()
            return

        if auth_state.code_handler.get_blocked_attempts_time() != 0:
            await message.answer("Слишком много попыток.", reply_markup=auth_code_kb())
            return

        if message.text != auth_state.code:
            auth_state.code_handler.add_attempt()
            await message.answer("Неверный код", reply_markup=auth_code_kb())
            return

        await message.answer("Успешно!", reply_markup=succ_kb())

        try:
            db_service.save_user(telegram_id=message.from_user.id, login=auth_state.login)
        except Exception as e:
            logger.warning(f"Ошибка записи пользователя: {e}")

        await state.clear()

    return router
