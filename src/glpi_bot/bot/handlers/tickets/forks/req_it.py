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
        ["develop", "Добавление/удаление прав/доступов/пользователей", 20],
        ["2", "Обслуживание орг техники, рабочих мест", 17],
        ["3", "Установка/удаление ПО", 16],
        ["4", "Диагностика рабочих мест", 60],
        ["5", "Сопровождение ЭЦП", 60],
        ["6", "Сопровождение сайтов", 1],
        ["7", "Cопровождение видеонаблюдения", 2],
        ["8", "Сопровождение телефонии", 73],
        ["9", "Сопровождение электронной почты", 23],
         ]

args = [local_register(*punct) for punct in puncts]


def build_flow(base_buttons: list) -> BaseFlowCollector:
    flow_collector = BaseFlowCollector(base_buttons=base_buttons)
    flow_collector.register_many(args)
    return flow_collector
