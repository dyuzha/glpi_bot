from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from glpi_bot.bot.ticket_handler.form_framework.step import FormStep
from typing import List
import logging


logger = logging.getLogger(__name__)


class TypeStep(FormStep):
    key = "type"
    show_key = "Тип заявки"
    prompt = "Выберите тип заявки"


    def get_custom_buttons(self) -> List[List[KeyboardButton]]:
        return [
            [KeyboardButton(text="Инцидент"), KeyboardButton(text="Запрос")]
        ]

    async def process_input(self, message: Message, state: FSMContext) -> bool:
        logger.debug(f"TypeStep call process_input")
        if message.text not in ["Инцидент", "Запрос"]:
            await message.answer("Пожалуйста, воспользуйтесь кнопками ниже.")
            return False

        await state.update_data(type=message.text)
        return True


class TitleStep(FormStep):
    key = "title"
    show_key = "Заголовок"
    prompt = "Напишите заголовок"

    async def process_input(self, message: Message, state: FSMContext):
        logger.debug(f"TitleStep call process_input")
        if len(str(message.text)) < 5:
            await message.answer("Заголовок слишком короткий.")
            return False

        await state.update_data(title=message.text)
        return True
