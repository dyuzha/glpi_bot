from typing import Awaitable, Callable, Iterable, Optional

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from glpi_bot.bot.handlers.tickets.models.flow_collector import BaseFlowCollector
from glpi_bot.bot.handlers.tickets.models.steps.select_step import SelectInlineStep


class SelectAutoInlineStep(SelectInlineStep):

    def __init__(
            self,
            state: State,
            prompt: str,
            prefix: str,
            base_buttons: Optional[list[InlineKeyboardButton]] = None,
            before_callback: Optional[Callable[[CallbackQuery, FSMContext], Awaitable[None]]] = None,
            filters: Optional[Iterable[Callable]] = None,
            self_button_text: Optional[str] = None,
        ):
        self.flow_collector = BaseFlowCollector(prefix, base_buttons)

        super().__init__(filters=filters,
                         state=state,
                         prompt=prompt,
                         before_callback=before_callback,
                         self_button_text=self_button_text,
                         )


    def set_steps(self, steps: dict[str, SelectInlineStep]):
        self.steps = steps
        self._register_flow_collector()
        self.keyboard = self._build_keyboard()


    def register_handler(self, router: Router) -> None:
        super().register_handler(router)
        self.register_ext_handlers(router)


    def register_ext_handlers(self, router: Router) -> None:

        async def handler(callback: CallbackQuery, state: FSMContext):
            await self.flow_collector(callback, state)  # <- вызываем __call__ с await

        router.callback_query.register(
            handler,  # <- теперь передаём асинхронную функцию
            self.flow_collector._cb_factory.filter(),
            StateFilter(self.state),
        )


    def _build_keyboard(self) -> InlineKeyboardMarkup:
        return self.flow_collector.build_keyboard()


    def _register_flow_collector(self) -> None:
        if not hasattr(self, "steps"):
            raise ValueError("Метод set_steps() не был вызван: 'steps' не определён")

        def make_handler(step):
            async def handler(callback: CallbackQuery, state: FSMContext):
                await step(callback, state)
            return handler

        for text, step in self.steps.items():
            self.flow_collector.register(text, make_handler(step))

            # async def handler(callback: CallbackQuery, state: FSMContext):
            #     await step(callback, state)
            # self.flow_collector.register(text, handler)

