
from typing import Callable, Optional
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardMarkup, Message

from glpi_bot.bot.handlers.utils import add_step


class ConfirmStep:
    def __init__(self, state: State, prompt: str, keyboard: InlineKeyboardMarkup):
        self.state = state
        self.prompt = prompt
        self.keyboard = keyboard

    async def show(self,
        prompt: Optional[str] = None,
        keyboard: Optional[InlineKeyboardMarkup] = None):

        prompt = prompt or self.prompt
        keyboard = keyboard or self.keyboard

        await add_step(self.state, prompt=prompt, keyboard=keyboard)
