# handler.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.ticket_handler.ticket_builder_flow import FormFlow
from glpi_bot.bot.ticket_handler.steps import TypeStep, CategoryStep
from glpi_bot.bot.states import TicketStates
import logging

logger = logging.getLogger(__name__)

router = Router()
ticket_builder = FormFlow([TypeStep(), CategoryStep()])

@router.message(Command("create_ticket"))
async def start_create_ticket(message: Message, state: FSMContext):
    logger.debug(f"Переход в start_create_ticket")
    await ticket_builder.start(message, state)



@router.message(TicketStates.create_ticket, F.text)
async def process_data_input(message: Message, state: FSMContext):
    logger.debug(f"Переход в process_data_input")
    await ticket_builder.handle_input(message, state)


@router.callback_query(TicketStates.create_ticket, F.data == "confirm")
async def confirm_data(call: CallbackQuery, state: FSMContext):
    logger.debug(f"Переход в process_registration_input")
    data = await state.get_data()

    summary = "\n".join(f"{step.show_key}: {data.get(step.key)}" for step in ticket_builder.steps)

    final_text = f"✅ Заявка сформирована. \n\n{summary}"

    try:
        await call.message.edit_text(final_text)
    except Exception as e:
        logger.error(f"Не удалось отредактировать сообщение")
        await call.message.answer(final_text)

    await state.clear()
    await call.answer()


@router.callback_query(TicketStates.create_ticket, F.data == "edit")
async def edit_menu(call: CallbackQuery):
    logger.debug(f"Переход в edit_menu")
    await ticket_builder.show_edit_menu(call.message)
    await call.answer()


@router.callback_query(TicketStates.create_ticket, F.data.startswith("edit:"))
async def handle_edit_step(call: CallbackQuery, state: FSMContext):
    step_key = call.data.split("edit:")[1]
    data = await state.get_data()

    # Находим нужный шаг
    step = next((s for s in ticket_builder.steps if s.key == step_key), None)
    if not step:
        await call.answer("Шаг не найден.")
        return

    # Сохраняем index редактируемого шага
    index = ticket_builder.steps.index(step)
    await state.update_data(step_index=index, edit_mode=True)

    current_value = data.get(step.key, "—")

   # сохраняем ID сообщения с prompt’ом
    prompt_msg = await call.message.answer(
        f"{step.prompt}\n\nТекущее значение: \n{current_value}",
        reply_markup=step.kb(),
    )

    await state.update_data(
        prompt_message_id=prompt_msg.message_id,
        summary_message_id=call.message.message_id
    )
    await call.answer()
