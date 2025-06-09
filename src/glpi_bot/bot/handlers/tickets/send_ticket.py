import logging
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from glpi_bot.bot.handlers.tickets.models.dinamic_bod_message import DynamicBotMessage
from glpi_bot.bot.keyboards import main_kb
from glpi_bot.bot.states import BaseStates, FinalStates
from glpi_bot.services import GLPITicketManager
from glpi_bot.services.glpi_service2_0 import TicketData


logger = logging.getLogger(__name__)
bot_message = DynamicBotMessage()


def setup_send_ticket(glpi: GLPITicketManager):
    router = Router()

    @router.callback_query(F.data == "confirm", StateFilter(FinalStates.confirm))
    async def process_confirm(callback: CallbackQuery, state: FSMContext):
        state_data = await state.get_data()
        ticket_data = TicketData(
                login = state_data["login"],
                name = state_data["title"],
                content = state_data["description"],
                type = state_data["type"],
                itilcategories_id = state_data["itilcategories_id"]
        )
        try:
            # Создаем заявку в GLPI
            response = glpi.send_ticket(ticket_data)
            logger.debug(f"Создание заявки вернуло: {response}")

        except Exception as e:
            logger.error(f"Ошибка создания заявки: {e}")
            await callback.message.answer("Ошибка при создании заявки", reply_markup=main_kb())

        else:
            logger.debug("Call process_confirm")
            await bot_message.update_message(callback.message, state,
                f"✅ Заявка успешно создана!\n\n"
                f"<b>Номер:</b> #{response['id']}\n"
                f"<b>Заголовок:</b> {state_data['title']}\n"
                f"<b>Статус:</b> В обработке",
                keyboard=InlineKeyboardMarkup(inline_keyboard=[])
            )
        # await bot_message.update_message(callback.message, state,
        #         "✅ Заявка успешно отправлена!",
        #         keyboard=InlineKeyboardMarkup(inline_keyboard=[])
        # )

        await state.clear()
        await state.set_state(BaseStates.complete_autorisation)
        await callback.answer()
        await callback.message.answer(
                "Чтобы создать заявку: воспользуйтесь кнопками ниже 👇",
                reply_markup=main_kb()
        )

    return router
