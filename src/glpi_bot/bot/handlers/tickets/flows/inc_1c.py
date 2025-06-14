import logging
from typing import Callable, Optional
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

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

    if isinstance(callback.message, Message):
        await description_step(callback.message, state, prompt)

    await callback.answer()


def local_register(
                   key_prompt: str,
                   itilcategories_id: int,
                   func: Optional[Callable]=None,
                   category: Optional[str]=None):
    return (
            key_prompt, func or call_description,
            {
                "category": category or key_prompt,
                "itilcategories_id": itilcategories_id
            }
    )


puncts = [
        ["Ошибка лицензирования", 43],
        ["Ошибка обмена данных", 46],
        ["Ошибка запуска 1С", 42],
        ["Ошибка при проведении/записи документов", 44],
        ["Ошибка при формировании отчета", 45],
        ["Ошибка расчета данных", 48],
        ["Прочие ошибки 1С", 49],
         ]

args = [local_register(*punct) for punct in puncts]

def build_flow(base_buttons: list) -> BaseFlowCollector:
    flow_collector = BaseFlowCollector(prefix="inc_1c", base_buttons=base_buttons)
    flow_collector.register_many(args)
    return flow_collector
