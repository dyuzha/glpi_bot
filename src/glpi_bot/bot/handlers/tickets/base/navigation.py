from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import logging

from glpi_bot.bot.handlers.tickets.base import router


logger = logging.getLogger(__name__)


@router.callback_query(F.data == "navigation_back")
async def back_handler(callback: CallbackQuery, state: FSMContext):
    logger.debug("Back button pressed")
    user_data = await state.get_data()
    navigation_data = user_data.get('navigation_data', {})

    stack = navigation_data.get('stack', [])

    if not navigation_data.get('stack'):
        await callback.answer("История пуста")
        return

    if len(stack) <= 1:
        await callback.answer("Это начальный экран")
        return

    # Удаляем текущее состояние из стека
    stack.pop()

    # Устанавливаем предыдущее состояние
    previous_state = stack[-1]
    await state.set_state(previous_state["state"])

    keyboard_data = previous_state.get("keyboard")
    keyboard = None
    # logger.debug(
            # f'previous: <state: {previous_state["state"]}>'
            # f"keyboard: {previous_state["keyboard"]}, "
            # f"message: {previous_state["message"]}>"
    # )

    if keyboard_data:
        try:
            keyboard = InlineKeyboardMarkup.model_validate(keyboard_data)
        except Exception:
            keyboard = None


    await callback.message.edit_text(
        previous_state['message'],
        reply_markup=keyboard
    )
    logger.debug(f"Back to: {previous_state['state']}")

    await state.update_data(navigation_data={"stack": stack})
    await callback.answer()
