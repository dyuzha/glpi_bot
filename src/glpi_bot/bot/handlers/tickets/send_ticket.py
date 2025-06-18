import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from glpi_bot.bot.handlers.tickets.instances import bot_message
from glpi_bot.bot.keyboards import main_kb
from glpi_bot.bot.states import BaseStates, FinalStates
from glpi_bot.services import GLPITicketManager
from glpi_bot.services.glpi_service import TicketData


logger = logging.getLogger(__name__)


def setup_send_ticket(glpi: GLPITicketManager):
    router = Router()

    @router.callback_query(F.data == "confirm", StateFilter(FinalStates.confirm))
    async def process_confirm(callback: CallbackQuery, state: FSMContext):
        logger.debug("Call process_confirm")

        try:
            d = await state.get_data()
        except Exception as e:
            logger.exception(f"Ошибка при получении состояния: {e}")
            await callback.answer("Произошла ошибка. Попробуйте сначала.")
            return

        ticket_data = TicketData(
                login = d['login'],
                # name = f"[{d['login']}] {d['title']}",
                name = d['title'],
                content = d['description'],
                type = d['type'],
                itilcategories_id = d['itilcategories_id']
        )
        try:
            # Создаем заявку в GLPI
            response = glpi.send_ticket(ticket_data)
            logger.debug(f"Создание заявки вернуло: {response}")

        except Exception as e:
            logger.error(f"Ошибка создания заявки: {e}")
            await callback.message.answer("Ошибка при создании заявки", reply_markup=main_kb())

        else:
            await bot_message.delete_message(callback.message, state)

            # await bot_message.update_message(
            #         callback.message, state,
            #         f"✅ Заявка успешно создана!\n\n"
            #         f"Ссылка: https://sd.it4prof.ru/front/ticket.form.php?id={response['id']}\n"
            #         f"<b>Номер:</b> #{response['id']}\n"
            #         f"<b>Заголовок:</b> {d['title']}\n"
            #         f"<b>Статус:</b> В обработке",
            #         keyboard=InlineKeyboardMarkup(inline_keyboard=[])
            #     )

        await state.clear()
        await state.set_state(BaseStates.complete_autorisation)
        await callback.answer()

        await callback.message.answer(
                text=(
                f"✅ Заявка успешно создана!\n\n"
                f"Ссылка: https://sd.it4prof.ru/front/ticket.form.php?id={response['id']}\n"
                f"<b>Номер:</b> #{response['id']}\n"
                f"<b>Заголовок:</b> {d['title']}\n"
                f"<b>Статус:</b> В обработке"),
                reply_markup=main_kb()
            )



        # await callback.message.answer(
        #         "Чтобы создать заявку: воспользуйтесь кнопками ниже 👇",
        #         reply_markup=main_kb()
        # )

    return router
