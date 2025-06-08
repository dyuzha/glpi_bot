from aiogram import Router
from .models import DynamicBotMessage
from glpi_bot.bot.handlers.tickets.models import BaseForkMaker
from glpi_bot.bot.keyboards import base_buttons

from .base import router as base_router
from .final import router as final_router
from .fork_makers import router as fork_makers_router
from .start_ticket import router as start_ticket_router
from .forks import *

bot_message = DynamicBotMessage()
incident_1c_fork_maker = BaseForkMaker(base_buttons=base_buttons)
inc_it_fork_maker = BaseForkMaker(base_buttons=base_buttons)
request_it_fork_maker = BaseForkMaker(base_buttons=base_buttons)
request_1c_fork_maker = BaseForkMaker(base_buttons=base_buttons)

from .forks import inc_1c  # <--- это запускает модуль с регистрацией
from .forks import inc_it  # <--- это запускает модуль с регистрацией
# from .forks import req_1c  # <--- это запускает модуль с регистрацией
# from .forks import req_it  # <--- это запускает модуль с регистрацией

router = Router()

router.include_routers(
        final_router,
        fork_makers_router,
        start_ticket_router,
        base_router,
)


bot_message = DynamicBotMessage()
incident_1c_fork_maker = BaseForkMaker(base_buttons=base_buttons)


router = Router()

router.include_routers(
        # final_router,
        fork_makers_router,
        start_ticket_router,
        base_router,
)
