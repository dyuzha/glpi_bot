# bot/handlers/tickets/forks/inc_it.py

import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from glpi_bot.bot.handlers.tickets.steps import title_step
from glpi_bot.bot.handlers.tickets.instances import bot_message, inc_it_fork_maker
from glpi_bot.bot.handlers.tickets.steps.title_step import title_step


logger = logging.getLogger(__name__)


async def call_title(
        callback: CallbackQuery,
        state: FSMContext,
        category: str,
        itilcategories_id: int,
        prompt:str = "Введите заголовок заявки\n(Краткое описание проблемы)",
    ):

    await state.update_data(itilcategories_id = itilcategories_id)
    await bot_message.add_field(state, "Категория", category)
    await title_step.show_after_callback(callback, state, prompt)


@inc_it_fork_maker.register_callback(name="no_inet", text="Нет интернета")
async def inet_truble(callback: CallbackQuery, state: FSMContext):
    await call_title(callback, state, "Отсутствие интернета", 60)


# @inc_it_fork_maker.register_callback(name="invalid_mail", text="Не работает почта")
async def mail_truble(callback: CallbackQuery, state: FSMContext):
    await call_title(callback, state, "Не работает почта", 23)


# @inc_it_fork_maker.register_callback(name="invalid_rdp", text="Не работает удаленка")
async def rdp_truble(callback: CallbackQuery, state: FSMContext):
    await call_title(callback, state, "Не работает удаленное подключение", 3)


# Регистрация дефолтных обаботчиков
inc_it_fork_maker.register_many(
    [
        # ("key", "button_text", func),
        # ("no_inet", "Интернета", inet_truble),
        ("invalid_mail", "Почта", mail_truble),
        ("rdp", "Удаленное подключение", rdp_truble),

        ("office", "Офисные программы", call_title, {
            "category": "Проблема при работе с офисными программами",
            "itilcategories_id": 15,
        }),

        ("peripheral", "Оборудование на рабочем месте", call_title, {
            "category": "Проблема c оборудованием на рабочем месте",
            "itilcategories_id": 17,
        }),

        ("print", "Принтер/сканер", call_title, {
            "category": "Проблема с принтером/сканером",
            "itilcategories_id": 17,
        }),

        ("resuerce", "Доступ к ресурсам", call_title, {
            "category": "Проблема c доступом к ресурсам",
            "itilcategories_id": 5,
        }),

        ("resuerce", "Производительность АРМ", call_title, {
            "category": "Проблема c производительностью АРМ",
            "itilcategories_id": 60,
        }),

        ("phone", "Телефония", call_title, {
            "category": "Проблема c телефонией",
            "itilcategories_id": 73,
        }),

        ("video", "Видеонаблюдение", call_title, {
            "category": "Проблема c видеонаблюдением",
            "itilcategories_id": 2,
        }),
    ],
)
