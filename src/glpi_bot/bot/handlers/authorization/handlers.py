from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from datetime import datetime
from typing import Callable
import logging

from glpi_bot.bot.handlers.authorization.models import AuthService
from glpi_bot.services import DBService, EmailConfirmation
from glpi_bot.bot.states import AuthStates, BaseStates

from glpi_bot.services import LDAPMailNotFound, LDAPError, LDAPUserNotFound
from glpi_bot.bot.keyboards import auth_code_kb, main_kb
from .models import AuthService
from .settings import (
        LENGTH_CODE,
        MAIL_NOT_FOUND,
        USER_NOT_FOUND,
        AUTHORIZATION_ERROR
)


logger = logging.getLogger(__name__)


def setup_authorization(
    db_service: DBService,
    mail_confirmation: EmailConfirmation,
    get_user_mail: Callable[[str], str]
) -> Router:
    router = Router()

    async def get_auth_state(state: FSMContext) -> AuthService:
        data = await state.get_data()
        if 'auth_state' not in data:
            data['auth_state'] = AuthService()
            await state.set_data(data)
        return data['auth_state']


    async def send_code(mail):
        """Генерирует и отправляет код на mail"""
        logger.debug(f"Отправка кода на <{mail}>")
        code = await mail_confirmation.send_confirmation_email(mail,
                                                               length=LENGTH_CODE)
        if code is None:
            raise Exception("Не удалось отправить код")
        return code


    @router.message(AuthStates.LOGIN, F.text != "Изменить логин")
    async def process_login(message: types.Message, state: FSMContext):
        logger.debug(f"Переход в состояние LOGIN_HANDLER")
        auth_state = await get_auth_state(state)

        # Проверка на наличие блокировки
        remaining_attempts_time = auth_state.login_handler.get_blocked_attempts_time()
        if remaining_attempts_time != 0:
            await message.answer("Превышено количество попыток."
                f"Попробуйте через {remaining_attempts_time} секунд",
                reply_markup=types.ReplyKeyboardRemove())
            return

        await state.set_state(AuthStates.LOGIN_HANDLER)
        await login_handler(message, state)


    @router.message(AuthStates.LOGIN_HANDLER, F.text != "Изменить логин")
    async def login_handler(message: types.Message, state: FSMContext):
        auth_state = await get_auth_state(state)

        # Проверка на наличие блокировки
        if auth_state.login_handler.get_blocked_attempts_time() != 0:
            remaining = auth_state.login_handler.get_blocked_attempts_time()
            await message.answer("Превышено количество попыток."
                                 f"Попробуйте через {remaining} секунд",
                                 reply_markup=types.ReplyKeyboardRemove())
            return

        login = message.text
        auth_state.login_handler.add_attempt()

        # Полкучение email
        try:
            mail = get_user_mail(login)
            if mail == "None":
                raise LDAPMailNotFound

        except LDAPMailNotFound:
            await message.answer(MAIL_NOT_FOUND)
            await state.clear()
            return

        except LDAPUserNotFound:
            await message.answer(USER_NOT_FOUND,
                                 reply_markup=types.ReplyKeyboardRemove())
            logger.debug(f"Неудачная попытка ввода логина: {message.text}")

            # Подсчет оставшихся попыток
            remaining_attempts = auth_state.login_handler.remaining_attempts
            logger.debug(f"Осталось попыток {remaining_attempts}")
            await message.answer(f"Осталось попыток: {remaining_attempts}")

            # Выставление блокировки, если попытки закончились
            if remaining_attempts == 0:
                remaining_time = auth_state.login_handler.set_attempts_blocked_until()
                logger.debug(f"Выставлена блокировка на {remaining_time} секунд")
                await message.answer(f"Попробуйте через {remaining_time} секунд")

            return

        except LDAPError as e:
            logger.critical(f"Error: {e}")
            await message.answer(AUTHORIZATION_ERROR)
            await state.clear()
            return

        except Exception as e:
            logger.critical(f"Error: {e}")
            await message.answer(AUTHORIZATION_ERROR)
            await state.clear()
            return

        auth_state.mail = mail
        auth_state.login_handler.reset()
        auth_state.login = login

        # Вручную вызываем следующий обработчик
        await state.set_state(AuthStates.CODE)
        await process_code(message, state)


    @router.message(AuthStates.CODE, F.text)
    async def process_code(message: types.Message, state: FSMContext):
        auth_state = await get_auth_state(state)
        mail = auth_state.mail

        # Обработка возможности отправки кода
        remaining_blocked_time = auth_state.code_handler.get_blocked_request_time()
        if remaining_blocked_time != 0:
            await message.answer("Отправить код повторно возможно через"
                                 f"{remaining_blocked_time} секунд",
                                 reply_markup=auth_code_kb())
            return

        # Отправка кода
        try:
            code = await send_code(mail)
        except Exception:
            await message.answer("⚠️Не удалось отправить код подтверждения.\n"
                                 "Попробуйте позже или обратитесь в поддержку.")
            await state.clear()
            return

        auth_state.code = code
        auth_state.code_handler.last_request_time = datetime.now()

        await message.answer(
            f"Код подтверждения отправлен на <b>{mail}</b>\n."
            f"⏳ Код действителен в течение 5 минут\n"
            f"Введите его для завершения авторизации:",
            parse_mode="HTML", reply_markup=auth_code_kb()
        )
        await state.set_state(AuthStates.CODE_HANDLER)


    @router.message(AuthStates.CODE_HANDLER, F.text.func(lambda t: t.isdigit() and len(t) == 4))
    async def code_handler(message: types.Message, state: FSMContext):
        logger.debug(f"Переход в состояние CODE_HANDLER")
        auth_state = await get_auth_state(state)

        # Проверка не истекло ли время действия кода
        if not auth_state.is_code_valid():
            logger.debug("Время действия кода истекло")
            await message.answer("⌛️ Время действия кода истекло.\n"
                                 "Запросите новый код.",
                                 reply_markup=auth_code_kb())
            auth_state.code_handler.reset()
            return

        # Проверка на наличие блокировки
        if auth_state.code_handler.get_blocked_attempts_time() != 0:
            remaining = auth_state.code_handler.get_blocked_attempts_time()
            await message.answer(f"Превышено количество попыток."
                                 "Попробуйте через {remaining} секунд",
                                 reply_markup=auth_code_kb())
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


    @router.message(AuthStates.CODE_HANDLER, F.text)
    async def invalid_code_handler(message: types.Message, state: FSMContext):
        logger.debug(f"Обработка нестандартного ответа")
        """Обработка нестандартного сообщения на запрос кода"""
        match message.text:
            case "Изменить логин":
                await message.answer(
                    "Введите другой логин",
                    reply_markup=types.ReplyKeyboardRemove()
                )
                await state.set_state(AuthStates.LOGIN)

            case "Отправить код повторно":
                await process_code(message, state)

            case _:
                await message.answer("Код должен содержать только цифры,"
                                     f"длина кода должна быть равна {LENGTH_CODE}")


    @router.message(AuthStates.SUCCESS, F.text)
    async def success_handler(message: types.Message, state: FSMContext):
        auth_state = await get_auth_state(state)

        try:
            await db_service.save_user(
                telegram_id=message.from_user.id,
                login=auth_state.login
            )
            logger.info("Добавлен новый пользоватьель в базу данных"
                        f"tg_id: {message.from_user.id}"
                        f"login: {auth_state.login}")

        except Exception as e:
            logger.warning(f"Error: {e}")
            await message.answer("Ошибка при добавления пользователя",
                                 "попробуйте позже")
            await state.clear()
            return

        await message.answer("✅ Авторизация успешно завершена!"
                             "Теперь вы можете создать заявку",
                             reply_markup=main_kb())
        await state.clear()
        await state.set_state(BaseStates.complete_autorisation)

    return router
