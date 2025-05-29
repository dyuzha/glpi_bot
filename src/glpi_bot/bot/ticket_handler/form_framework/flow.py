# form_framework/flow.py
from typing import List, Optional, Callable, Awaitable, Protocol
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from .step import FormStep

Handler = Callable[[CallbackQuery, FSMContext], Awaitable[None]]

class CallbackHandlerRegistry:
    def __init__(self):
        self._handlers: dict[str, Handler] = {}

    def register(self, key: str, handler: Handler):
        self._handlers[key] = handler

    def get(self, key: str) -> Handler | None:
        return self._handlers.get(key)

    def all(self) -> dict[str, Handler]:
        return self._handlers


class KeyboardBuilder(Protocol):
    def build_keyboard(self, step: FormStep) -> ReplyKeyboardMarkup | InlineKeyboardMarkup: ...


class InputKeyboardBuilder:
    def __init__(self, back_key: str, cancel_key: str):
        self.back_key = back_key
        self.cancel_key = cancel_key

    def build_keyboard(self, step: FormStep) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=self.get_buttons(step),
            resize_keyboard=True,
            input_field_placeholder="Выберите или введите..."
        )

    def get_buttons(self, step: FormStep) -> list[list[KeyboardButton]]:
        buttons = step.get_custom_buttons()
        if step.optional:
            buttons.append([KeyboardButton(text=self.cancel_key)])
        buttons.append([KeyboardButton(text=self.back_key)])
        return buttons


class EditKeyboardBuilder:
    def __init__(self, back_key: str, complete_key: str):
        self.back_key = back_key
        self.complete_key = complete_key

    def build_keyboard(self, step: FormStep) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=self.back_key, callback_data=self.back_key)],
                [InlineKeyboardButton(text=self.complete_key, callback_data=self.complete_key)],
            ]
        )


class FormModeHandler(Protocol):
    async def go_to_step(self, index: int, message: Message, state: FSMContext): ...
    async def handle_input(self, message: Message, state: FSMContext): ...


class InputModeHandler:
    def __init__(self, steps: List[FormStep], keyboard_builder: InputKeyboardBuilder):
        self.steps = steps
        self.kb = keyboard_builder

    async def go_to_step(self, index: int, message: Message, state: FSMContext):
        step = self.steps[index]
        await state.update_data(step_index=index)
        await message.answer(step.prompt, reply_markup=self.kb.build_keyboard(step))

    async def handle_input(self, message: Message, state: FSMContext):
        data = await state.get_data()
        index = data.get("step_index", 0)
        step = self.steps[index]

        if await step.process_input(message, state):
            if index + 1 < len(self.steps):
                await state.update_data(step_index=index + 1)
                await self.go_to_step(index + 1, message, state)
            else:
                await FormFlow.show_summary_static(self.steps, message, state)


class EditModeHandler:
    def __init__(self, steps: List[FormStep], keyboard_builder: EditKeyboardBuilder):
        self.steps = steps
        self.kb = keyboard_builder

    async def go_to_step(self, index: int, message: Message, state: FSMContext):
        step = self.steps[index]
        await state.update_data(step_index=index)
        await message.answer(step.prompt, reply_markup=self.kb.build_keyboard(step))

    async def handle_input(self, message: Message, state: FSMContext):
        await message.answer("Вы находитесь в режиме редактирования. Нажмите кнопку.")


class FormFlow:
    back_key = "🔙 Назад"
    cancel_key = "🚫 Пропустить"
    complete_key = "✅ Завершить"
    edit_key = "✏️ Изменить"

    def __init__(self, steps: List[FormStep]):
        self.steps = steps
        self.input_handler = InputModeHandler(steps, InputKeyboardBuilder(self.back_key, self.cancel_key))
        self.edit_handler = EditModeHandler(steps, EditKeyboardBuilder(self.back_key, self.complete_key))
        self.callbacks = CallbackHandlerRegistry()
        self._register_default_callbacks()

    def _register_default_callbacks(self):
        self.callbacks.register(self.back_key, self.handle_back)
        self.callbacks.register(self.cancel_key, self.handle_cancel)
        self.callbacks.register(self.edit_key, self.handle_edit)
        self.callbacks.register(self.complete_key, self.handle_confirm)

    def get_mode_handler(self, data: dict) -> FormModeHandler:
        return self.edit_handler if data.get("edit_mode") else self.input_handler

    async def start(self, message: Message, state: FSMContext):
        await state.set_data({"step_index": 0, "edit_mode": False})
        await self.input_handler.go_to_step(0, message, state)

    async def handle_input(self, message: Message, state: FSMContext):
        data = await state.get_data()
        handler = self.get_mode_handler(data)
        await handler.handle_input(message, state)

    async def _go_to_step(self, index: int, message: Message, state: FSMContext):
        data = await state.get_data()
        handler = self.get_mode_handler(data)
        await handler.go_to_step(index, message, state)

    async def handle_callback_query(self, call: CallbackQuery, state: FSMContext):
        data = call.data
        handler = self.callbacks.get(data)

        if handler:
            return await handler(call, state)

        index = (await state.get_data()).get("step_index", 0)
        step = self.steps[index]

        if hasattr(step, "handle_callback"):
            return await step.handle_callback(call, state)

        return await call.answer("Нераспознанное действие")

    async def handle_back(self, call: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        index = max(0, data.get("step_index", 0) - 1)
        await self._go_to_step(index, call.message, state)
        await call.answer()

    async def handle_cancel(self, call: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        index = data.get("step_index", 0)
        key = self.steps[index].key
        await state.update_data({key: None})
        await self.handle_back(call, state)

    async def handle_edit(self, call: CallbackQuery, state: FSMContext):
        await state.update_data(edit_mode=True)
        await self._go_to_step((await state.get_data()).get("step_index", 0), call.message, state)
        await call.answer()

    async def handle_confirm(self, call: CallbackQuery, state: FSMContext):
        await call.message.answer("✅ Подтверждено.")
        await state.clear()
        await call.answer()

    async def show_summary(self, message: Message, state: FSMContext):
        await self.show_summary_static(self.steps, message, state)

    @staticmethod
    async def show_summary_static(steps: List[FormStep], message: Message, state: FSMContext):
        data = await state.get_data()
        text = "📋 Введённые данные:\n\n"
        for step in steps:
            val = data.get(step.key, "—")
            text += f"{step.show_key}: {val}\n"
        await message.answer(text)
