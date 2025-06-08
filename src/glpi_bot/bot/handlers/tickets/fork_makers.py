# bot/handlers/fork_makers.py

import logging
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from glpi_bot.bot.handlers.tickets import incident_1c_fork_maker
from glpi_bot.bot.handlers.tickets import inc_it_fork_maker
from glpi_bot.bot.handlers.tickets import request_1c_fork_maker
from glpi_bot.bot.handlers.tickets import request_it_fork_maker

from glpi_bot.bot.states import FlowStates, TicketStates
from aiogram.types import CallbackQuery
from glpi_bot.bot.handlers.utils import default_handle


logger = logging.getLogger(__name__)
router = Router()


# Инцидент 1с
@router.callback_query(F.data == "inc_1c",
        StateFilter(TicketStates.type, FlowStates.inc_1c))
async def select_category_inc_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите вашу проблему"
    keyboard = incident_1c_fork_maker.build_keyboard()
    await state.set_state(FlowStates.inc_1c)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.inc_1c))
async def callback_dispatcher_inc_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await incident_1c_fork_maker(callback, state)


# Инцидент IT
@router.callback_query(F.data == "inc_it",
        StateFilter(TicketStates.type, FlowStates.inc_it))
async def select_category_inc_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите вашу проблему"
    keyboard = inc_it_fork_maker.build_keyboard()
    await state.set_state(FlowStates.inc_it)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.inc_it))
async def callback_dispatcher_inc_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await inc_it_fork_maker(callback, state)


# Запрос 1c
@router.callback_query(F.data == "req_1c",
        StateFilter(TicketStates.type, FlowStates.req_1c))
async def select_category_req_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите вашу проблему"
    keyboard = request_1c_fork_maker.build_keyboard()
    await state.set_state(FlowStates.req_it)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.req_1c))
async def callback_dispatcher_req_1c(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await request_1c_fork_maker(callback, state)


# Запрос IT
@router.callback_query(F.data == "req_it",
        StateFilter(TicketStates.type, FlowStates.req_it))
async def select_category_req_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call select_category")

    prompt = "Выберите вашу проблему"
    keyboard = request_it_fork_maker.build_keyboard()
    await state.set_state(FlowStates.req_it)
    await default_handle(callback, state, prompt, keyboard)


@router.callback_query(~F.data.in_({"navigation_back", "cancel"}),  # исключаем назад и отмену
        StateFilter(FlowStates.req_it))
async def callback_dispatcher_req_it(callback: CallbackQuery, state: FSMContext):
    logger.debug("Call callback_dispatcher")
    await request_it_fork_maker(callback, state)
