from aiogram import F
from aiogram.filters import Command
from bot.states import TicketCreation, Authorization, Base


from .deffault import (
    cmd_start

)
from .tickets import (
    start_ticket_build,
    process_title,
    process_description,
    cancel_creation,
    start_ticket_creation
)
from .authorization import (
    handle_login,
    handle_code,
)

# Инициализация
def initialisation_handlers(dp):

# Авторизация
def authorization_handlers(dp):
    dp.message.register(authorization, Base.waiting_authorization)
    dp.message.register(handle_login, Authorization.waiting_for_login)
    dp.message.register(handle_code, Authorization.waiting_for_code)

# Составление заявки
def register_ticket_handlers(dp):
    dp.message.register(start_ticket_build, F.text == "Начать составление заявки")
    dp.message.register(start_ticket_creation, F.text == "Создать заявку")
    dp.message.register(process_title, TicketCreation.waiting_for_title)
    dp.message.register(process_description, TicketCreation.waiting_for_description)
    dp.message.register(cancel_creation, Command("cancel"))
    dp.message.register(cancel_creation, F.text.lower() == "отмена")
    # dp.message.register(go_back, Command("back"))
    # dp.message.register(handle_photo, F.photo)
