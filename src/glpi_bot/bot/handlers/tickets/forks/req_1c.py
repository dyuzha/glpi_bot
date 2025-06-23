# bot/handlers/tickets/forks/req_1c.py

import logging
from typing import Callable, Optional
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from glpi_bot.bot.handlers.models import BaseFlowCollector
from glpi_bot.bot.handlers.tickets.steps import description_step
from glpi_bot.bot.handlers.tickets.instances import bot_message


logger = logging.getLogger(__name__)


async def call_description(
        callback: CallbackQuery,
        state: FSMContext,
        category: str,
        itilcategories_id: int,
        prompt:str = "Опишите задачу подробнее",
    ):

    await state.update_data(itilcategories_id = itilcategories_id)
    await state.update_data(title = category)
    await bot_message.add_field(state, "Категория", category)

    if isinstance(callback.message, Message):
        await description_step.show(callback.message, state, prompt)

    await callback.answer()


def local_register(call_code: str, key_prompt: str,  itilcategories_id: int, func: Optional[Callable]=None, category: Optional[str]=None):
    return (
            call_code, key_prompt, func or call_description,
            {
                "category": category or key_prompt,
                "itilcategories_id": itilcategories_id
            }
    )

puncts = [
        ["develop", "Доработка/разработка (отчеты, формы...)", 40],
        ["2", "Сервисы (ЭДО, 1C отчетность...)", 76],
        ["3", "Оборудование (Кассы, весы, ТСД...)", 77],
        ["4", "Визуализация данных, списков, таблиц", 42],
        ["5", "Типовые решения (ЗУП, бухгалтерия...)", 79],
        ["6", "Экспорт/импорт данных", 56],
        ["7", "Обновление конфигурации", 31],
        ["8", "Покупка продуктов (лицензии, конфигурации...)", 81],
        ["9", "Добавление, удаление, восстановление баз и пользователей", 19],
        ["10", "Производительность", 80],
         ]

args = [local_register(*punct) for punct in puncts]


def build_flow(base_buttons: list) -> BaseFlowCollector:
    flow_collector = BaseFlowCollector(base_buttons=base_buttons)
    flow_collector.register_many(args)
    return flow_collector
