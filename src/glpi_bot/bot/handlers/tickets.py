import logging
from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from glpi_bot.services import glpi_service
from glpi_bot.bot.keyboards import main_kb, back_kb, confirm_kb, type_kb
from glpi_bot.bot import dp
from glpi_bot.bot.states import TicketCreation, BaseStates


logger = logging.getLogger(__name__)


DISABLE_KEY = "❌ Отмена"
COMPLETE_KEY = "✅ Подтвердить"
BACK_KEY = "🔙 Назад"

SELECT_WILL_TYPE_TICKET = (
    "Выберите тип заявки:\n\n"
    "🐛 <b>Инцидент</b> — если что-то сломалось\n"
    "📋 <b>Запрос</b> — если вам что-то нужно"
)
INPUT_WILL_HEAD = (
    "📝 Введите краткий заголовок заявки "
    "(например: 'Проблема с принтером'):"
    )

INPUT_WILL_DISCRIPTION = (
    "✏️ Теперь подробно опишите проблему:\n\n"
    "• Что произошло?\n"
    "• Когда возникла проблема?\n"
    "• Укажите имя ПК, с которым связана проблема\n"
    "• Какие ошибки видите?\n\n"
    "  Напишите данные, которые могли бы помочь быстрее решить проблему:\n\n"
    "• Укажите имя ПК, с которым связана проблема\n"
    "• Если проблема связана с оборудование, напишите его модель"
)
INPUT_WILL_REPEAT_DESCRIPTION = "Редактируем описание. Введите новый текст:"

CHANGE_WILL_TYPE_TICKET = "Пожалуйста, выберите тип заявки кнопками ниже:"

RETURN_TO_MAIN_MENU = "Вы вернулись в главное меню"
CHANGE_TYPE_TICKET = "Вы вернулись к выбору типа заявки"

INVALID_HEADER = (
    "❌ Заголовок должен содержать минимум 5 символов. "
    "Попробуйте еще раз:"
)
INVALID_DISCRIPTION = (
    "❌ Описание должно содержать минимум 10 символов. "
    "Пожалуйста, опишите подробнее:"
)
ERROR_CREATE_TICKET = (
    "❌ Произошла ошибка при создании заявки. "
    "Пожалуйста, попробуйте позже."
)

@dp.message(F.text == "Создать заявку", BaseStates.COMPLETE_AUTORISATION)
async def start_ticket_creation(message: types.Message, state: FSMContext):
    """Выбрать Инцидент/Запрос"""
    logger.debug(f"Переход в главное меню")
    data = await state.get_data()
    logger.debug(f"Данные в кеше: {data}")
    await message.answer(
        SELECT_WILL_TYPE_TICKET,
        reply_markup=type_kb()
    )
    await state.set_state(TicketCreation.waiting_for_type)


@dp.message(TicketCreation.waiting_for_type)
async def start_ticket_build(message: types.Message, state: FSMContext):
    """Обработка выбора типа заявки и переход к вводу заголовка"""
    logger.debug("Переход к выбору типа заявки")

    # Сделать match/case
    if message.text == BACK_KEY:
        await message.answer(RETURN_TO_MAIN_MENU, reply_markup=main_kb())
        await state.clear()
        return

    if message.text == DISABLE_KEY:
        await cancel_creation(message, state)
        return

    # Определяем тип заявки
    type_ticket = None
    if message.text == "Инцидент":
        logger.debug("Выбран пункт Инцидент")
        type_ticket = 1
    elif message.text == "Запрос":
        logger.debug("Выбран пункт Запрос")
        type_ticket = 2
    else:
        await message.answer(CHANGE_WILL_TYPE_TICKET)
        logger.debug(f"Некорректный ввод: {message.text}")
        return

    # Сохраняем тип заявки в состоянии
    await state.update_data(type=type_ticket)
    logger.debug(f"Тип заявки сохранен в состоянии {type_ticket}")
    await message.answer(
        INPUT_WILL_HEAD,
        reply_markup=back_kb()
    )
    await state.set_state(TicketCreation.waiting_for_title)


@dp.message(TicketCreation.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    """Обработка заголовка и запрос описания"""
    logger.debug("Переход созданию заголовка")

    if message.text == BACK_KEY:
        await message.answer(
            CHANGE_TYPE_TICKET,
            reply_markup=type_kb()
        )
        logger.debug("Переход на шаг назад (Выбор типа заявки)")
        await state.clear()
        return

    if message.text == DISABLE_KEY:
        await cancel_creation(message, state)
        return

    if len(str(message.text)) < 5:
        logger.debug(f"Некорректный ввод {message.text}")
        await message.answer(INVALID_HEADER)
        return

    await state.update_data(title=message.text)
    logger.debug(f"Заголовок заявки сохранен в состоянии {message.text}")
    await message.answer(INPUT_WILL_DISCRIPTION, reply_markup=back_kb())
    await state.set_state(TicketCreation.waiting_for_description)


@dp.message(TicketCreation.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    """Обработка описания и создание заявки в GLPI"""
    logger.debug("Переход созданию описания")

    if message.text == BACK_KEY:
        data = await state.get_data()
        logger.debug("Переход на шаг назад (Составление описания)")
        await message.answer(
            f"Редактируем заголовок.\nТекущий: {data['title']}\n"
            "Введите новый заголовок:",
            reply_markup=back_kb()
        )
        await state.set_state(TicketCreation.waiting_for_title)
        return

    if message.text == DISABLE_KEY:
        await cancel_creation(message, state)
        return

    if len(str(message.text)) < 10:
        await message.answer(INVALID_DISCRIPTION)
        logger.debug(f"Некорректный ввод {message.text}")
        return

    # Сохраняем данные в кеш
    await state.update_data(description=message.text)
    logger.debug(f"Описание заявки сохранено в состоянии {message.text}")
    # Забираем данные в виде словаря
    data = await state.get_data()


    await message.answer(
        "📋 Проверьте данные заявки:\n\n"
        f"<b>Заголовок:</b> {data['title']}\n"
        f"<b>Описание:</b>\n{data['description']}\n\n"
        "Всё верно?",
        reply_markup=confirm_kb()
    )
    await state.set_state(TicketCreation.confirm_data)


# Обработка подтверждения
@dp.message(TicketCreation.confirm_data)
async def confirm_ticket(message: types.Message, state: FSMContext):
    """Обработка подтверждения"""
    logger.debug("Переход обработке подтверждения")

    if message.text == BACK_KEY:
        logger.debug("Переход на шаг назад (Составление описания)")
        await message.answer(
            INPUT_WILL_REPEAT_DESCRIPTION,
            reply_markup=back_kb()
        )
        await state.set_state(TicketCreation.waiting_for_description)
        return

    if message.text == DISABLE_KEY:
        await cancel_creation(message, state)
        return

    if message.text == COMPLETE_KEY:
        data = await state.get_data()
        logger.debug(f"Получение всей информации: {data}")

        ticket_data = {
                "login": data["login"],
                "name": data['title'],
                "content": data['description'],
                "type": data['type'], # 1 для инцидента, 2 для запроса
                # "urgency": 3, # Срочность (1-5)
                # "impact": 3, # Влияние (1-5)
                # "priority": 3, # Приоритет (1-5)
                # "requesttypes_id": 1, # Источник запроса
                "itilcategories_id": 1, # ID Категории,
                # "_users_id_requester": 291, # ID пользователя-заявителя
                # "entities_id": 10  # ID организации (0 для корневой)
            }

        logger.debug(f"Составление запроса: {ticket_data}")

        try:
            # Создаем заявку в GLPI
            glpi_service.set_data(**ticket_data)
            response = glpi_service.send_ticket()
            logger.debug(f"Создание заявки вернуло: {response}")

        except Exception as e:
            logger.error(f"Ошибка создания заявки: {e}")
            await message.answer(ERROR_CREATE_TICKET, reply_markup=main_kb())

        else:
            await message.answer(
                f"✅ Заявка успешно создана!\n\n"
                f"<b>Номер:</b> #{response['id']}\n"
                f"<b>Заголовок:</b> {data['title']}\n"
                f"<b>Статус:</b> В обработке",
                reply_markup=main_kb()
            )

        finally:
            await state.clear()
            logger.debug(f"Обнуление состояния")
    else:
        logger.debug(f"Некорректный ввод f{message.text}")
        await message.answer("Пожалуйста, используйте кнопки ниже")


# @dp.message(Command("back"))
# @dp.message(F.text.lower() == BACK_KEY)
# async def go_back(message: types.Message, state: FSMContext):
#     """Переход на шаг назад"""
#     pass


@dp.message(Command("cancel"))
@dp.message(F.text.lower() == DISABLE_KEY)
async def cancel_creation(message: types.Message, state: FSMContext):
    """Отмена создания заявки"""
    await state.clear()
    logger.debug("Создание заявки отменено")
    await message.answer(
        "🚫 Создание заявки отменено",
        reply_markup=main_kb()
    )


# @dp.message(F.photo)
# async def handle_photo(message: types.Message, state: FSMContext):
#     photo_id = message.photo[-1].file_id
#     await state.update_data(photo_id=photo_id)
