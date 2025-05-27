# form_handler.py

from aiogram import types
from aiogram.fsm.context import FSMContext
from steps import StepA, StepB, StepC
from glpi_bot.bot.handlers.ticket_handler.forms import Form


class FormHandler:
    def __init__(self, router):
        self.router = router
        self.form = Form([StepA(), StepB(), StepC()])
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_form, types.Message)
        self.router.message.register(self.process_input, types.Message)

    async def start_form(self, message: types.Message, state: FSMContext):
        await self.form.start(message, state)

    async def process_input(self, message: types.Message, state: FSMContext):
        await self.form.process_input(message, state)
