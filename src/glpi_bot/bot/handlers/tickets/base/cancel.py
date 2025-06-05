from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from glpi_bot.bot.states import BaseStates
from glpi_bot.bot.keyboards import main_kb
from glpi_bot.bot.handlers.tickets.base import router


logger = logging.getLogger(__name__)


@router.callback_query(F.data == "cancel")
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call cancel_creation")

    # Очистка состояния и истории
    await state.clear()
    await state.set_state(BaseStates.complete_autorisation)
    # await state.update_data(navigation_data={"stack": []})

    # Пытаемся удалить сообщение
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete message: {e}")

    # Отправляем уведомление
    await callback.message.answer(
        text="🚫 Создание заявки отменено",
        reply_markup=main_kb()
    )
    await callback.answer()
