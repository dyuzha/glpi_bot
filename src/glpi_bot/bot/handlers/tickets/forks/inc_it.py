# bot/handlers/tickets/forks/inc_it.py

import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from glpi_bot.bot.handlers.tickets.models import BaseFlowCollector
from glpi_bot.bot.handlers.tickets.steps import description_step
from glpi_bot.bot.handlers.tickets.instances import bot_message


logger = logging.getLogger(__name__)

async def call_description(
        callback: CallbackQuery,
        state: FSMContext,
        category: str,
        itilcategories_id: int,
        prompt:str = "Опишите проблему подробнее",
    ):

    await state.update_data(itilcategories_id = itilcategories_id)
    await state.update_data(title = category)
    await bot_message.add_field(state, "Категория", category)

    await description_step.show(callback.message, state, prompt)
    await callback.answer()


async def mail_truble(callback: CallbackQuery, state: FSMContext):
    await call_description(callback, state, "Не работает почта", 23)


async def rdp_truble(callback: CallbackQuery, state: FSMContext):
    await call_description(callback, state, "Не работает удаленное подключение", 3)


# Дефолтные обаботчики
puncts = [
        # ("key", "button_text", func),
        # ("no_inet", "Интернета", inet_truble),
        ("invalid_mail", "Почта", mail_truble),
        ("rdp", "Удаленное подключение", rdp_truble),

        ("office", "Офисные программы", call_description, {
            "category": "Проблема при работе с офисными программами",
            "itilcategories_id": 15,
        }),

        ("peripheral", "Оборудование на рабочем месте", call_description, {
            "category": "Проблема c оборудованием на рабочем месте",
            "itilcategories_id": 17,
        }),

        ("print", "Принтер/сканер", call_description, {
            "category": "Проблема с принтером/сканером",
            "itilcategories_id": 17,
        }),

        ("resuerce", "Доступ к ресурсам", call_description, {
            "category": "Проблема c доступом к ресурсам",
            "itilcategories_id": 5,
        }),

        ("resuerce", "Производительность АРМ", call_description, {
            "category": "Проблема c производительностью АРМ",
            "itilcategories_id": 60,
        }),

        ("phone", "Телефония", call_description, {
            "category": "Проблема c телефонией",
            "itilcategories_id": 73,
        }),

        ("video", "Видеонаблюдение", call_description, {
            "category": "Проблема c видеонаблюдением",
            "itilcategories_id": 2,
        }),
    ]

def build_flow(base_buttons: list) -> BaseFlowCollector:
    flow_collector = BaseFlowCollector(base_buttons=base_buttons)

    @flow_collector.register_callback(name="no_inet", text="Нет интернета")
    async def inet_truble(callback: CallbackQuery, state: FSMContext):
        await call_description(callback, state, "Отсутствие интернета", 60)

    # Регистрация дефолтных обаботчиков
    flow_collector.register_many(puncts)

    return flow_collector
