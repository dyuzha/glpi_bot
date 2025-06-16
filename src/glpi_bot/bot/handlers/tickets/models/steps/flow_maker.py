from typing import Awaitable, Callable, Iterable, Optional
from aiogram import Router, F
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import logging

from glpi_bot.bot.handlers.tickets.models import BaseFlowCollector
from glpi_bot.bot.handlers.tickets.models.steps.select_step import SelectInlineStep
from glpi_bot.bot.handlers.utils import default_handle


logger = logging.getLogger(__name__)


class FlowMaker(SelectInlineStep):
    def __init__(
            self,
            filters: Iterable[Callable],
            next_state: State,
            prompt: str,
            flow_collector: BaseFlowCollector,
            before_callback: Optional[Callable[[CallbackQuery, FSMContext], Awaitable[None]]] = None,

        ):
        self.flow_collector = flow_collector
        super().__init__(filters=filters,
                         state=next_state,
                         prompt=prompt,
                         keyboard=self.flow_collector.build_keyboard(),
                         before_callback=before_callback)


    # def register_ext_handlers(self, router: Router) -> None:
    #     router.callback_query.register(
    #         self.flow_collector,
    #         self.flow_collector._cb_factory.filter(),
    #         StateFilter(self.next_state),
    #     )

    def register_ext_handlers(self, router: Router) -> None:
        async def handler(callback: CallbackQuery, state: FSMContext):
            await self.flow_collector(callback, state)  # <- вызываем __call__ с await

        router.callback_query.register(
            handler,  # <- теперь передаём асинхронную функцию
            self.flow_collector.cb_factory.filter(),
            StateFilter(self.state),
        )


    def register_handler(self, router: Router) -> None:
        super().register_handler(router)
        self.register_ext_handlers(router)
