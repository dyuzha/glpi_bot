from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from .step import FormStep
from typing import List


class FormKeyboardBuilder:
    def __init__(self, back_key: str, cancel_key: str):
        self.back_key = back_key
        self.cancel_key = cancel_key

    def build(self, step: FormStep) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=self.get_buttons_for_step(step),
            resize_keyboard=True,
            input_field_placeholder="Выберите или введите..."
        )

    def get_buttons_for_step(self, step: FormStep) -> List[List[KeyboardButton]]:
        # Кастомные кнопки от шага
        custom = step.get_custom_buttons()
        base = self.get_base_buttons(step)
        return custom + base

    def get_base_buttons(self, step: FormStep) -> List[List[KeyboardButton]]:
        buttons: List[List[KeyboardButton]] = []

        if step.optional:
            buttons.append([KeyboardButton(text=self.cancel_key)])

        buttons.append([KeyboardButton(text=self.back_key)])
        return buttons
