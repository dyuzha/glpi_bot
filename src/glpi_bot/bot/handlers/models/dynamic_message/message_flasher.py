# models/dynamic_message/message_flasher.py

from typing import TYPE_CHECKING, Optional
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

if TYPE_CHECKING:
    from .dynamic_bot_message import DynamicBotMessage


class MessageFlasher:
    def __init__(self, renderer: "DynamicBotMessage"):
        self.renderer = renderer

    async def flash(self, message: Message, state: FSMContext, prefix: str, *strings,
                    keyboard: Optional[InlineKeyboardMarkup] = None):

        custom_strings = [prefix + s for s in strings]

        return await self.renderer.update_message(message, state, *custom_strings,
                                           keyboard=keyboard)


    async def request(self, message: Message, state: FSMContext, *strings,
                      keyboard: Optional[InlineKeyboardMarkup] = None):
        return await self.flash(message, state, "💬 ", *strings, keyboard=keyboard)


    async def warning(self, message: Message, state: FSMContext, *strings,
                      keyboard: Optional[InlineKeyboardMarkup] = None):
        return await self.flash(message, state, "❗️ ", *strings, keyboard=keyboard)
