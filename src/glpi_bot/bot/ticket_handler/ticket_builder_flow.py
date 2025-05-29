# registration_flow.py

from typing import List, Optional
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.ticket_handler.steps import FormStep, DISABLE_KEY, COMPLETE_KEY, BACK_KEY, EDIT_KEY
import logging


logger = logging.getLogger(__name__)


class TicketBuilderFlow:
    def __init__(self, steps: List[FormStep]):
        self.steps = steps
        self.input_handler = InputHandler(self)
        self.edit_handler = EditHandler(self)


    async def start(self, message: Message, state: FSMContext):
        logger.debug(f"Переход в RegistrationFlow start")
        await self.input_handler.go_to_step(0, message, state)


    async def handle_input(self, message: Message, state: FSMContext):
        logger.debug(f"Переход в RegistrationFlow handle_input ")
        data = await state.get_data()
        index = data.get("step_index", 0)
        logger.debug(f"step_index saved: {index}")
        edit_mode = data.get("edit_mode", False)

        if edit_mode:
            await self.edit_handler.handle_edit(message, state, data)
        else:
            await self.input_handler.handle_step(message, state)


    async def confirm(self, message: Message, state: FSMContext, edit=False, message_id: Optional[int] = None):
        logger.debug(f"Переход в RegistrationFlow confirm")
        data = await state.get_data()
        summary = "\n".join(f"{step.show_key}: {data.get(step.key)}"
                            for step in self.steps)
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=EDIT_KEY, callback_data="edit")],
                [InlineKeyboardButton(text=COMPLETE_KEY, callback_data="confirm")],
            ]
        )

        if edit and message_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message_id,
                    text=f"Подтверждение данных:\n{summary}",
                    reply_markup=kb
                )
            except Exception as e:
                logger.error(f"Ошибка обновления symmary: {e}")
            return

        sent_msg = await message.answer(
            f"Подтверждение данных:\n{summary}", reply_markup=kb
        )
        await state.update_data(summary_message_id=sent_msg.message_id)


    async def show_edit_menu(self, message: Message):
        logger.debug(f"Переход в RegistrationFlow show_edit_menu")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [ InlineKeyboardButton(text=step.show_key, callback_data=f"edit:{step.key}")]
                for step in self.steps
            ]
        )
        await message.edit_reply_markup(reply_markup=kb)


class InputHandler:
    def __init__(self, flow: TicketBuilderFlow):
        self.flow = flow

    async def handle_step(self, message: Message, state: FSMContext):
        logger.debug(f"Переход в InputHandler handle_step")
        data = await state.get_data()
        index = data.get("step_index", 0)

        if message.text == BACK_KEY:
            await self.go_to_step(index - 1, message, state)
            return

        step = self.flow.steps[index]
        await step.handle_input(message, state)

        if index + 1 < len(self.flow.steps):
            await self.go_to_step(index + 1, message, state)
        else:
            await self.flow.confirm(message, state)

    async def go_to_step(self, index: int, message: Message, state: FSMContext):
        logger.debug(f"Переход в InputHandler go_to_step")
        await self._go_to_step(index, message, state)

    async def _go_to_step(self, index: int, message: Message, state: FSMContext):
        logger.debug(f"Переход в InputHandler _go_to_step")
        await state.update_data(step_index=index)
        step = self.flow.steps[index]
        await message.answer(step.prompt, reply_markup=step.kb())


class EditHandler:
    def __init__(self, flow: TicketBuilderFlow):
        self.flow = flow

    async def handle_edit(self, message: Message, state: FSMContext, data: dict):
        logger.debug(f"Переход в EditHandler handle_edit")
        data = await state.get_data()
        prompt_id = data.get("prompt_message_id")
        summary_id = data.get("summary_message_id")

        index = data.get("step_index", 0)
        step = self.flow.steps[index]
        await step.handle_input(message, state)

        # удаляем prompt
        if prompt_id:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=prompt_id
                )
                logger.debug(
                    f"Удаляем prompt_message_id: {prompt_id},"
                    f"user_message_id: {message.message_id}"
                )
            except Exception as e:
                logger.warning(f"Не удалось удалить prompt_message: {e}")

        # Удаляем пользовательское сообщение
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id
            )
            logger.debug(
                f"Удаляем prompt_message_id: {prompt_id}, user_message_id: {message.message_id}"
            )
        except Exception as e:
            logger.warning(f"Не удалось удалить user_message: {e}")

        await state.update_data(edit_mode=False)
        await self.flow.confirm(message, state, edit=True, message_id=summary_id)


