# form_framework/router.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from .flow import FormFlow


class FormRouter:
    def __init__(self, flow: FormFlow, state: State, command: str):
        self.flow = flow
        self.state = state
        self.command = command

    def register(self, router: Router):
        router.message(F.text, self._is_start_command)(self._start)
        router.message(self.state)(self._handle_input)
        # router.callback_query(self.state)(self._handle_callback)

    def _is_start_command(self, message: Message) -> bool:
        return message.text.startswith(f"/{self.command}")

    async def _start(self, message: Message, state: FSMContext):
        await self.flow.start(message, state)

    async def _handle_input(self, message: Message, state: FSMContext):
        await self.flow.handle_input(message, state)

    async def start_flow(self, message: Message, state: FSMContext):
        await state.set_state(self.state)
        await state.update_data(step_index=0)
        await self._start(message, state)

    # async def _handle_callback(self, call: CallbackQuery, state: FSMContext):
    #     await self.flow.handle_callback(call, state)
