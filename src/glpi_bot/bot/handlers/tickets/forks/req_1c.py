# bot/handlers/tickets/forks/req_1c.py

import logging
from typing import Callable, Optional
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from glpi_bot.bot.handlers.tickets.steps import title_step
from glpi_bot.bot.handlers.tickets.instances import bot_message, req_1c_fork_maker
from glpi_bot.bot.handlers.tickets.steps.title_step import title_step


logger = logging.getLogger(__name__)


async def call_description(
        callback: CallbackQuery,
        state: FSMContext,
        category: str,
        itilcategories_id: int,
        prompt:str = "Введите заголовок заявки\n(Краткое описание проблемы)",
    ):

    await state.update_data(itilcategories_id = itilcategories_id)
    await state.update_data(name = category)
    await bot_message.add_field(state, "Категория", category)
    await title_step.show_after_callback(callback, state, prompt)


def local_register(call_code: str, key_prompt: str,  itilcategories_id: int, func: Optional[Callable]=None, category: Optional[str]=None):
    if func is None:
        func = call_description

    if category is None:
        category = key_prompt

    # return (
    #         call_code, key_prompt, func or call_description,
    #         {
    #             "category": category or key_prompt,
    #             "itilcategories_id": itilcategories_id
    #         }
    # )
    return (
            call_code, key_prompt, func,
            {
                "category": category,
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

rl = [local_register(*punct) for punct in puncts]

req_1c_fork_maker.register_many(rl)
