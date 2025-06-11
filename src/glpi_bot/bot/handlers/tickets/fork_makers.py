# bot/handlers/tickets/fork_makers.py

import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.states import FlowStates, TicketStates
from aiogram.types import CallbackQuery
from glpi_bot.bot.handlers.utils import default_handle

from glpi_bot.bot.handlers.tickets.forks.req_1c import build_flow as build_flow_req_1c
from glpi_bot.bot.handlers.tickets.forks.inc_1c import build_flow as build_flow_inc_1c
from glpi_bot.bot.handlers.tickets.forks.req_it import build_flow as build_flow_req_it
from glpi_bot.bot.handlers.tickets.forks.inc_it import build_flow as build_flow_inc_it
from glpi_bot.bot.keyboards import base_buttons

logger = logging.getLogger(__name__)

req_1c_flow_collector = build_flow_req_1c(base_buttons=base_buttons)
inc_1c_flow_collector = build_flow_inc_1c(base_buttons=base_buttons)
req_it_flow_collector = build_flow_req_it(base_buttons=base_buttons)
inc_it_flow_collector = build_flow_inc_it(base_buttons=base_buttons)

router = Router()


# Инцидент 1с
@router.callback_query(F.data == "inc_1c", StateFilter(TicketStates.incident))
        # StateFilter(TicketStates.incident, FlowStates.inc_1c))
async def select_category_inc_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите объект вашей проблемы"
    keyboard = inc_1c_flow_collector.build_keyboard()
    await state.set_state(FlowStates.inc_1c)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.inc_1c))
async def callback_dispatcher_inc_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await inc_1c_flow_collector(callback, state)


# Инцидент IT
@router.callback_query(F.data == "inc_it", StateFilter(TicketStates.incident))
        # StateFilter(TicketStates.incident, FlowStates.inc_it))
async def select_category_inc_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите объект вашей проблемы"
    keyboard = inc_it_flow_collector.build_keyboard()
    await state.set_state(FlowStates.inc_it)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.inc_it))
async def callback_dispatcher_inc_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await inc_it_flow_collector(callback, state)


# Запрос 1c
@router.callback_query(F.data == "req_1c",
        StateFilter(TicketStates.type, FlowStates.req_1c))
async def select_category_req_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите направление запроса"
    keyboard = req_1c_flow_collector.build_keyboard()
    await state.set_state(FlowStates.req_1c)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.req_1c))
async def callback_dispatcher_req_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await req_1c_flow_collector(callback, state)


# Запрос IT
@router.callback_query(F.data == "req_it",
        StateFilter(TicketStates.type, FlowStates.req_it))
async def select_category_req_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите направление запроса"
    keyboard = req_it_flow_collector.build_keyboard()
    await state.set_state(FlowStates.req_it)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.req_it))
async def callback_dispatcher_req_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await req_it_flow_collector(callback, state)
