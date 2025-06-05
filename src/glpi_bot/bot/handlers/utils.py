# bot/handlers/utils.py

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from functools import wraps
from typing import Callable, Optional, Awaitable, Any
import logging
import asyncio


logger = logging.getLogger(__name__)


async def flash_message(message: Message, text: str, delay: int = 3):
    """
    Отправляет временное сообщение пользователю и удаляет его через delay секунд.
    """
    flash = await message.answer(text)
    await asyncio.sleep(delay)
    try:
        await flash.delete()
    except Exception:
        pass  # Сообщение уже удалено или не может быть удалено


async def add_step(state: FSMContext, prompt: str, keyboard=None):
    logger.debug(f"Call add_step")
    navigation_data = (await state.get_data()).get("navigation_data", {"stack": []})
    stack = navigation_data.get("stack", [])

    current_data = ({
        "state": await state.get_state(),
        "message": prompt,
        "keyboard": keyboard.model_dump() if keyboard else None,
    })

    if stack and stack[-1] == current_data:
        logger.debug(f"Skip duplicate state")
        return

    stack.append(current_data)

    if len(stack) > 10:
        stack = stack[-10:]

    logger.debug(f"stack_states: {[step["state"] for step in stack]}")
    navigation_data["stack"] = stack
    await state.update_data(navigation_data=navigation_data)


async def default_handle(callback: CallbackQuery, state: FSMContext, prompt: str,
        keyboard: InlineKeyboardMarkup, next_state: Optional[State] = None):
    await add_step(state=state, prompt=prompt, keyboard=keyboard)
    if next_state:
        await state.set_state(next_state)
    await callback.message.edit_text(prompt, reply_markup=keyboard)
    await callback.answer()


def register_step(prompt: str, keyboard: Optional[InlineKeyboardMarkup] = None):
    def decorator(func: Callable[[Message, FSMContext], Awaitable[Any]]):
        @wraps(func)
        async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
            # Выполняем оригинальный хендлер
            result = await func(message, state, *args, **kwargs)

            # Добавляем в стек шаг после выполнения хендлера
            navigation_data = (await state.get_data()).get("navigation_data", {"stack": []})
            stack = navigation_data.get("stack", [])

            stack.append({
                "state": await state.get_state(),
                "message": prompt,
                "keyboard": keyboard.model_dump() if keyboard else None,
            })

            # Ограничиваем стек
            if len(stack) > 10:
                stack = stack[-10:]

            navigation_data["stack"] = stack
            await state.update_data(navigation_data=navigation_data)

            return result
        return wrapper
    return decorator
