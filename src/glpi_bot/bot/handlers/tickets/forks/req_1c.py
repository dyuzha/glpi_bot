# bot/handlers/tickets/forks/req_1c.py

import logging
from typing import Callable, Optional
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
        prompt:str = "Подробно опишите проблему",
    ):

    await state.update_data(itilcategories_id = itilcategories_id)
    await state.update_data(title = category)
    await bot_message.add_field(state, "Категория", category)

    await description_step(callback.message, state, prompt)
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
        ["develop", "Доработка/разработка (отчеты, формы...)", 42],
        ["2", "Сервисы (ЭДО, 1C отчетность...)", 42],
        ["3", "Оборудование (Кассы, весы, ТСД...)", 42],
        ["4", "Визуализация данных, списков, таблиц", 42],
        ["5", "Типовые решения (ЗУП, бухгалтерия...)", 42],
        ["6", "Экспорт/импорт данных", 42],
        ["7", "Обновление конфигурации", 42],
        ["8", "Покупка продуктов (лицензии, конфигурации...)", 42],
        ["9", "Добавление, удаление, восстановление баз и пользователей", 42],
        ["10", "Производительность", 42],
         ]

args = [local_register(*punct) for punct in puncts]

def build_flow(base_buttons: list) -> BaseFlowCollector:
    flow_collector = BaseFlowCollector(base_buttons=base_buttons)
    flow_collector.register_many(args)
    return flow_collector
