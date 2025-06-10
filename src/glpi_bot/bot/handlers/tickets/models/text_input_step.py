# bot/handlers/tickets/handlers/models/text_input_step.py

from typing import Awaitable, Callable, Optional
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
import logging

from glpi_bot.bot.handlers.tickets.models import DynamicBotMessage
from glpi_bot.bot.handlers.utils import add_step, default_handle
from glpi_bot.bot.keyboards import base_buttons


logger = logging.getLogger(__name__)



class TextInputStep:
    def __init__(
        self,
        state: State,
        prompt: str,
        bot_message: DynamicBotMessage,
        validate: Optional[Callable[[Message, FSMContext, DynamicBotMessage], Awaitable[bool]]] = None,
        final: Optional[Callable[[Message, FSMContext, DynamicBotMessage], Awaitable[None]]] = None,
    ):
        self.state = state
        self.prompt = prompt
        self.bot_message = bot_message
        self.validate = validate
        self.final = final


    async def show_after_callback(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        prompt: Optional[str] = None,
    ):
        await self._show(callback.message, state, prompt)
        await callback.answer()


    async def show_after_message(
        self,
        message: Message,
        state: FSMContext,
        prompt: Optional[str] = None,
    ):
        await self._show(message, state, prompt)


    async def _show(self, message: Message, state: FSMContext, prompt: Optional[str] = None):
        await state.set_state(self.state)

        edit_message = await self.bot_message.flasher.request(
            message, state, prompt or self.prompt
        )

        if edit_message is None:
            logger.warning("Не удалось отредактировать сообщение")
            # Можно, например, показать alert, если message от callback
            if hasattr(message, 'bot'):
                try:
                    await message.answer("Произошла ошибка при обновлении сообщения")
                except Exception:
                    pass
            return

        prompt = edit_message.text or ""
        keyboard = edit_message.reply_markup
        await add_step(state, prompt=prompt, keyboard=keyboard)


    # async def show_after_callback(
    #     self,
    #     callback: CallbackQuery,
    #     state: FSMContext,
    #     prompt: Optional[str] = None,
    # ):
    #     """Показ шага — задаёт состояние и показывает сообщение (после callback)."""
    #     await state.set_state(self.state)
    #
    #     edit_message = await self.bot_message.flasher.request(
    #         callback.message, state, prompt or self.prompt
    #     )
    #
    #     if edit_message is None:
    #         logger.warning("Не удалось отредактировать сообщение после callback")
    #         await callback.answer("Что-то пошло не так", show_alert=True)
    #         return
    #
    #     prompt = edit_message.text or ""
    #     keyboard = edit_message.reply_markup
    #     await add_step(state, prompt=prompt, keyboard=keyboard)
    #
    #     await callback.answer()
    #
    #
    # async def show_after_message(self,
    #                              message: Message,
    #                              state: FSMContext,
    #                              prompt: Optional[str] = None):
    #     """Показ шага — задаёт состояние и показывает сообщение."""
    #     await state.set_state(self.state)
    #
    #     edit_message = await self.bot_message.flasher.request(
    #             message, state, prompt or self.prompt
    #     )
    #
    #     if edit_message is None:
    #         logger.warning("Не удалось отредактирвоать сообщение")
    #         return
    #
    #     prompt = edit_message.text or ""
    #     keyboard = edit_message.reply_markup
    #     await add_step(state, prompt=prompt, keyboard=keyboard)


    async def __call__(self, message: Message, state: FSMContext):
        """
        Обработка ввода пользователя,
        возвращает True[False] при прохождении[не прохождении] валидации.
        """
        if self.validate:
            is_valid = await self.validate(message, state, self.bot_message)
            if not is_valid:
                return False
        else:
            is_valid = True

        if is_valid and self.final:
            logger.debug("Call final")
            await self.final(message, state, self.bot_message)
            logger.debug("Call final end")

        return True
