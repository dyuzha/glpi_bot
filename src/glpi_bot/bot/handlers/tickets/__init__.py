from aiogram import Router
from .models import DynamicBotMessage

bot_message = DynamicBotMessage()

from .base import router as base_router
from .fork_makers import router as fork_makers_router
from .final import router as final_router
from .start_ticket import router as start_ticket_router

router = Router()

router.include_routers(
        final_router,
        fork_makers_router,
        start_ticket_router,
        base_router,
)
