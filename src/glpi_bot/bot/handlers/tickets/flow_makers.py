# bot/handlers/tickets/flow_makers.py

from aiogram import F, Router
from aiogram.filters import StateFilter
import logging

from glpi_bot.bot.handlers.tickets.models.steps.flow_maker import FlowMaker
from glpi_bot.bot.states import FlowStates, TicketStates
from glpi_bot.bot.keyboards import base_buttons

from glpi_bot.bot.handlers.tickets.flows import (build_flow_req_1c,
                                                 build_flow_inc_1c,
                                                 build_flow_req_it,
                                                 build_flow_inc_it,)


logger = logging.getLogger(__name__)
router = Router()


FlowMaker(
        filters=(F.data == "inc_1c", StateFilter(TicketStates.incident)),
        next_state=FlowStates.inc_1c,
        prompt = "Выберите объект вашей проблемы",
        flow_collector = build_flow_inc_1c(base_buttons=base_buttons)
).register_handler(router)


FlowMaker(
        filters=(F.data == "inc_it", StateFilter(TicketStates.incident)),
        next_state=FlowStates.inc_it,
        prompt = "Выберите объект вашей проблемы",
        flow_collector = build_flow_inc_it(base_buttons=base_buttons)
).register_handler(router)


FlowMaker(
        filters=(F.data == "req_1c", StateFilter(TicketStates.request)),
        next_state=FlowStates.req_1c,
        prompt = "Выберите направление запроса",
        flow_collector = build_flow_req_1c(base_buttons=base_buttons)
).register_handler(router)


FlowMaker(
        filters=(F.data == "req_it", StateFilter(TicketStates.request)),
        next_state=FlowStates.req_it,
        prompt = "Выберите направление запроса",
        flow_collector = build_flow_req_it(base_buttons=base_buttons)
).register_handler(router)














# inc_1c_flow_collector = build_flow_inc_1c(base_buttons=base_buttons)
# SelectInlineStep(
#         filters=(F.data == "inc_1c", StateFilter(TicketStates.incident)),
#         next_state=FlowStates.inc_1c,
#         prompt = "Выберите объект вашей проблемы",
#         keyboard=inc_1c_flow_collector.build_keyboard(),
# ).register_handler(router)
#
# @router.callback_query(inc_1c_flow_collector._cb_factory.filter(), StateFilter(FlowStates.inc_1c))
# async def callback_dispatcher_inc_1c(callback: CallbackQuery, state: FSMContext):
#     logger.debug("Call callback_dispatcher")
#     await inc_1c_flow_collector(callback, state)


# Инцидент 1с
# @router.callback_query(F.data == "inc_1c", StateFilter(TicketStates.incident))
# async def select_category_inc_1c(callback: CallbackQuery, state: FSMContext):
#     logger.debug("Call select_category")
#     await state.set_state(FlowStates.inc_1c)
#
#     prompt = "Выберите объект вашей проблемы"
#     keyboard = inc_1c_flow_collector.build_keyboard()
#
#     await add_step(state=state, prompt=prompt, keyboard=keyboard)
#     if isinstance(callback.message, Message):
#         await callback.message.edit_text(prompt, reply_markup=keyboard)
#     await callback.answer()

#
# @router.callback_query(inc_1c_flow_collector._cb_factory.filter(), StateFilter(FlowStates.inc_1c))
# async def callback_dispatcher_inc_1c(callback: CallbackQuery, state: FSMContext):
#     logger.debug("Call callback_dispatcher")
#     await inc_1c_flow_collector(callback, state)
