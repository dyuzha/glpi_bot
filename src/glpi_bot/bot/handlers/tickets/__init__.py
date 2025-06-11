from aiogram import Router
from glpi_bot.bot.handlers.tickets.models import BaseFlowCollector
from glpi_bot.bot.keyboards import base_buttons

from . import instances

from .base import router as base_router
from .final import router as final_router
from .fork_makers import router as fork_makers_router
from .start_ticket import router as start_ticket_router

from .send_ticket import setup_send_ticket
from .forks import *

router = Router()

router.include_routers(
        final_router,
        fork_makers_router,
        start_ticket_router,
        base_router,
)
