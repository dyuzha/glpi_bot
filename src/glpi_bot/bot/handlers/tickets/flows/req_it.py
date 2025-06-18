# bot/handlers/tickets/forks/req_1c.py

import logging
from typing import Callable, Optional
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from glpi_bot.bot.handlers.tickets.models import BaseFlowCollector
from glpi_bot.bot.handlers.tickets.steps import description_step
from glpi_bot.bot.handlers.tickets.instances import bot_message


logger = logging.getLogger(__name__)


async def call_description(callback: CallbackQuery,
                           state: FSMContext,
                           category: str,
                           itilcategories_id: int,
                           prompt:str = "Подробно опишите проблему",
                        ):

    await state.update_data(itilcategories_id = itilcategories_id)
    await state.update_data(title = category)
    await bot_message.add_field(state, "Категория", category)

    if isinstance(callback.message, Message):
        await description_step(callback.message, state, prompt)
    await callback.answer()


def local_register(key_prompt: str,
                   itilcategories_id: int,
                   func: Optional[Callable]=None,
                   category: Optional[str]=None
                ):
    return (
            key_prompt, func or call_description,
            {
                "category": category or key_prompt,
                "itilcategories_id": itilcategories_id
            }
    )

puncts = [
        ["Добавление/удаление прав/доступов/пользователей", 20],
        ["Обслуживание орг техники, рабочих мест", 17],
        ["Установка/удаление ПО", 16],
        ["Диагностика рабочих мест", 60],
        ["Сопровождение ЭЦП", 60],
        ["Сопровождение сайтов", 1],
        ["Cопровождение видеонаблюдения", 2],
        ["Сопровождение телефонии", 73],
        ["Сопровождение электронной почты", 23],
         ]

args = [local_register(*punct) for punct in puncts]


def build_flow(base_buttons: list) -> BaseFlowCollector:
    flow_collector = BaseFlowCollector(prefix="req_it", base_buttons=base_buttons)
    flow_collector.register_many(args)
    return flow_collector
