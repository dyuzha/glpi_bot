from aiogram import F
from aiogram.filters import Command
from bot.states import TicketCreation

from .tickets import (
    start_ticket_build,
    process_title,
    process_description,
    cancel_creation,
    start_ticket_creation
)
from .deffault import cmd_start

def register_ticket_handlers(dp):
    dp.message.register(start_ticket_build, F.text == "Начать составление заявки")
    dp.message.register(start_ticket_creation, F.text == "Создать заявку")
    dp.message.register(process_title, TicketCreation.waiting_for_title)
    dp.message.register(process_description, TicketCreation.waiting_for_description)
    dp.message.register(cancel_creation, Command("cancel"))
    dp.message.register(cancel_creation, F.text.lower() == "отмена")
    dp.message.register(cmd_start, Command("start"))
    # dp.message.register(go_back, Command("back"))
    # dp.message.register(handle_photo, F.photo)
