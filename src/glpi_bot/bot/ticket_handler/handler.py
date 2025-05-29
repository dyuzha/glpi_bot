# handler.py

from aiogram.dispatcher.router import Router
from glpi_bot.bot.states import TicketStates
from glpi_bot.bot.ticket_handler.form_framework.flow import FormFlow
from glpi_bot.bot.ticket_handler.form_framework.routers import FormRouter
from glpi_bot.bot.ticket_handler.steps import CategoryStep, TypeStep


flow = FormFlow(steps=[TypeStep(), CategoryStep()])
form_router = FormRouter(flow=flow, state=TicketStates.create_ticket, command="create_ticket")

router = Router()
form_router.register(router)
